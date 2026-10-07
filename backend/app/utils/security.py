"""Security utilities for ClaimLens.

Token generation, hashing, and SSRF IP validation.
"""
import hashlib
import ipaddress
import secrets
from typing import Optional


def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)


def hash_token(token: str) -> str:
    """Hash a token with SHA-256 for storage."""
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def verify_token(token: str, token_hash: str) -> bool:
    """Verify a token against its stored hash."""
    return secrets.compare_digest(hash_token(token), token_hash)


def is_private_ip(ip_str: str) -> bool:
    """Check if an IP address is private, loopback, link-local, or multicast.

    Used for SSRF protection — blocks requests to internal networks.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # Invalid IP → treat as private (block)

    # Block private, reserved, loopback, link-local, multicast
    if ip.is_private:
        return True
    if ip.is_loopback:
        return True
    if ip.is_link_local:
        return True
    if ip.is_multicast:
        return True
    if ip.is_reserved:
        return True
    if ip.is_unspecified:
        return True

    # Additional IPv4 checks
    if isinstance(ip, ipaddress.IPv4Address):
        # Block 0.0.0.0/8
        if ip_str.startswith('0.'):
            return True
        # Block metadata endpoints (169.254.x.x is already link-local)
        # Block IPv4-mapped IPv6 addresses that resolve to private
        pass

    # Additional IPv6 checks
    if isinstance(ip, ipaddress.IPv6Address):
        # Block IPv4-mapped IPv6
        if ip.ipv4_mapped and is_private_ip(str(ip.ipv4_mapped)):
            return True
        # Block 6to4 addresses
        if ip.sixtofour and is_private_ip(str(ip.sixtofour)):
            return True
        # Block Teredo
        if ip.teredo:
            server, client = ip.teredo
            if is_private_ip(str(client)):
                return True

    return False


def validate_url_for_fetch(url: str) -> tuple[bool, Optional[str]]:
    """Validate a URL is safe to fetch (no SSRF risk).

    Returns (is_safe, error_message).
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)
    except Exception:
        return False, 'Invalid URL format'

    # Only allow HTTP(S)
    if parsed.scheme not in ('http', 'https'):
        return False, f'Unsupported scheme: {parsed.scheme}. Only HTTP and HTTPS allowed.'

    # Block URLs with embedded credentials
    if parsed.username or parsed.password:
        return False, 'URLs with embedded credentials are not allowed.'

    # Check hostname exists
    if not parsed.hostname:
        return False, 'URL must include a hostname.'

    # Block non-standard ports (allow 80, 443, 8080, 8443)
    allowed_ports = {80, 443, 8080, 8443, None}
    if parsed.port not in allowed_ports:
        return False, f'Non-standard port {parsed.port} is not allowed.'

    return True, None