"""
Link Checker - Validates all URLs across markdown files in the repository.

This script discovers URLs in markdown files, validates them via HTTP requests,
detects redirects, soft 404s, and PDF content changes, and produces a detailed
report with suggested remediation actions.
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import yaml

from utils.http_client import RateLimitedClient
from utils.markdown_parser import extract_urls, get_all_markdown_files

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LinkChecker:
    """
    Validates URLs found in markdown files against live HTTP endpoints.

    Attributes:
        config: Configuration dict with rate limits, approved domains, soft 404 patterns
        repo_root: Root directory of the repository
        registry_path: Optional path to fact_registry.yaml for PDF verification
        client: RateLimitedClient instance for HTTP requests
        fact_registry: Loaded fact registry data (if available)
    """

    def __init__(
        self,
        config: dict,
        repo_root: Path,
        registry_path: Optional[Path] = None
    ):
        """
        Initialize the link checker.

        Args:
            config: Configuration dictionary containing rate_limits, approved_domains, etc.
            repo_root: Path to repository root
            registry_path: Optional path to fact_registry.yaml
        """
        self.config = config
        self.repo_root = repo_root
        self.registry_path = registry_path

        # Initialize HTTP client with config
        self.client = RateLimitedClient(config)

        # Load fact registry if available
        self.fact_registry = self._load_fact_registry()

    def _load_fact_registry(self) -> Optional[dict]:
        """
        Load the fact registry YAML file.

        Returns:
            Parsed registry dict or None if not available
        """
        if not self.registry_path or not self.registry_path.exists():
            logger.info("No fact registry provided or file not found")
            return None

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = yaml.safe_load(f)
                logger.info(f"Loaded fact registry from {self.registry_path}")
                return registry
        except Exception as e:
            logger.error(f"Failed to load fact registry: {e}")
            return None

    def _discover_urls(self) -> Dict[str, List[dict]]:
        """
        Discover all URLs across markdown files.

        Returns:
            Dict mapping URL to list of location dicts {file, line, link_text}
        """
        logger.info("Discovering URLs in markdown files...")
        url_locations: Dict[str, List[dict]] = {}

        markdown_files = get_all_markdown_files(self.repo_root)
        logger.info(f"Found {len(markdown_files)} markdown files")

        for md_file in markdown_files:
            urls = extract_urls(md_file)
            for url_info in urls:
                url = url_info.url
                location = {
                    'file': str(md_file.relative_to(self.repo_root)),
                    'line': url_info.line_number,
                    'link_text': url_info.link_text
                }

                if url not in url_locations:
                    url_locations[url] = []
                url_locations[url].append(location)

        logger.info(f"Discovered {len(url_locations)} unique URLs")
        return url_locations

    def _get_pdf_registry_info(self, url: str) -> Optional[Tuple[str, int]]:
        """
        Get stored hash and content length for a PDF URL from the registry.

        Args:
            url: PDF URL to lookup

        Returns:
            Tuple of (content_hash, content_length) or None if not found
        """
        if not self.fact_registry:
            return None

        # Search for URL in PDF entries
        pdfs = self.fact_registry.get('pdfs', [])
        for pdf_entry in pdfs:
            if pdf_entry.get('url') == url:
                content_hash = pdf_entry.get('content_hash')
                content_length = pdf_entry.get('content_length')
                if content_hash and content_length:
                    return (content_hash, content_length)

        return None

    def _classify_url(self, url: str) -> Tuple[str, dict]:
        """
        Check a URL and classify its status.

        Args:
            url: URL to check

        Returns:
            Tuple of (status_classification, details_dict)
        """
        # Check if URL appears to be a PDF
        is_pdf = url.lower().endswith('.pdf')
        known_hash = None
        known_length = None

        if is_pdf:
            registry_info = self._get_pdf_registry_info(url)
            if registry_info:
                known_hash, known_length = registry_info

        # Perform HTTP check
        if is_pdf and known_hash:
            pdf_result = self.client.check_pdf(url, known_length, known_hash)
            details = {
                'error_detail': pdf_result.get('error', '') or '',
                'final_url': url,
                'status_code': pdf_result.get('status_code'),
            }
            if pdf_result.get('error'):
                if 'timeout' in pdf_result['error'].lower():
                    return ('TIMEOUT', details)
                elif 'dns' in pdf_result['error'].lower() or 'getaddrinfo' in pdf_result['error'].lower():
                    return ('DOMAIN_ERROR', details)
                else:
                    return ('DOMAIN_ERROR', details)
            if pdf_result.get('status_code') == 404:
                return ('NOT_FOUND', details)
            if pdf_result.get('status_code', 0) >= 500:
                return ('SERVER_ERROR', details)
            if pdf_result.get('changed', False):
                details['old_hash'] = known_hash
                details['new_hash'] = pdf_result.get('new_hash')
                details['old_content_length'] = known_length
                details['new_content_length'] = pdf_result.get('new_content_length')
                return ('MOVED_PDF', details)
            return ('OK', details)

        # Standard URL fetch
        result = self.client.fetch(url)

        details = {
            'error_detail': result.get('error', '') or '',
            'final_url': result.get('final_url', url),
            'status_code': result.get('status_code'),
        }

        # Classify based on fetch result fields
        error = result.get('error')
        status_code = result.get('status_code', 0)
        is_soft_404 = result.get('is_soft_404', False)
        final_url = result.get('final_url', url)

        if error is not None:
            error_lower = error.lower()
            if 'timeout' in error_lower or 'timed out' in error_lower:
                return ('TIMEOUT', details)
            elif 'dns' in error_lower or 'getaddrinfo' in error_lower or 'name or service not known' in error_lower:
                return ('DOMAIN_ERROR', details)
            else:
                return ('DOMAIN_ERROR', details)

        if status_code == 200 and is_soft_404:
            return ('SOFT_404', details)

        if status_code == 200:
            if final_url != url:
                return ('REDIRECT', details)
            return ('OK', details)

        if status_code in (301, 302, 303, 307, 308):
            return ('REDIRECT', details)

        if status_code == 404:
            return ('NOT_FOUND', details)

        if status_code >= 500:
            return ('SERVER_ERROR', details)

        # Fallback for other status codes
        return ('DOMAIN_ERROR', details)

    def _generate_suggested_action(
        self,
        status: str,
        url: str,
        details: dict
    ) -> str:
        """
        Generate a suggested action based on the failure type.

        Args:
            status: Status classification
            url: The URL that was checked
            details: Details dict from classification

        Returns:
            Human-readable suggested action string
        """
        if status == 'NOT_FOUND':
            if '/resource/blob/' in url:
                return "PDF document replaced. Search eurex.com for updated version."
            else:
                # Extract domain from URL
                from urllib.parse import urlparse
                domain = urlparse(url).netloc
                return f"Page removed. Search {domain} for replacement."

        elif status == 'REDIRECT':
            final_url = details.get('final_url', '')
            return f"URL redirects to {final_url}. Update reference."

        elif status == 'MOVED_PDF':
            return "PDF document has been updated. Review for content changes."

        elif status == 'SOFT_404':
            return "Page appears to be an error page. Verify manually."

        elif status == 'TIMEOUT':
            return "Server not responding. May be temporary. Retry manually."

        elif status == 'SERVER_ERROR':
            status_code = details.get('status_code', 'unknown')
            return f"Server error ({status_code}). May be temporary."

        elif status == 'DOMAIN_ERROR':
            error_detail = details.get('error_detail', '')
            if 'DNS' in error_detail or 'getaddrinfo' in error_detail:
                return "Domain not found. Verify domain is correct."
            elif 'SSL' in error_detail or 'certificate' in error_detail:
                return "SSL certificate error. Site may be misconfigured."
            else:
                return "Connection failed. Check URL and try again."

        return "Manual review required."

    def run(self) -> dict:
        """
        Run the link checker and produce results.

        Returns:
            Results dictionary with all validation data
        """
        logger.info("Starting link checker...")

        # Discover all URLs
        url_locations = self._discover_urls()
        total_urls = sum(len(locations) for locations in url_locations.values())
        unique_urls = len(url_locations)

        # Initialize result counters
        results = {
            'OK': 0,
            'REDIRECT': 0,
            'MOVED_PDF': 0,
            'NOT_FOUND': 0,
            'SERVER_ERROR': 0,
            'TIMEOUT': 0,
            'DOMAIN_ERROR': 0,
            'SOFT_404': 0
        }

        failures = []
        pdf_updates = []

        # Check each unique URL
        logger.info(f"Checking {unique_urls} unique URLs...")
        for idx, (url, locations) in enumerate(url_locations.items(), 1):
            if idx % 10 == 0:
                logger.info(f"Progress: {idx}/{unique_urls} URLs checked")

            status, details = self._classify_url(url)
            results[status] += 1

            # Track failures (anything non-OK)
            if status != 'OK':
                failure_entry = {
                    'url': url,
                    'status': status,
                    'locations': locations,
                    'error_detail': details.get('error_detail', ''),
                    'final_url': details.get('final_url', url),
                    'suggested_action': self._generate_suggested_action(
                        status, url, details
                    )
                }
                failures.append(failure_entry)

                # Separate tracking for PDF updates
                if status == 'MOVED_PDF':
                    pdf_entry = {
                        'url': url,
                        'old_hash': details.get('old_hash', ''),
                        'new_hash': details.get('new_hash', ''),
                        'old_content_length': details.get('old_content_length', 0),
                        'new_content_length': details.get('new_content_length', 0),
                        'locations': locations,
                        'suggested_action': failure_entry['suggested_action']
                    }
                    pdf_updates.append(pdf_entry)

        logger.info(f"Link checking complete. {results['OK']}/{unique_urls} URLs OK")

        # Build final result
        result = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_urls': total_urls,
            'unique_urls': unique_urls,
            'results': results,
            'failures': failures,
            'pdf_updates': pdf_updates
        }

        return result


def main():
    """CLI entry point for standalone execution."""
    parser = argparse.ArgumentParser(
        description='Check all URLs in markdown files for validity'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('scripts/verification/config.yaml'),
        help='Path to configuration YAML file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('links_result.json'),
        help='Path for JSON output file'
    )
    parser.add_argument(
        '--registry',
        type=Path,
        default=Path('knowledge_base/fact_registry.yaml'),
        help='Path to fact registry YAML file'
    )

    args = parser.parse_args()

    # Load configuration
    if not args.config.exists():
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(2)

    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(2)

    # Determine repository root (assume script is in scripts/verification/)
    repo_root = Path(__file__).parent.parent.parent

    # Initialize and run checker
    checker = LinkChecker(
        config=config,
        repo_root=repo_root,
        registry_path=args.registry if args.registry.exists() else None
    )

    result = checker.run()

    # Write results to JSON
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        logger.info(f"Results written to {args.output}")
    except Exception as e:
        logger.error(f"Failed to write results: {e}")
        sys.exit(2)

    # Determine exit code
    has_failures = len(result['failures']) > 0
    has_warnings = (
        result['results']['REDIRECT'] > 0 or
        result['results']['MOVED_PDF'] > 0
    )

    if has_failures:
        logger.warning(f"Link checking found {len(result['failures'])} failures")
        sys.exit(2)
    elif has_warnings:
        logger.warning(f"Link checking found warnings (redirects or PDF updates)")
        sys.exit(1)
    else:
        logger.info("All links validated successfully")
        sys.exit(0)


if __name__ == '__main__':
    main()
