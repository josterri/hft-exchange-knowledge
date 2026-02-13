"""
Regulatory/Circular Monitor for Deutsche Boerse/Eurex Knowledge Base.

Monitors Deutsche Boerse and Eurex circular/announcement pages for new regulatory
updates, pricing changes, and technical releases. Uses HTML scraping as primary
method with RSS/Atom fallback, and implements a 3-day escalation protocol for
persistent scraping failures.
"""

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml
from bs4 import BeautifulSoup

# Import local utility
from utils.http_client import RateLimitedClient

# Try importing feedparser with graceful fallback
try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    logging.warning("feedparser not available - RSS fallback disabled")


class CircularMonitor:
    """
    Monitors Deutsche Boerse/Eurex circular and announcement pages.

    Features:
    - HTML scraping with BeautifulSoup for primary data extraction
    - RSS/Atom feed fallback when HTML parsing fails
    - 3-day escalation protocol for persistent scraping failures
    - Keyword-based relevance filtering
    - State persistence for incremental monitoring
    """

    def __init__(self, config: dict, state_dir: Path):
        """
        Initialize the circular monitor.

        Args:
            config: Configuration dictionary with circular_sources,
                   circular_keywords, keyword_to_files
            state_dir: Directory for persisting monitor state
        """
        self.config = config
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / "last_seen_circulars.json"

        # Extract configuration
        self.sources = config.get("circular_sources", [])
        self.keywords = config.get("circular_keywords", {})
        self.keyword_to_files = config.get("keyword_to_files", {})

        # Initialize HTTP client
        self.client = RateLimitedClient(
            rate_limit=10,  # 10 requests per minute to be respectful
            period=60.0
        )

        # Load state
        self.state = self._load_state()

        # Configure logging
        self.logger = logging.getLogger(__name__)

    def _load_state(self) -> dict:
        """
        Load previous monitoring state from disk.

        Returns:
            State dictionary with per-source tracking
        """
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load state: {e}, starting fresh")

        return {}

    def save_state(self):
        """Persist current state to disk."""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            self.logger.info(f"State saved to {self.state_file}")
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")

    def _parse_html_circulars(self, html: str, source_name: str) -> Optional[list[dict]]:
        """
        Parse HTML content to extract circular/announcement entries.

        Looks for common patterns: anchor tags with titles/URLs, div/li entries
        with dates and titles, tables with circular information.

        Args:
            html: Raw HTML content
            source_name: Name of the source for logging

        Returns:
            List of dicts with {title, date, url} or None if parsing fails
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            entries = []

            # Strategy 1: Look for tables with circular entries
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        # Try to extract title and link
                        link = row.find('a')
                        if link and link.get('href'):
                            title = link.get_text(strip=True)
                            url = link['href']

                            # Extract date if present in cells
                            date = None
                            for cell in cells:
                                text = cell.get_text(strip=True)
                                # Look for date patterns (DD.MM.YYYY, YYYY-MM-DD, etc.)
                                if re.search(r'\d{2}[./]\d{2}[./]\d{4}|\d{4}[-/]\d{2}[-/]\d{2}', text):
                                    date = text
                                    break

                            if title and url:
                                entries.append({
                                    'title': title,
                                    'date': date,
                                    'url': self._normalize_url(url, source_name)
                                })

            # Strategy 2: Look for list items with links
            if not entries:
                list_items = soup.find_all(['li', 'div'], class_=re.compile(r'circular|news|announcement|item', re.I))
                for item in list_items:
                    link = item.find('a')
                    if link and link.get('href'):
                        title = link.get_text(strip=True)
                        url = link['href']

                        # Try to find date in same item
                        date = None
                        date_match = re.search(r'\d{2}[./]\d{2}[./]\d{4}|\d{4}[-/]\d{2}[-/]\d{2}',
                                             item.get_text())
                        if date_match:
                            date = date_match.group(0)

                        if title and url:
                            entries.append({
                                'title': title,
                                'date': date,
                                'url': self._normalize_url(url, source_name)
                            })

            # Strategy 3: Generic anchor search in main content areas
            if not entries:
                content_areas = soup.find_all(['main', 'article', 'section', 'div'],
                                             class_=re.compile(r'content|main|body', re.I))
                for area in content_areas:
                    links = area.find_all('a', href=True)
                    for link in links:
                        href = link['href']
                        # Filter for circular-like URLs
                        if any(term in href.lower() for term in ['circular', 'announcement', 'news', 'pdf', 'document']):
                            title = link.get_text(strip=True)
                            if title and len(title) > 10:  # Avoid button text
                                entries.append({
                                    'title': title,
                                    'date': None,
                                    'url': self._normalize_url(href, source_name)
                                })

            if entries:
                self.logger.info(f"Parsed {len(entries)} entries from {source_name} HTML")
                return entries
            else:
                self.logger.warning(f"No circular entries found in {source_name} HTML")
                return None

        except Exception as e:
            self.logger.error(f"HTML parsing failed for {source_name}: {e}")
            return None

    def _try_rss_fallback(self, source_url: str, source_name: str) -> Optional[list[dict]]:
        """
        Attempt to fetch and parse RSS/Atom feed as fallback.

        Args:
            source_url: Base URL of the source
            source_name: Name of the source for logging

        Returns:
            List of dicts with {title, date, url} or None if fallback fails
        """
        if not HAS_FEEDPARSER:
            self.logger.debug(f"RSS fallback skipped for {source_name} - feedparser not available")
            return None

        # Try common RSS/Atom feed paths
        feed_paths = ['/rss', '/feed', '/atom', '/rss.xml', '/feed.xml']

        for path in feed_paths:
            feed_url = source_url.rstrip('/') + path
            try:
                self.logger.info(f"Trying RSS feed: {feed_url}")
                response = self.client.get(feed_url)

                if response.status_code == 200:
                    feed = feedparser.parse(response.text)

                    if feed.entries:
                        entries = []
                        for entry in feed.entries:
                            title = entry.get('title', '')
                            link = entry.get('link', '')

                            # Extract date
                            date = None
                            if hasattr(entry, 'published'):
                                date = entry.published
                            elif hasattr(entry, 'updated'):
                                date = entry.updated

                            if title and link:
                                entries.append({
                                    'title': title,
                                    'date': date,
                                    'url': link
                                })

                        if entries:
                            self.logger.info(f"RSS fallback successful for {source_name}: {len(entries)} entries")
                            return entries

            except Exception as e:
                self.logger.debug(f"RSS feed {feed_url} failed: {e}")
                continue

        self.logger.warning(f"RSS fallback failed for {source_name} - no valid feeds found")
        return None

    def _normalize_url(self, url: str, source_name: str) -> str:
        """
        Convert relative URLs to absolute URLs.

        Args:
            url: URL to normalize
            source_name: Source name for base URL lookup

        Returns:
            Absolute URL
        """
        if url.startswith('http'):
            return url

        # Get base URL from source
        for source in self.sources:
            if source.get('name') == source_name:
                base_url = source.get('url', '')
                if base_url:
                    # Handle different relative URL formats
                    if url.startswith('/'):
                        # Absolute path - use domain
                        from urllib.parse import urlparse
                        parsed = urlparse(base_url)
                        return f"{parsed.scheme}://{parsed.netloc}{url}"
                    else:
                        # Relative path - append to base
                        return base_url.rstrip('/') + '/' + url.lstrip('/')

        return url

    def _check_keywords(self, title: str) -> tuple[list[str], list[str]]:
        """
        Check title against keyword lists and determine potentially affected files.

        Args:
            title: Circular/announcement title

        Returns:
            Tuple of (matched_keywords, potentially_affected_files)
        """
        title_lower = title.lower()
        matched_keywords = []
        affected_files = set()

        # Check each keyword category
        for category, keyword_list in self.keywords.items():
            for keyword in keyword_list:
                if keyword.lower() in title_lower:
                    matched_keywords.append(keyword)

                    # Look up affected files
                    if keyword in self.keyword_to_files:
                        files = self.keyword_to_files[keyword]
                        if isinstance(files, list):
                            affected_files.update(files)
                        else:
                            affected_files.add(files)

        return matched_keywords, sorted(list(affected_files))

    def _fetch_source(self, source: dict) -> Optional[list[dict]]:
        """
        Fetch and parse a single circular source.

        Implements HTML scraping with RSS fallback and 3-day escalation protocol.

        Args:
            source: Source configuration dict with name, url

        Returns:
            List of circular entries or None on failure
        """
        source_name = source.get('name', 'Unknown')
        source_url = source.get('url')

        if not source_url:
            self.logger.error(f"No URL configured for source: {source_name}")
            return None

        self.logger.info(f"Checking source: {source_name}")

        # Initialize source state if needed
        if source_name not in self.state:
            self.state[source_name] = {
                'last_checked': None,
                'seen_titles': [],
                'consecutive_failure_count': 0
            }

        source_state = self.state[source_name]

        try:
            # Primary: HTML scraping
            response = self.client.get(source_url)
            response.raise_for_status()

            entries = self._parse_html_circulars(response.text, source_name)

            # Fallback: RSS/Atom
            if entries is None:
                self.logger.info(f"Attempting RSS fallback for {source_name}")
                entries = self._try_rss_fallback(source_url, source_name)

            # Check if we got any data
            if entries is None or len(entries) == 0:
                # Increment failure count
                source_state['consecutive_failure_count'] += 1
                self.logger.error(
                    f"Both HTML and RSS failed for {source_name} "
                    f"(consecutive failures: {source_state['consecutive_failure_count']})"
                )
                return None

            # Success - reset failure count
            source_state['consecutive_failure_count'] = 0
            source_state['last_checked'] = datetime.now().isoformat()

            return entries

        except Exception as e:
            source_state['consecutive_failure_count'] += 1
            self.logger.error(
                f"Failed to fetch {source_name}: {e} "
                f"(consecutive failures: {source_state['consecutive_failure_count']})"
            )
            return None

    def run(self) -> dict:
        """
        Main entry point - check all sources for new circulars.

        Returns:
            Result dictionary with new circulars, statistics, and failures
        """
        self.logger.info("Starting circular monitoring")

        result = {
            'timestamp': datetime.now().isoformat(),
            'total_sources_checked': len(self.sources),
            'sources_succeeded': 0,
            'sources_failed': 0,
            'new_circulars': [],
            'new_relevant': 0,
            'scraping_failures': []
        }

        # Check each source
        for source in self.sources:
            source_name = source.get('name', 'Unknown')
            entries = self._fetch_source(source)

            if entries is None:
                result['sources_failed'] += 1

                # Check for escalation (3+ consecutive failures)
                source_state = self.state.get(source_name, {})
                failure_count = source_state.get('consecutive_failure_count', 0)

                if failure_count >= 3:
                    result['scraping_failures'].append({
                        'source': source_name,
                        'consecutive_failures': failure_count,
                        'escalated': True,
                        'note': 'ESCALATED: 3+ consecutive failures - manual review required'
                    })
                else:
                    result['scraping_failures'].append({
                        'source': source_name,
                        'consecutive_failures': failure_count,
                        'escalated': False,
                        'note': f'Failed {failure_count} time(s) - will escalate at 3'
                    })

                continue

            result['sources_succeeded'] += 1

            # Check for new circulars
            source_state = self.state.get(source_name, {'seen_titles': []})
            seen_titles = set(source_state.get('seen_titles', []))

            for entry in entries:
                title = entry.get('title', '')

                if title and title not in seen_titles:
                    # New circular found
                    matched_keywords, affected_files = self._check_keywords(title)
                    is_relevant = len(matched_keywords) > 0

                    new_circular = {
                        'source': source_name,
                        'title': title,
                        'date': entry.get('date'),
                        'url': entry.get('url'),
                        'matched_keywords': matched_keywords,
                        'potentially_affects': affected_files,
                        'is_relevant': is_relevant
                    }

                    result['new_circulars'].append(new_circular)

                    if is_relevant:
                        result['new_relevant'] += 1

                    # Update seen titles
                    seen_titles.add(title)

            # Update state
            source_state['seen_titles'] = list(seen_titles)
            self.state[source_name] = source_state

        self.logger.info(
            f"Monitoring complete: {result['new_circulars']} new circulars, "
            f"{result['new_relevant']} relevant"
        )

        return result


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor Deutsche Boerse/Eurex circulars')
    parser.add_argument('--config', type=Path, required=True, help='Path to config.yaml')
    parser.add_argument('--output', type=Path, required=True, help='Path to output JSON file')
    parser.add_argument('--state-dir', type=Path, required=True, help='Directory for state files')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    # Load configuration
    try:
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        sys.exit(2)

    # Run monitor
    try:
        monitor = CircularMonitor(config, args.state_dir)
        result = monitor.run()
        monitor.save_state()

        # Write output
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Results written to {args.output}")

        # Exit code: 1 if new relevant circulars found, 0 otherwise
        sys.exit(1 if result['new_relevant'] > 0 else 0)

    except Exception as e:
        logger.error(f"Monitor failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
