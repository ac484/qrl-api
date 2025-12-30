"""Session builders for HTTP clients."""
from typing import Dict, Optional

import httpx


def build_async_client(headers: Dict[str, str], timeout: float) -> httpx.AsyncClient:
    """Create a configured AsyncClient with sane defaults."""
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    return httpx.AsyncClient(headers=headers, timeout=timeout, limits=limits)


__all__ = ["build_async_client"]
