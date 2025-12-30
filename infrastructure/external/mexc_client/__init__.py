"""
MEXC client package
-------------------
Provides the async MEXCClient, websocket helpers, and shared mexc_client instance.
"""
from .client import MEXCClient, mexc_client
from .ws_client import (
    MEXCWebSocketClient,
    book_ticker_batch_stream,
    book_ticker_stream,
    build_protobuf_decoder,
    connect_public_trades,
    connect_user_stream,
    diff_depth_stream,
    kline_stream,
    mini_tickers_stream,
    partial_depth_stream,
    trade_stream,
)

__all__ = ["MEXCClient", "mexc_client"]
__all__.extend(
    [
        "connect_public_trades",
        "connect_user_stream",
        "MEXCWebSocketClient",
        "trade_stream",
        "kline_stream",
        "diff_depth_stream",
        "partial_depth_stream",
        "book_ticker_stream",
        "book_ticker_batch_stream",
        "mini_tickers_stream",
        "build_protobuf_decoder",
    ]
)
