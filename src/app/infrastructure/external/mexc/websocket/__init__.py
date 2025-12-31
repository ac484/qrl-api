"""Websocket utilities for MEXC client."""
from .client import MEXCWebSocketClient, WS_BASE
from .data_streams import (
    DEFAULT_USER_STREAM_CHANNELS,
    account_update_stream,
    user_deals_stream,
    user_orders_stream,
)
from .handlers import MessageHandler
from .manager import websocket_manager
from .market_streams import (
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

__all__ = [
    "BinaryDecoder",
    "MEXCWebSocketClient",
    "WS_BASE",
    "DEFAULT_USER_STREAM_CHANNELS",
    "account_update_stream",
    "user_deals_stream",
    "user_orders_stream",
    "websocket_manager",
    "MessageHandler",
    "book_ticker_batch_stream",
    "book_ticker_stream",
    "build_protobuf_decoder",
    "diff_depth_stream",
    "kline_stream",
    "mini_tickers_stream",
    "partial_depth_stream",
    "trade_stream",
]
