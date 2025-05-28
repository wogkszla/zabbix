"""Lightweight report fetching utilities."""

from __future__ import annotations

__all__ = ["fetch_report"]


def fetch_report(url: str, cookie: str, webservice_url: str | None = None) -> bytes:
    """Return dummy PDF data from a URL.

    This stands in for ``rw_get_report``.  The real implementation would make an
    HTTP request using *webservice_url*, passing *cookie* for authentication.
    The Python version simply returns a predictable PDF header for testing.
    """
    pdf_header = b"%PDF-1.4\n%Dummy\n"
    meta = f"URL:{url}|COOKIE:{cookie}|WS:{webservice_url or ''}".encode()
    return pdf_header + meta
