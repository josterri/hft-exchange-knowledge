#!/usr/bin/env python3
"""
Cross-Reference Validator for Markdown Documentation

Validates all internal markdown links, anchor references, and back-links in the repository.
Detects orphaned files and provides actionable suggestions for fixing broken links.
"""

import argparse
import json
import logging
import re
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.markdown_parser import (
    extract_internal_links,
    extract_headings,
    get_all_markdown_files
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CrossRefValidator:
    """Validates cross-references, anchors, and links in markdown documentation."""

    # Files to exclude from orphan detection
    EXCLUDED_FROM_ORPHAN_CHECK = {
        'README.md',
        'CONTRIBUTING.md',
        'LICENSE.md',
        'LICENSE',
        'SOURCES.md',
        '_config.yml',
        'AGENTS.md',
    }

    # Directories to exclude
    EXCLUDED_DIRS = {'.omc', '.github', '.git', 'node_modules', 'scripts'}

    def __init__(self, config: dict, repo_root: Path):
        """
        Initialize the cross-reference validator.

        Args:
            config: Configuration dictionary with validation settings
            repo_root: Path to repository root directory
        """
        self.config = config
        self.repo_root = Path(repo_root).resolve()
        self.file_index: Set[Path] = set()
        self.anchor_index: Dict[Path, Set[str]] = {}
        self.toc_file = self.repo_root / "TABLE_OF_CONTENTS.md"
        self.toc_referenced_files: Set[Path] = set()

    def to_github_anchor(self, heading_text: str) -> str:
        """
        Convert heading text to GitHub-style anchor.

        GitHub's anchor generation rules:
        - Remove markdown formatting (**, *, `, etc.)
        - Lowercase
        - Replace spaces with hyphens
        - Remove everything except alphanumerics, hyphens, underscores

        Args:
            heading_text: The heading text to convert

        Returns:
            GitHub-style anchor string
        """
        # Remove markdown formatting
        text = re.sub(r'[*`\[\]()]', '', heading_text)
        # Lowercase and strip
        text = text.lower().strip()
        # Replace spaces with hyphens
        text = re.sub(r'\s+', '-', text)
        # Remove everything except alphanumerics, hyphens, underscores
        text = re.sub(r'[^a-z0-9\-_]', '', text)
        return text

    def build_file_index(self) -> None:
        """Build index of all markdown files in the repository."""
        logger.info("Building file index...")
        self.file_index = set(get_all_markdown_files(self.repo_root))
        logger.info(f"Found {len(self.file_index)} markdown files")

    def build_anchor_index(self) -> None:
        """
        Build index of all anchors (headings) in each markdown file.

        Handles duplicate headings by appending -1, -2, etc. (GitHub behavior)
        """
        logger.info("Building anchor index...")

        for file_path in self.file_index:
            try:
                headings = extract_headings(file_path)
                anchors = set()
                anchor_counts: Dict[str, int] = defaultdict(int)

                for heading_text in headings:
                    base_anchor = self.to_github_anchor(heading_text)

                    # Handle duplicate anchors (GitHub appends -1, -2, etc.)
                    if base_anchor in anchor_counts:
                        count = anchor_counts[base_anchor]
                        actual_anchor = f"{base_anchor}-{count}"
                        anchor_counts[base_anchor] += 1
                    else:
                        actual_anchor = base_anchor
                        anchor_counts[base_anchor] = 1

                    anchors.add(actual_anchor)
                    # Also add the base anchor for matching
                    anchors.add(base_anchor)

                self.anchor_index[file_path] = anchors

            except Exception as e:
                logger.warning(f"Failed to extract headings from {file_path}: {e}")
                self.anchor_index[file_path] = set()

        logger.info(f"Built anchor index for {len(self.anchor_index)} files")

    def resolve_link_path(self, source_file: Path, link_target: str) -> Tuple[Optional[Path], Optional[str]]:
        """
        Resolve a relative link from source file to target file and anchor.

        Args:
            source_file: The markdown file containing the link
            link_target: The link target (may include anchor, e.g., 'file.md#section')

        Returns:
            Tuple of (resolved_file_path, anchor) or (None, None) if invalid
        """
        # Split target into file path and anchor
        if '#' in link_target:
            file_part, anchor_part = link_target.split('#', 1)
            anchor = anchor_part if anchor_part else None
        else:
            file_part = link_target
            anchor = None

        # Handle empty file part (same-file anchor link)
        if not file_part:
            return source_file, anchor

        # Resolve relative path from source file's directory
        source_dir = source_file.parent
        target_path = (source_dir / file_part).resolve()

        # Ensure the target is within repo and exists in our index
        try:
            target_path.relative_to(self.repo_root)
            if target_path in self.file_index:
                return target_path, anchor
        except ValueError:
            pass

        return None, anchor

    def find_similar_anchors(self, target_anchor: str, available_anchors: Set[str], max_results: int = 3) -> List[str]:
        """
        Find similar anchors using simple string similarity.

        Args:
            target_anchor: The anchor we're looking for
            available_anchors: Set of available anchors to search
            max_results: Maximum number of similar anchors to return

        Returns:
            List of similar anchor names
        """
        # Simple similarity: count matching substrings
        similarities = []
        for anchor in available_anchors:
            # Count common words/parts
            target_parts = set(target_anchor.split('-'))
            anchor_parts = set(anchor.split('-'))
            common = len(target_parts & anchor_parts)
            if common > 0:
                similarities.append((common, anchor))

        # Sort by similarity and return top results
        similarities.sort(reverse=True, key=lambda x: x[0])
        return [anchor for _, anchor in similarities[:max_results]]

    def validate_internal_links(self) -> Tuple[List[dict], int, int]:
        """
        Validate all internal links in markdown files.

        Returns:
            Tuple of (failures list, total_links count, valid_links count)
        """
        logger.info("Validating internal links...")

        failures = []
        total_links = 0
        valid_links = 0

        for source_file in self.file_index:
            try:
                links = extract_internal_links(source_file)

                for link_info in links:
                    total_links += 1
                    # Reconstruct full target (path#anchor) for resolve_link_path
                    target = link_info.target_path
                    if link_info.anchor:
                        target = f"{target}#{link_info.anchor}"
                    line = link_info.line_number

                    # Resolve the link
                    resolved_path, anchor = self.resolve_link_path(source_file, target)

                    # Check if file exists
                    if resolved_path is None:
                        failures.append({
                            'source_file': str(source_file.relative_to(self.repo_root)),
                            'line': line,
                            'target': target,
                            'resolved_path': 'N/A',
                            'error': 'File not found',
                            'suggested_action': f"File path could not be resolved. Check if the file was renamed or moved."
                        })
                        continue

                    # Check if anchor exists (if specified)
                    if anchor:
                        anchor_normalized = self.to_github_anchor(anchor)
                        available_anchors = self.anchor_index.get(resolved_path, set())

                        # Case-insensitive anchor matching
                        if not any(a.lower() == anchor_normalized.lower() for a in available_anchors):
                            similar = self.find_similar_anchors(anchor_normalized, available_anchors)
                            similar_str = f" Similar anchors: {', '.join(similar)}" if similar else ""

                            failures.append({
                                'source_file': str(source_file.relative_to(self.repo_root)),
                                'line': line,
                                'target': target,
                                'resolved_path': str(resolved_path.relative_to(self.repo_root)),
                                'error': f"Anchor #{anchor} not found in target file",
                                'suggested_action': f"Anchor '#{anchor}' does not exist in {resolved_path.name}.{similar_str}"
                            })
                            continue

                    # Link is valid
                    valid_links += 1

            except Exception as e:
                logger.warning(f"Failed to validate links in {source_file}: {e}")

        logger.info(f"Validated {total_links} internal links: {valid_links} valid, {len(failures)} broken")
        return failures, total_links, valid_links

    def validate_toc(self) -> Tuple[int, int, List[dict]]:
        """
        Validate all links in TABLE_OF_CONTENTS.md.

        Returns:
            Tuple of (total_toc_links, valid_toc_links, toc_failures)
        """
        logger.info("Validating TABLE_OF_CONTENTS.md...")

        if not self.toc_file.exists():
            logger.warning(f"TABLE_OF_CONTENTS.md not found at {self.toc_file}")
            return 0, 0, []

        toc_failures = []
        total_toc_links = 0
        valid_toc_links = 0

        try:
            links = extract_internal_links(self.toc_file)

            for link_info in links:
                total_toc_links += 1
                # Reconstruct full target (path#anchor) for resolve_link_path
                target = link_info.target_path
                if link_info.anchor:
                    target = f"{target}#{link_info.anchor}"
                line = link_info.line_number

                # Resolve the link
                resolved_path, anchor = self.resolve_link_path(self.toc_file, target)

                if resolved_path is None:
                    toc_failures.append({
                        'source_file': 'TABLE_OF_CONTENTS.md',
                        'line': line,
                        'target': target,
                        'resolved_path': 'N/A',
                        'error': 'File not found',
                        'suggested_action': f"TOC references non-existent file: {target}"
                    })
                else:
                    valid_toc_links += 1
                    self.toc_referenced_files.add(resolved_path)

        except Exception as e:
            logger.error(f"Failed to validate TOC: {e}")

        logger.info(f"TOC validation: {valid_toc_links}/{total_toc_links} valid links")
        return total_toc_links, valid_toc_links, toc_failures

    def validate_back_links(self) -> Tuple[int, int, List[str]]:
        """
        Validate that each chapter has a "Back to Table of Contents" link.

        Returns:
            Tuple of (chapters_with_back_link, chapters_without_back_link, missing_in_files)
        """
        logger.info("Validating back-links to TABLE_OF_CONTENTS.md...")

        chapters_with_back = 0
        missing_in = []

        # Pattern to match "Back to Table of Contents" links
        back_link_pattern = re.compile(
            r'\[.*?back.*?table.*?of.*?contents.*?\].*?TABLE_OF_CONTENTS\.md',
            re.IGNORECASE
        )

        for file_path in self.file_index:
            # Skip TOC itself and meta files
            if file_path.name in self.EXCLUDED_FROM_ORPHAN_CHECK:
                continue

            # Skip files in excluded directories
            if any(excluded in file_path.parts for excluded in self.EXCLUDED_DIRS):
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                if back_link_pattern.search(content):
                    chapters_with_back += 1
                else:
                    missing_in.append(str(file_path.relative_to(self.repo_root)))
            except Exception as e:
                logger.warning(f"Failed to check back-link in {file_path}: {e}")

        chapters_without_back = len(missing_in)
        logger.info(f"Back-links: {chapters_with_back} chapters with back-link, {chapters_without_back} without")

        return chapters_with_back, chapters_without_back, missing_in

    def detect_orphaned_files(self) -> List[str]:
        """
        Detect markdown files that exist but are not referenced from TABLE_OF_CONTENTS.md.

        Returns:
            List of orphaned file paths (relative to repo root)
        """
        logger.info("Detecting orphaned files...")

        orphaned = []

        for file_path in self.file_index:
            # Skip meta files
            if file_path.name in self.EXCLUDED_FROM_ORPHAN_CHECK:
                continue

            # Skip TOC itself
            if file_path == self.toc_file:
                continue

            # Skip files in excluded directories
            if any(excluded in file_path.parts for excluded in self.EXCLUDED_DIRS):
                continue

            # Check if referenced from TOC
            if file_path not in self.toc_referenced_files:
                orphaned.append(str(file_path.relative_to(self.repo_root)))

        logger.info(f"Found {len(orphaned)} orphaned files")
        return orphaned

    def run(self) -> dict:
        """
        Run the complete cross-reference validation.

        Returns:
            Dictionary with validation results
        """
        logger.info("Starting cross-reference validation...")

        # Build indexes
        self.build_file_index()
        self.build_anchor_index()

        # Validate TOC first (to build referenced files set)
        total_toc_links, valid_toc_links, toc_failures = self.validate_toc()

        # Validate all internal links
        link_failures, total_links, valid_links = self.validate_internal_links()

        # Combine all failures
        all_failures = link_failures + toc_failures

        # Validate back-links
        chapters_with_back, chapters_without_back, missing_back_in = self.validate_back_links()

        # Detect orphaned files
        orphaned_files = self.detect_orphaned_files()

        # Build result
        result = {
            'timestamp': datetime.now().isoformat(),
            'total_internal_links': total_links,
            'valid': valid_links,
            'broken': len(link_failures),
            'orphaned_files': orphaned_files,
            'failures': all_failures,
            'toc_coverage': {
                'total_toc_links': total_toc_links,
                'valid': valid_toc_links,
                'broken': len(toc_failures)
            },
            'back_links': {
                'chapters_with_back_link': chapters_with_back,
                'chapters_without_back_link': chapters_without_back,
                'missing_in': missing_back_in
            }
        }

        # Log summary
        logger.info("=" * 60)
        logger.info("CROSS-REFERENCE VALIDATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total internal links: {total_links}")
        logger.info(f"Valid links: {valid_links}")
        logger.info(f"Broken links: {len(link_failures)}")
        logger.info(f"Orphaned files: {len(orphaned_files)}")
        logger.info(f"TOC coverage: {valid_toc_links}/{total_toc_links} valid")
        logger.info(f"Back-links: {chapters_with_back} present, {chapters_without_back} missing")
        logger.info("=" * 60)

        return result


def main():
    """Main entry point for the cross-reference validator."""
    parser = argparse.ArgumentParser(
        description='Validate cross-references and links in markdown documentation'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'verification_config.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path(__file__).parent.parent.parent / 'crossrefs_result.json',
        help='Path to output JSON file'
    )
    parser.add_argument(
        '--repo-root',
        type=Path,
        default=Path(__file__).parent.parent.parent,
        help='Path to repository root'
    )

    args = parser.parse_args()

    # Load configuration
    config = {}
    if args.config.exists():
        try:
            import yaml
            with open(args.config, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {args.config}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")

    # Run validator
    validator = CrossRefValidator(config, args.repo_root)
    result = validator.run()

    # Write results
    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results written to {args.output}")
    except Exception as e:
        logger.error(f"Failed to write results: {e}")
        sys.exit(1)

    # Exit with appropriate code
    if result['broken'] > 0 or len(result['orphaned_files']) > 0:
        logger.error("Validation FAILED: broken links or orphaned files detected")
        sys.exit(2)
    else:
        logger.info("Validation PASSED: all links valid")
        sys.exit(0)


if __name__ == '__main__':
    main()
