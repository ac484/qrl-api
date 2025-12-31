"""MEXC WebSocket client."""
from .ws_core import MEXCWebSocketClient, WS_BASE, websockets
from .ws_channels import (
    diff_depth_stream,
    partial_depth_stream,
    trade_stream,
    kline_stream,
    book_ticker_stream,
    book_ticker_batch_stream,
    mini_tickers_stream,
    build_protobuf_decoder,
)

__all__ = [
    "MEXCWebSocketClient",
    "WS_BASE",
    "websockets",
    "diff_depth_stream",
    "partial_depth_stream",
    "trade_stream",
    "kline_stream",
    "book_ticker_stream",
    "book_ticker_batch_stream",
    "mini_tickers_stream",
    "build_protobuf_decoder",
]
