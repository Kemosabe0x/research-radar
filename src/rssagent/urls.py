"""Normalize and validate journal URLs from the CSV."""

from __future__ import annotations

from urllib.parse import urlparse


def normalize_http_url(raw: str | None) -> str:
    """
    Return a fetchable http(s) URL, or empty string if not recoverable.

    Handles missing schemes (e.g. ``example.com/feed``) and strips whitespace.
    """
    if raw is None:
        return ""
    url = str(raw).strip()
    if not url or url.lower() in ("nan", "none", "n/a"):
        return ""

    parsed = urlparse(url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return url

    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return ""

    # Bare domain or path — assume https
    if url.startswith("//"):
        return f"https:{url}"
    return f"https://{url.lstrip('/')}"


def is_valid_http_url(url: str) -> bool:
    """True when URL has http(s) scheme and a host."""
    if not url:
        return False
    parsed = urlparse(url)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)
