"""MEXC WebSocket client."""
from .ws_core import MEXCWebSocketClient, WS_BASE, websockets
from .ws_channels import (
    BinaryDecoder,
    DEFAULT_USER_STREAM_CHANNELS,
    account_update_stream,
    book_ticker_batch_stream,
    book_ticker_stream,
    build_protobuf_decoder,
    diff_depth_stream,
    kline_stream,
    mini_tickers_stream,
    partial_depth_stream,
    trade_stream,
    user_deals_stream,
    user_orders_stream,
)

__all__ = [
    "BinaryDecoder",
    "MEXCWebSocketClient",
    "WS_BASE",
    "websockets",
    "DEFAULT_USER_STREAM_CHANNELS",
    "account_update_stream",
    "diff_depth_stream",
    "partial_depth_stream",
    "trade_stream",
    "kline_stream",
    "book_ticker_stream",
    "book_ticker_batch_stream",
    "mini_tickers_stream",
    "build_protobuf_decoder",
    "user_deals_stream",
    "user_orders_stream",
]
