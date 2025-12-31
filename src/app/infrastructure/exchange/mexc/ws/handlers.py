"""
Websocket handler shims exposing legacy channel builders and decoders.
"""

from src.app.infrastructure.external.mexc.ws_channels import (
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
    "DEFAULT_USER_STREAM_CHANNELS",
    "account_update_stream",
    "book_ticker_batch_stream",
    "book_ticker_stream",
    "build_protobuf_decoder",
    "diff_depth_stream",
    "kline_stream",
    "mini_tickers_stream",
    "partial_depth_stream",
    "trade_stream",
    "user_deals_stream",
    "user_orders_stream",
]
