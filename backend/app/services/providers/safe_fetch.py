"""Safe HTTP client with SSRF protection and strict security controls.

Guards against Server-Side Request Forgery (SSRF), DNS rebinding,
overly large responses, and malicious protocols.
"""
import asyncio
import ipaddress
import logging
import socket
from typing import Optional, Tuple
from urllib.parse import urlparse

import httpx

from app.utils.security import is_private_ip, validate_url_for_fetch

logger = logging.getLogger(__name__)

# Security parameters
MAX_RESPONSE_SIZE = 5 * 1024 * 1024  # 5 MB
DEFAULT_CONNECT_TIMEOUT = 5.0
DEFAULT_READ_TIMEOUT = 15.0
MAX_REDIRECTS = 5
ALLOWED_CONTENT_TYPES = {
    'text/html',
    'application/xhtml+xml',
    'text/plain',
    'application/json',
}


class SSRFValidationError(Exception):
    """Raised when a URL or resolved IP fails security checks."""
    pass


def resolve_and_validate_hostname(hostname: str) -> list[str]:
    """Resolve hostname and check all IP addresses against private ranges.
    
    Prevents DNS rebinding and internal network scanning.
    """
    try:
        addr_info = socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)
    except socket.gaierror as e:
        raise SSRFValidationError(f"Could not resolve hostname '{hostname}': {e}")

    resolved_ips = set()
    for item in addr_info:
        ip = item[4][0]
        resolved_ips.add(ip)

    if not resolved_ips:
        raise SSRFValidationError(f"No IP addresses resolved for '{hostname}'")

    for ip in resolved_ips:
        if is_private_ip(ip):
            raise SSRFValidationError(
                f"Resolved IP {ip} for host '{hostname}' belongs to a private/reserved address space."
            )

    return list(resolved_ips)


class SafeFetcher:
    """HTTP client with enforced SSRF protection and content inspection."""

    @staticmethod
    async def fetch(
        url: str,
        timeout_read: float = DEFAULT_READ_TIMEOUT,
        max_size: int = MAX_RESPONSE_SIZE,
    ) -> Tuple[str, dict]:
        """Safely fetch web content.
        
        Returns (html_or_text_content, metadata_dict).
        Raises SSRFValidationError or httpx.HTTPError.
        """
        # Validate URL structure
        is_safe, error_msg = validate_url_for_fetch(url)
        if not is_safe:
            raise SSRFValidationError(error_msg or "Invalid URL")

        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            raise SSRFValidationError("Hostname missing from URL")

        # DNS resolution check
        resolve_and_validate_hostname(hostname)

        transport = httpx.AsyncHTTPTransport(verify=True)
        timeout = httpx.Timeout(connect=DEFAULT_CONNECT_TIMEOUT, read=timeout_read, write=5.0, pool=5.0)

        headers = {
            'User-Agent': 'ClaimLens-MisinformationDetector/1.0 (+https://github.com/claimlens/claimlens; academic research)',
            'Accept': 'text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
        }

        async with httpx.AsyncClient(transport=transport, timeout=timeout, follow_redirects=False) as client:
            current_url = url
            response = None

            # Handle redirects manually to validate destination IPs each hop
            for _ in range(MAX_REDIRECTS):
                resp = await client.get(current_url, headers=headers)

                # Check redirect status
                if resp.status_code in (301, 302, 303, 307, 308):
                    location = resp.headers.get('Location')
                    if not location:
                        break

                    # Construct target redirect URL
                    target_url = httpx.URL(current_url).join(location)
                    target_str = str(target_url)

                    # Re-validate new URL for SSRF
                    is_safe_redir, redir_err = validate_url_for_fetch(target_str)
                    if not is_safe_redir:
                        raise SSRFValidationError(f"Redirect blocked: {redir_err}")

                    redir_parsed = urlparse(target_str)
                    if redir_parsed.hostname:
                        resolve_and_validate_hostname(redir_parsed.hostname)

                    current_url = target_str
                    continue
                else:
                    response = resp
                    break

            if response is None:
                raise SSRFValidationError("Too many redirects or failed to get response")

            response.raise_for_status()

            # Content-Type validation
            content_type = response.headers.get('Content-Type', '').split(';')[0].strip().lower()
            if content_type and content_type not in ALLOWED_CONTENT_TYPES:
                raise SSRFValidationError(f"Unsupported content type '{content_type}'. Must be text or html.")

            # Content length check
            content_len_header = response.headers.get('Content-Length')
            if content_len_header:
                try:
                    if int(content_len_header) > max_size:
                        raise SSRFValidationError(f"Content length exceeds limit of {max_size} bytes")
                except ValueError:
                    pass

            text = response.text
            if len(text.encode('utf-8')) > max_size:
                raise SSRFValidationError(f"Downloaded payload exceeds maximum size of {max_size} bytes")

            metadata = {
                'url': str(response.url),
                'status_code': response.status_code,
                'content_type': content_type,
                'headers': dict(response.headers),
            }

            return text, metadata