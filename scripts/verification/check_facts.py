#!/usr/bin/env python3
"""
Fact Change Detector

Verifies facts in the registry against their source URLs/documents.
Detects changes, staleness, and approaching deadlines.
"""

import argparse
import json
import logging
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse

import yaml
from bs4 import BeautifulSoup

# Graceful pdfplumber import
try:
    import pdfplumber
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
    logging.warning("pdfplumber not installed - PDF text extraction disabled")

# Import the rate-limited HTTP client
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.http_client import RateLimitedClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FactChecker:
    """Verifies facts in the registry against their sources."""

    # Status constants
    STATUS_VERIFIED = "VERIFIED"
    STATUS_CHANGED = "CHANGED"
    STATUS_NOT_FOUND = "NOT_FOUND_IN_SOURCE"
    STATUS_STALE = "STALE"
    STATUS_APPROACHING_DEADLINE = "APPROACHING_DEADLINE"
    STATUS_NEEDS_UPDATE = "NEEDS_UPDATE"
    STATUS_UNVERIFIABLE_AUTO = "UNVERIFIABLE_AUTO"
    STATUS_UNVERIFIABLE_PDF = "UNVERIFIABLE_PDF"

    def __init__(self, config: Dict, repo_root: Path, registry_path: Path):
        """
        Initialize the fact checker.

        Args:
            config: Configuration dictionary
            repo_root: Root directory of the repository
            registry_path: Path to the fact registry YAML file
        """
        self.config = config
        self.repo_root = repo_root
        self.registry_path = registry_path

        # Load fact registry
        with open(registry_path, 'r', encoding='utf-8') as f:
            self.registry = yaml.safe_load(f)

        # Initialize HTTP client
        self.http_client = RateLimitedClient(config)

        facts = self.registry if isinstance(self.registry, list) else self.registry.get('facts', [])
        logger.info(f"Loaded {len(facts)} facts from registry")

    def run(self) -> Dict:
        """
        Run fact verification for all facts in the registry.

        Returns:
            Result dictionary with verification results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_facts": 0,
            "verified": 0,
            "stale": 0,
            "changed": 0,
            "not_found_in_source": 0,
            "unverifiable": 0,
            "approaching_deadlines": 0,
            "needs_update": 0,
            "details": []
        }

        facts = self.registry if isinstance(self.registry, list) else self.registry.get('facts', [])
        results["total_facts"] = len(facts)

        for fact in facts:
            fact_id = fact.get('id', 'unknown')
            category = fact.get('category', 'unknown')

            logger.info(f"Checking fact: {fact_id} ({category})")

            detail = self._verify_fact(fact)
            results["details"].append(detail)

            # Update counters
            status = detail["status"]
            if status == self.STATUS_VERIFIED:
                results["verified"] += 1
            elif status == self.STATUS_CHANGED:
                results["changed"] += 1
            elif status == self.STATUS_NOT_FOUND:
                results["not_found_in_source"] += 1
            elif status == self.STATUS_STALE:
                results["stale"] += 1
            elif status == self.STATUS_APPROACHING_DEADLINE:
                results["approaching_deadlines"] += 1
            elif status == self.STATUS_NEEDS_UPDATE:
                results["needs_update"] += 1
            elif status in [self.STATUS_UNVERIFIABLE_AUTO, self.STATUS_UNVERIFIABLE_PDF]:
                results["unverifiable"] += 1

        return results

    def _verify_fact(self, fact: Dict) -> Dict:
        """
        Verify a single fact against its source.

        Args:
            fact: Fact dictionary from registry

        Returns:
            Detail dictionary with verification result
        """
        fact_id = fact.get('id', 'unknown')
        category = fact.get('category', 'unknown')
        value = fact.get('value', '')
        source_url = fact.get('source_url', '')
        verification_method = fact.get('verification_method', 'automated')
        effective_date = fact.get('effective_date')
        file_path = fact.get('file', '')
        line_number = fact.get('line', 0)

        detail = {
            "id": fact_id,
            "category": category,
            "value_in_repo": value,
            "value_in_source": None,
            "source_url": source_url,
            "file": file_path,
            "line": line_number,
            "note": "",
            "days_until": None
        }

        # Check for staleness first (applies to all facts)
        staleness_status = self._check_staleness(fact, detail)
        if staleness_status:
            detail["status"] = staleness_status
            return detail

        # Then perform source verification based on method
        if verification_method == 'manual':
            detail["status"] = self.STATUS_UNVERIFIABLE_AUTO
            detail["note"] = "Manual verification required"
            logger.info(f"  {fact_id}: Manual verification required")

        elif verification_method == 'pdf_text_check':
            self._verify_pdf_fact(fact, detail)

        elif verification_method == 'automated':
            self._verify_html_fact(fact, detail)

        else:
            detail["status"] = self.STATUS_UNVERIFIABLE_AUTO
            detail["note"] = f"Unknown verification method: {verification_method}"
            logger.warning(f"  {fact_id}: Unknown verification method")

        return detail

    def _check_staleness(self, fact: Dict, detail: Dict) -> Optional[str]:
        """
        Check if fact is stale or has approaching/passed deadlines.

        Args:
            fact: Fact dictionary
            detail: Detail dictionary to update

        Returns:
            Status string if stale/deadline issue, None otherwise
        """
        effective_date = fact.get('effective_date')
        value = fact.get('value', '')

        today = datetime.now().date()

        # Check effective_date staleness (>12 months old)
        if effective_date:
            try:
                eff_date = datetime.strptime(effective_date, '%Y-%m-%d').date()
                age_days = (today - eff_date).days

                if age_days > 365:
                    detail["note"] = f"Effective date is {age_days} days old (>12 months)"
                    logger.warning(f"  {fact['id']}: STALE ({age_days} days old)")
                    return self.STATUS_STALE
            except ValueError:
                logger.warning(f"  {fact['id']}: Invalid effective_date format: {effective_date}")

        # Check for date values in the fact
        date_info = self._extract_date_from_value(value)
        if date_info:
            date_val, days_diff = date_info

            # Future date within 30 days
            if 0 < days_diff <= 30:
                detail["days_until"] = days_diff
                detail["note"] = f"Deadline approaching in {days_diff} days"
                logger.warning(f"  {fact['id']}: APPROACHING_DEADLINE ({days_diff} days)")
                return self.STATUS_APPROACHING_DEADLINE

            # Past date
            elif days_diff < 0:
                detail["days_until"] = days_diff
                detail["note"] = f"Date has passed {abs(days_diff)} days ago"
                logger.warning(f"  {fact['id']}: NEEDS_UPDATE (date passed)")
                return self.STATUS_NEEDS_UPDATE

        return None

    def _extract_date_from_value(self, value: str) -> Optional[Tuple[datetime, int]]:
        """
        Extract date from fact value and calculate days until/since.

        Args:
            value: Fact value string

        Returns:
            Tuple of (datetime, days_difference) or None
        """
        today = datetime.now().date()

        # Pattern: YYYY-MM-DD
        iso_match = re.search(r'\b(\d{4})-(\d{2})-(\d{2})\b', value)
        if iso_match:
            try:
                date_val = datetime.strptime(iso_match.group(0), '%Y-%m-%d').date()
                days_diff = (date_val - today).days
                return (datetime.combine(date_val, datetime.min.time()), days_diff)
            except ValueError:
                pass

        # Pattern: "May 2026", "January 2025"
        month_year_match = re.search(r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b', value, re.IGNORECASE)
        if month_year_match:
            try:
                date_str = month_year_match.group(0)
                date_val = datetime.strptime(date_str, '%B %Y').date()
                days_diff = (date_val - today).days
                return (datetime.combine(date_val, datetime.min.time()), days_diff)
            except ValueError:
                pass

        # Pattern: "Q1 2026", "Q2 2025"
        quarter_match = re.search(r'\bQ([1-4])\s+(\d{4})\b', value)
        if quarter_match:
            quarter = int(quarter_match.group(1))
            year = int(quarter_match.group(2))
            month = (quarter - 1) * 3 + 1  # Q1->Jan, Q2->Apr, Q3->Jul, Q4->Oct
            try:
                date_val = datetime(year, month, 1).date()
                days_diff = (date_val - today).days
                return (datetime.combine(date_val, datetime.min.time()), days_diff)
            except ValueError:
                pass

        return None

    def _verify_html_fact(self, fact: Dict, detail: Dict) -> None:
        """
        Verify fact against HTML source page.

        Args:
            fact: Fact dictionary
            detail: Detail dictionary to update
        """
        fact_id = fact.get('id')
        value = fact.get('value', '')
        source_url = fact.get('source_url', '')

        try:
            # Fetch the HTML page using session with rate limiting
            self.http_client._wait_for_rate_limit(self.http_client._get_domain(source_url))
            response = self.http_client.session.get(source_url, timeout=self.http_client.timeout)

            if response.status_code != 200:
                detail["status"] = self.STATUS_UNVERIFIABLE_AUTO
                detail["note"] = f"HTTP {response.status_code}"
                logger.error(f"  {fact_id}: Failed to fetch source (HTTP {response.status_code})")
                return

            # Parse HTML and extract text
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            text = soup.get_text(separator=' ', strip=True)

            # Search for value in text
            if self._value_found_in_text(value, text):
                detail["status"] = self.STATUS_VERIFIED
                detail["value_in_source"] = value
                detail["note"] = "Value found in source"
                logger.info(f"  {fact_id}: VERIFIED")
            else:
                # Try to find similar values (potential changes)
                similar_value = self._find_similar_value(value, text)
                if similar_value:
                    detail["status"] = self.STATUS_CHANGED
                    detail["value_in_source"] = similar_value
                    detail["note"] = f"Found different value in context: {similar_value}"
                    logger.warning(f"  {fact_id}: CHANGED (found: {similar_value})")
                else:
                    detail["status"] = self.STATUS_NOT_FOUND
                    detail["note"] = "Value not found in source"
                    logger.warning(f"  {fact_id}: NOT_FOUND_IN_SOURCE")

        except Exception as e:
            detail["status"] = self.STATUS_UNVERIFIABLE_AUTO
            detail["note"] = f"Error fetching source: {str(e)}"
            logger.error(f"  {fact_id}: Error - {str(e)}")

    def _verify_pdf_fact(self, fact: Dict, detail: Dict) -> None:
        """
        Verify fact against PDF source document.

        Args:
            fact: Fact dictionary
            detail: Detail dictionary to update
        """
        fact_id = fact.get('id')
        value = fact.get('value', '')
        source_url = fact.get('source_url', '')
        pdf_text_extractable = fact.get('pdf_text_extractable', False)

        if not PDF_SUPPORT:
            detail["status"] = self.STATUS_UNVERIFIABLE_PDF
            detail["note"] = "pdfplumber not installed"
            logger.warning(f"  {fact_id}: PDF support not available")
            return

        if not pdf_text_extractable:
            detail["status"] = self.STATUS_UNVERIFIABLE_AUTO
            detail["note"] = "PDF text extraction not enabled for this fact"
            logger.info(f"  {fact_id}: PDF text extraction not enabled")
            return

        try:
            # Fetch the PDF using session with rate limiting
            self.http_client._wait_for_rate_limit(self.http_client._get_domain(source_url))
            response = self.http_client.session.get(source_url, timeout=self.http_client.timeout)

            if response.status_code != 200:
                detail["status"] = self.STATUS_UNVERIFIABLE_PDF
                detail["note"] = f"HTTP {response.status_code}"
                logger.error(f"  {fact_id}: Failed to fetch PDF (HTTP {response.status_code})")
                return

            # Save PDF temporarily
            import tempfile
            temp_pdf_path = Path(tempfile.gettempdir()) / f"fact_check_{fact_id}.pdf"
            temp_pdf_path.write_bytes(response.content)

            try:
                # Extract text from PDF
                with pdfplumber.open(temp_pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"

                if not text.strip():
                    detail["status"] = self.STATUS_UNVERIFIABLE_PDF
                    detail["note"] = "PDF text extraction failed (empty result)"
                    logger.warning(f"  {fact_id}: PDF text extraction returned empty")
                    return

                # Search for value in text
                if self._value_found_in_text(value, text):
                    detail["status"] = self.STATUS_VERIFIED
                    detail["value_in_source"] = value
                    detail["note"] = "Value found in PDF"
                    logger.info(f"  {fact_id}: VERIFIED")
                else:
                    similar_value = self._find_similar_value(value, text)
                    if similar_value:
                        detail["status"] = self.STATUS_CHANGED
                        detail["value_in_source"] = similar_value
                        detail["note"] = f"Found different value in PDF: {similar_value}"
                        logger.warning(f"  {fact_id}: CHANGED (found: {similar_value})")
                    else:
                        detail["status"] = self.STATUS_NOT_FOUND
                        detail["note"] = "Value not found in PDF"
                        logger.warning(f"  {fact_id}: NOT_FOUND_IN_SOURCE")

            finally:
                # Clean up temp file
                if temp_pdf_path.exists():
                    temp_pdf_path.unlink()

        except Exception as e:
            detail["status"] = self.STATUS_UNVERIFIABLE_PDF
            detail["note"] = f"PDF extraction error: {str(e)}"
            logger.error(f"  {fact_id}: PDF extraction error - {str(e)}")

    def _value_found_in_text(self, value: str, text: str) -> bool:
        """
        Check if value exists in text (with fuzzy matching for numbers).

        Args:
            value: Value to search for
            text: Text to search in

        Returns:
            True if value found
        """
        # Try exact match first (case-insensitive)
        if value.lower() in text.lower():
            return True

        # Try fuzzy numeric match
        if self._is_numeric(value):
            return self._fuzzy_match_numeric(value, text)

        # Try removing formatting characters
        value_clean = re.sub(r'[,.\s]', '', value)
        text_clean = re.sub(r'[,.\s]', '', text)
        if value_clean.lower() in text_clean.lower():
            return True

        return False

    def _is_numeric(self, value: str) -> bool:
        """Check if value is numeric (possibly with formatting)."""
        clean = re.sub(r'[,.\s]', '', value)
        return bool(re.match(r'^-?\d+$', clean))

    def _fuzzy_match_numeric(self, value_str: str, text: str, tolerance: float = 0.10) -> bool:
        """
        Check if a numeric value appears in text, with +/-10% tolerance.

        Args:
            value_str: Numeric value as string
            text: Text to search in
            tolerance: Tolerance as fraction (0.10 = 10%)

        Returns:
            True if matching number found
        """
        # Parse the value
        try:
            value_clean = re.sub(r'[,.\s]', '', value_str)
            value_num = float(value_clean)
        except (ValueError, TypeError):
            return False

        # Find all numbers in text
        number_patterns = [
            r'\b(\d{1,3}(?:[,.\s]\d{3})*(?:[,.\s]\d+)?)\b',  # With thousand separators
            r'\b(\d+)\b'  # Simple integers
        ]

        for pattern in number_patterns:
            for match in re.finditer(pattern, text):
                try:
                    num_str = match.group(1)
                    num_clean = re.sub(r'[,.\s]', '', num_str)
                    num_val = float(num_clean)

                    # Check if within tolerance
                    diff = abs(num_val - value_num)
                    max_diff = value_num * tolerance

                    if diff <= max_diff:
                        return True

                except (ValueError, TypeError):
                    continue

        # Also check for formatted variations with currency symbols
        currency_pattern = r'(?:EUR|USD|€|\$)\s*(\d{1,3}(?:[,.\s]\d{3})*)'
        for match in re.finditer(currency_pattern, text):
            try:
                num_str = match.group(1)
                num_clean = re.sub(r'[,.\s]', '', num_str)
                num_val = float(num_clean)

                diff = abs(num_val - value_num)
                max_diff = value_num * tolerance

                if diff <= max_diff:
                    return True

            except (ValueError, TypeError):
                continue

        return False

    def _find_similar_value(self, value: str, text: str) -> Optional[str]:
        """
        Find similar values in text (for detecting changes).

        Args:
            value: Original value
            text: Text to search in

        Returns:
            Similar value if found, None otherwise
        """
        # For numeric values, look for nearby numbers
        if self._is_numeric(value):
            try:
                value_clean = re.sub(r'[,.\s]', '', value)
                value_num = float(value_clean)

                # Find numbers in similar magnitude (within 50%)
                for match in re.finditer(r'\b(\d{1,3}(?:[,.\s]\d{3})*)\b', text):
                    try:
                        num_str = match.group(1)
                        num_clean = re.sub(r'[,.\s]', '', num_str)
                        num_val = float(num_clean)

                        # Similar magnitude?
                        ratio = num_val / value_num if value_num != 0 else 0
                        if 0.5 <= ratio <= 2.0 and abs(num_val - value_num) > value_num * 0.10:
                            return num_str

                    except (ValueError, TypeError):
                        continue

            except (ValueError, TypeError):
                pass

        # For text values, look for partial matches
        # (This is a simple implementation - could be enhanced with fuzzy string matching)
        value_words = set(value.lower().split())
        if len(value_words) > 2:
            # Look for phrases with similar words
            sentences = re.split(r'[.!?]', text)
            for sentence in sentences:
                sentence_words = set(sentence.lower().split())
                overlap = len(value_words & sentence_words)
                if overlap >= len(value_words) * 0.6:
                    return sentence.strip()[:100]  # Return first 100 chars

        return None


def main():
    """Main entry point for fact checker CLI."""
    parser = argparse.ArgumentParser(
        description='Verify facts in registry against their sources'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('scripts/verification/config.yaml'),
        help='Path to configuration file'
    )
    parser.add_argument(
        '--registry',
        type=Path,
        default=Path('.omc/facts/fact_registry.yaml'),
        help='Path to fact registry file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('.omc/facts/facts_result.json'),
        help='Path to output results file'
    )

    args = parser.parse_args()

    # Load configuration
    if not args.config.exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(2)

    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Check registry exists
    if not args.registry.exists():
        logger.error(f"Fact registry not found: {args.registry}")
        sys.exit(2)

    # Determine repo root
    repo_root = Path.cwd()
    if (repo_root / '.git').exists():
        pass  # Already at repo root
    elif (repo_root.parent / '.git').exists():
        repo_root = repo_root.parent

    # Run fact checker
    checker = FactChecker(config, repo_root, args.registry)
    results = checker.run()

    # Write results
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    logger.info(f"Results written to {args.output}")

    # Print summary
    print("\n" + "="*60)
    print("FACT VERIFICATION SUMMARY")
    print("="*60)
    print(f"Total facts:              {results['total_facts']}")
    print(f"Verified:                 {results['verified']}")
    print(f"Changed:                  {results['changed']}")
    print(f"Not found in source:      {results['not_found_in_source']}")
    print(f"Stale (>12 months):       {results['stale']}")
    print(f"Approaching deadlines:    {results['approaching_deadlines']}")
    print(f"Needs update:             {results['needs_update']}")
    print(f"Unverifiable:             {results['unverifiable']}")
    print("="*60)

    # Determine exit code
    if results['changed'] > 0 or results['not_found_in_source'] > 0:
        logger.error("FAILURE: Facts have changed or not found in source")
        sys.exit(2)
    elif results['stale'] > 0 or results['approaching_deadlines'] > 0 or results['needs_update'] > 0:
        logger.warning("WARNING: Stale facts or approaching deadlines detected")
        sys.exit(1)
    else:
        logger.info("SUCCESS: All facts verified or require manual check")
        sys.exit(0)


if __name__ == "__main__":
    main()
