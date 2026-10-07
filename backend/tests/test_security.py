"""Unit tests for security utilities and SSRF prevention."""
import pytest
from app.utils.security import generate_token, hash_token, verify_token, is_private_ip, validate_url_for_fetch


def test_token_generation_and_verification():
    token = generate_token()
    token_hash = hash_token(token)

    assert len(token) > 20
    assert len(token_hash) == 64  # SHA-256 hex string
    assert verify_token(token, token_hash) is True
    assert verify_token("wrong_token", token_hash) is False


def test_ssrf_private_ips_blocked():
    # IPv4 loopback & private
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("10.0.0.1") is True
    assert is_private_ip("192.168.1.1") is True
    assert is_private_ip("172.16.0.1") is True
    assert is_private_ip("169.254.169.254") is True  # Cloud metadata
    assert is_private_ip("0.0.0.0") is True

    # IPv6 loopback & private
    assert is_private_ip("::1") is True
    assert is_private_ip("fc00::1") is True
    assert is_private_ip("fe80::1") is True

    # Public IP
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("1.1.1.1") is False


def test_validate_url_for_fetch():
    # Safe public HTTP(S)
    ok, _ = validate_url_for_fetch("https://en.wikipedia.org/wiki/Earth")
    assert ok is True

    # Non-HTTP schemes blocked
    ok, err = validate_url_for_fetch("file:///etc/passwd")
    assert ok is False
    assert "scheme" in err.lower()

    ok, err = validate_url_for_fetch("ftp://ftp.example.com")
    assert ok is False

    # Embedded credentials blocked
    ok, err = validate_url_for_fetch("https://admin:password@example.com/api")
    assert ok is False
    assert "credentials" in err.lower()

    # Non-standard ports blocked
    ok, err = validate_url_for_fetch("http://example.com:22/secret")
    assert ok is False
    assert "port" in err.lower()
