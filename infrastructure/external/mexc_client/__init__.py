"""
MEXC client package
-------------------
Provides the async MEXCClient, websocket helpers, and shared mexc_client instance.
"""
from .client import MEXCClient, mexc_client
from .websocket import MEXCWebSocketClient as _WSClient, websocket_manager, WS_BASE
from .ws_channels import (
    BinaryDecoder,
    book_ticker_batch_stream,
    book_ticker_stream,
    build_protobuf_decoder,
    diff_depth_stream,
    kline_stream,
    mini_tickers_stream,
    partial_depth_stream,
    trade_stream,
)
from .ws_client import connect_public_trades, connect_user_stream
MEXCWebSocketClient = _WSClient

__all__ = [
    "MEXCClient",
    "mexc_client",
    "connect_public_trades",
    "connect_user_stream",
    "MEXCWebSocketClient",
    "websocket_manager",
    "WS_BASE",
    "trade_stream",
    "kline_stream",
    "diff_depth_stream",
    "partial_depth_stream",
    "book_ticker_stream",
    "book_ticker_batch_stream",
    "mini_tickers_stream",
    "build_protobuf_decoder",
    "BinaryDecoder",
]
