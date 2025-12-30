"""Backward-compatible import surface for the MEXC client."""
from .client import MEXCClient, mexc_client

__all__ = ["MEXCClient", "mexc_client"]
