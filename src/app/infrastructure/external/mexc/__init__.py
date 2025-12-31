"""MEXC API client for spot trading."""
from src.app.infrastructure.external.mexc.client import MEXCClient, mexc_client
from src.app.infrastructure.external.mexc.exceptions import MEXCAPIException
from src.app.infrastructure.external.mexc.ws_channels import (
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
    "MEXCClient",
    "mexc_client",
    "MEXCAPIException",
    "diff_depth_stream",
    "partial_depth_stream",
    "trade_stream",
    "kline_stream",
    "book_ticker_stream",
    "book_ticker_batch_stream",
    "mini_tickers_stream",
    "build_protobuf_decoder",
]
