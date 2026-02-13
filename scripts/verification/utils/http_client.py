"""HTTP client with rate limiting, retry logic, and soft 404 detection."""

import hashlib
import time
from typing import Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class RateLimitedClient:
    """HTTP client with per-domain rate limiting and retry logic."""

    def __init__(self, config: dict):
        """Initialize client with configuration.

        Args:
            config: Configuration dictionary containing rate_limits, retry, timeouts, etc.
        """
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.get('user_agent', 'hft-exchange-knowledge-verifier/1.0')
        })
        self._domain_timestamps: dict[str, float] = {}

        # Extract config values
        self.rate_limit = config.get('rate_limits', {}).get('default', 2)  # req/s
        self.max_retries = config.get('retry', {}).get('max_retries', 3)
        self.backoff_base = config.get('retry', {}).get('backoff_base', 1)
        self.backoff_multiplier = config.get('retry', {}).get('backoff_multiplier', 4)
        self.timeout = config.get('timeouts', {}).get('request', 30)

        # Soft 404 patterns
        self.soft_404_patterns = config.get('soft_404_patterns', [])
        self.db_specific_soft_404 = config.get('db_specific_soft_404', {})

    def _get_domain(self, url: str) -> str:
        """Extract domain from URL.

        Args:
            url: Full URL

        Returns:
            Domain name (e.g., 'eurex.com')
        """
        parsed = urlparse(url)
        return parsed.netloc

    def _wait_for_rate_limit(self, domain: str):
        """Wait if needed to respect rate limit for domain.

        Args:
            domain: Domain name to check rate limit for
        """
        if domain not in self._domain_timestamps:
            self._domain_timestamps[domain] = 0

        min_interval = 1.0 / self.rate_limit  # seconds between requests
        elapsed = time.time() - self._domain_timestamps[domain]

        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)

        self._domain_timestamps[domain] = time.time()

    def _is_soft_404(self, url: str, final_url: str, response: requests.Response) -> bool:
        """Detect soft 404 errors (200 status but no real content).

        Args:
            url: Original requested URL
            final_url: Final URL after redirects
            response: Response object

        Returns:
            True if this appears to be a soft 404
        """
        # Check for generic soft 404 patterns in body
        try:
            content = response.text.lower()
            for pattern in self.soft_404_patterns:
                if pattern.lower() in content:
                    return True
        except:
            pass

        # DB-specific checks
        domain = self._get_domain(url)
        if not any(approved in domain for approved in self.config.get('approved_domains', [])):
            return False

        # Check 1: Homepage redirect (deep path redirects to domain root)
        if self.db_specific_soft_404.get('homepage_redirect', True):
            original_path = urlparse(url).path
            final_path = urlparse(final_url).path
            if len(original_path) > 10 and final_path in ['/', '/en/', '/de/']:
                return True

        # Check 2: Expired blob landing page
        if self.db_specific_soft_404.get('expired_blob_landing', True):
            if '/resource/blob/' in url.lower():
                try:
                    soup = BeautifulSoup(response.content, 'lxml')
                    # Look for generic landing page indicators
                    if soup.find('title') and 'deutsche börse' in soup.find('title').text.lower():
                        # If we're on a blob URL but title is generic, likely expired
                        if not any(word in response.text.lower() for word in ['pdf', 'document', 'download']):
                            return True
                except:
                    pass

        # Check 3: Meta refresh redirect
        if self.db_specific_soft_404.get('meta_refresh_redirect', True):
            if '<meta http-equiv="refresh"' in response.text.lower():
                return True

        return False

    def fetch(self, url: str, method: str = "GET", stream: bool = False) -> dict:
        """Fetch URL with rate limiting and retry logic.

        Args:
            url: URL to fetch
            method: HTTP method (GET, HEAD, etc.)
            stream: Whether to stream response

        Returns:
            Dictionary with response metadata and status
        """
        domain = self._get_domain(url)
        result = {
            "url": url,
            "status_code": 0,
            "final_url": url,
            "content_type": "",
            "content_length": 0,
            "content_hash": "",
            "response_time_ms": 0.0,
            "error": None,
            "is_soft_404": False,
            "headers": {}
        }

        for attempt in range(self.max_retries):
            try:
                self._wait_for_rate_limit(domain)

                start_time = time.time()
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    allow_redirects=True,
                    stream=stream
                )
                elapsed_ms = (time.time() - start_time) * 1000

                result["status_code"] = response.status_code
                result["final_url"] = response.url
                result["content_type"] = response.headers.get('Content-Type', '')
                result["content_length"] = int(response.headers.get('Content-Length', 0))
                result["response_time_ms"] = elapsed_ms
                result["headers"] = dict(response.headers)

                # Compute hash for GET requests (not streaming)
                if method == "GET" and not stream:
                    content = response.content
                    result["content_hash"] = hashlib.sha256(content).hexdigest()
                    result["content_length"] = len(content)

                # Check for soft 404
                if response.status_code == 200 and method == "GET" and not stream:
                    result["is_soft_404"] = self._is_soft_404(url, response.url, response)

                return result

            except requests.exceptions.RequestException as e:
                # Calculate backoff delay
                if attempt < self.max_retries - 1:
                    delay = self.backoff_base * (self.backoff_multiplier ** attempt)
                    time.sleep(delay)
                else:
                    result["error"] = str(e)
                    return result

        return result

    def check_pdf(
        self,
        url: str,
        known_content_length: Optional[int] = None,
        known_hash: Optional[str] = None
    ) -> dict:
        """Check if PDF has changed using HEAD request and optional full download.

        Args:
            url: PDF URL to check
            known_content_length: Previously recorded Content-Length
            known_hash: Previously recorded SHA-256 hash

        Returns:
            Dictionary with change detection results
        """
        result = {
            "url": url,
            "changed": False,
            "new_content_length": 0,
            "new_hash": "",
            "error": None,
            "status_code": 0
        }

        # First try HEAD request
        head_result = self.fetch(url, method="HEAD")
        result["status_code"] = head_result["status_code"]

        if head_result["error"]:
            result["error"] = head_result["error"]
            return result

        if head_result["status_code"] != 200:
            result["error"] = f"HTTP {head_result['status_code']}"
            return result

        new_length = head_result["content_length"]
        result["new_content_length"] = new_length

        # If we have known length and it matches, assume unchanged
        if known_content_length is not None and new_length == known_content_length:
            result["changed"] = False
            result["new_hash"] = known_hash or ""
            return result

        # Content-Length differs or unavailable - do full GET to compute hash
        get_result = self.fetch(url, method="GET")

        if get_result["error"]:
            result["error"] = get_result["error"]
            return result

        if get_result["status_code"] != 200:
            result["error"] = f"HTTP {get_result['status_code']}"
            return result

        result["new_content_length"] = get_result["content_length"]
        result["new_hash"] = get_result["content_hash"]

        # Compare hash if we have a known hash
        if known_hash:
            result["changed"] = (get_result["content_hash"] != known_hash)
        else:
            # No known hash - if length changed, consider it changed
            result["changed"] = (known_content_length is not None and
                               new_length != known_content_length)

        return result
