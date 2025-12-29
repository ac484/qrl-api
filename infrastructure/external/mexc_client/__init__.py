"""
MEXC client package
-------------------
Provides the async MEXCClient and shared mexc_client instance.
"""
from .client import MEXCClient, mexc_client

__all__ = ["MEXCClient", "mexc_client"]
