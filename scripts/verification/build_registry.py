#!/usr/bin/env python3
"""
Fact Registry Builder - Scans markdown files for verifiable facts.

Usage:
    python build_registry.py --scan-all --output fact_registry.yaml
    python build_registry.py --scan-all --output fact_registry.yaml --merge
"""

import argparse
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any, Set
from collections import defaultdict

# Import the markdown parser utility
import sys
sys.path.insert(0, str(Path(__file__).parent))
from utils.markdown_parser import get_all_markdown_files


# Regex patterns for fact extraction
PATTERNS = {
    'urls': re.compile(r'https?://[^\s\)>\]]+'),
    'pricing': re.compile(r'(?:EUR\s*[\d,.]+|[\d,.]+\s*EUR)', re.IGNORECASE),
    'latency': re.compile(r'[\d,.]+\s*(?:ns|µs|us|ms|microsecond|nanosecond|millisecond)s?', re.IGNORECASE),
    'session_limits': re.compile(r'[\d,.]+\s*(?:msg/sec|req/sec|TPS|sessions|partitions|messages|orders)', re.IGNORECASE),
    'dates': re.compile(r'''(?:
        \d{4}[-/]\d{2}[-/]\d{2} |
        Q[1-4]\s*\d{4} |
        (?:January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4} |
        \d{1,2}\s*(?:January|February|March|April|May|June|July|August|September|October|November|December)\s*\d{4}
    )''', re.VERBOSE | re.IGNORECASE),
    'contacts': re.compile(r'[\w.+-]+@[\w-]+\.[\w.-]+'),
    'regulatory': re.compile(r'(?:MiFID|MiFIR|RTS|MAR|EMIR|HFT Act|BaFin)\s*[\dIVX/.\-]+', re.IGNORECASE),
}


def get_context(line_content: str, match_start: int, match_end: int, context_chars: int = 50) -> str:
    """Extract surrounding context for a match."""
    start_idx = max(0, match_start - context_chars)
    end_idx = min(len(line_content), match_end + context_chars)
    context = line_content[start_idx:end_idx].strip()
    return context


def extract_unit(value: str, category: str) -> tuple:
    """Extract numeric value and unit from a matched string."""
    if category == 'pricing':
        # Extract number and set unit to EUR
        num_match = re.search(r'[\d,.]+', value)
        if num_match:
            return num_match.group(0), 'EUR'
        return value, 'EUR'

    elif category == 'latency':
        # Extract number and time unit
        match = re.match(r'([\d,.]+)\s*(\w+)', value, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).lower()
        return value, None

    elif category == 'session_limits':
        # Extract number and capacity unit
        match = re.match(r'([\d,.]+)\s*(.+)', value, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).strip()
        return value, None

    # No unit extraction needed
    return value, None


def scan_file(file_path: Path, repo_root: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Scan a single markdown file for fact candidates."""
    candidates = defaultdict(list)

    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines()
        relative_path = file_path.relative_to(repo_root).as_posix()

        for line_num, line_content in enumerate(lines, start=1):
            for category, pattern in PATTERNS.items():
                for match in pattern.finditer(line_content):
                    value = match.group(0).strip()
                    context = get_context(line_content, match.start(), match.end())

                    # Extract value and unit if applicable
                    extracted_value, unit = extract_unit(value, category)

                    # Generate ID
                    file_stem = file_path.stem
                    fact_id = f"{category}-{file_stem}-{line_num}"

                    candidate = {
                        'id': fact_id,
                        'category': category,
                        'value': extracted_value,
                        'unit': unit,
                        'file': relative_path,
                        'line': line_num,
                        'context': context,
                        'source_url': '',
                        'source_document': '',
                        'effective_date': None,
                        'last_verified': None,
                        'verification_method': 'unreviewed',
                        'pdf_text_extractable': None,
                        'notes': ''
                    }

                    candidates[category].append(candidate)

    except Exception as e:
        print(f"Error scanning {file_path}: {e}")

    return candidates


def deduplicate_urls(candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Deduplicate URLs across all files, tracking all locations."""
    url_map = {}

    for candidate in candidates:
        url = candidate['value']

        if url in url_map:
            # Add location to existing entry
            if 'locations' not in url_map[url]:
                url_map[url]['locations'] = [
                    {'file': url_map[url]['file'], 'line': url_map[url]['line']}
                ]
            url_map[url]['locations'].append({
                'file': candidate['file'],
                'line': candidate['line']
            })
        else:
            # First occurrence
            url_map[url] = candidate

    return list(url_map.values())


def merge_registries(existing_path: Path, new_candidates: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
    """Merge new candidates with existing registry, preserving reviewed entries."""
    if not existing_path.exists():
        return new_candidates

    try:
        with open(existing_path, 'r', encoding='utf-8') as f:
            existing_data = yaml.safe_load(f) or []

        # Build map of existing entries by ID
        existing_map = {entry['id']: entry for entry in existing_data}

        merged = defaultdict(list)

        # Process new candidates
        for category, candidates in new_candidates.items():
            for candidate in candidates:
                cid = candidate['id']

                if cid in existing_map:
                    existing = existing_map[cid]

                    # Keep reviewed entries as-is
                    if existing.get('verification_method') != 'unreviewed':
                        merged[category].append(existing)
                    else:
                        # Update unreviewed entries if value changed
                        if existing.get('value') != candidate['value']:
                            candidate['notes'] = f"Updated from: {existing.get('value')}"
                        merged[category].append(candidate)

                    # Mark as processed
                    del existing_map[cid]
                else:
                    # New candidate
                    merged[category].append(candidate)

        # Add remaining existing entries that weren't matched
        for entry in existing_map.values():
            merged[entry['category']].append(entry)

        return merged

    except Exception as e:
        print(f"Error merging with existing registry: {e}")
        return new_candidates


def scan_all_files(repo_root: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Scan all markdown files in the repository."""
    all_candidates = defaultdict(list)
    stats = defaultdict(int)

    markdown_files = get_all_markdown_files(repo_root)
    print(f"Scanning {len(markdown_files)} markdown files...")

    for file_path in markdown_files:
        candidates = scan_file(file_path, repo_root)

        for category, facts in candidates.items():
            all_candidates[category].extend(facts)
            stats[category] += len(facts)

    # Deduplicate URLs
    if 'urls' in all_candidates:
        all_candidates['urls'] = deduplicate_urls(all_candidates['urls'])
        stats['urls'] = len(all_candidates['urls'])

    return all_candidates, stats


def write_registry(output_path: Path, candidates: Dict[str, List[Dict[str, Any]]]):
    """Write the fact registry to YAML file."""
    # Flatten all candidates into single list, sorted by category then ID
    all_entries = []
    for category in sorted(candidates.keys()):
        all_entries.extend(sorted(candidates[category], key=lambda x: x['id']))

    # Add header comment
    header = """# Fact Registry for hft-exchange-knowledge
#
# Schema: Each entry represents a verifiable fact in the repository.
# Run `python build_registry.py --scan-all --output fact_registry.yaml` to auto-populate.
# Review each entry and set verification_method to: manual, automated, or pdf_text_check.
# Entries with verification_method: unreviewed need human review.
#
# Categories: urls, pricing, latency, session_limits, dates, contacts, regulatory
#

"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(header)
        yaml.dump(all_entries, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"\nWrote {len(all_entries)} entries to {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Build fact registry from markdown files')
    parser.add_argument('--scan-all', action='store_true', help='Scan all markdown files')
    parser.add_argument('--output', type=str, default='fact_registry.yaml', help='Output YAML file')
    parser.add_argument('--merge', action='store_true', help='Merge with existing registry')

    args = parser.parse_args()

    if not args.scan_all:
        parser.error('--scan-all is required')

    # Determine repository root (2 levels up from script location)
    repo_root = Path(__file__).parent.parent.parent
    output_path = Path(__file__).parent / args.output

    print(f"Repository root: {repo_root}")
    print(f"Output file: {output_path}")

    # Scan all files
    candidates, stats = scan_all_files(repo_root)

    # Merge if requested
    if args.merge:
        print("\nMerging with existing registry...")
        candidates = merge_registries(output_path, candidates)

    # Write registry
    write_registry(output_path, candidates)

    # Print summary
    print("\n=== Summary ===")
    print(f"Scanned files: {len(get_all_markdown_files(repo_root))}")
    total_facts = sum(stats.values())
    print(f"Found {total_facts} candidates:")
    for category in sorted(stats.keys()):
        print(f"  - {category}: {stats[category]}")


if __name__ == '__main__':
    main()
