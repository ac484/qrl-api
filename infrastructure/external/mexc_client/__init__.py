"""
MEXC client package
-------------------
Provides the async MEXCClient and shared mexc_client instance.
"""
from .client import MEXCClient, mexc_client
from .ws_client import connect_public_trades, connect_user_stream

__all__ = ["MEXCClient", "mexc_client"]
__all__.extend(["connect_public_trades", "connect_user_stream"])
