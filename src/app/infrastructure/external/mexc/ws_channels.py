"""Compatibility wrapper for websocket channel helpers.

Cloud Run startup expects legacy import paths like
``src.app.infrastructure.external.mexc.ws_channels`` to exist. This module
forwards to the actual implementations under ``src.app.infrastructure.external.mexc.ws.ws_channels``.
"""
from src.app.infrastructure.external.mexc.ws.ws_channels import (
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


def account_update_stream(*_args, **_kwargs):
    """
    Placeholder to preserve backward compatibility with earlier channel helpers.

    Account update streams are not currently implemented in the v3 websocket
    helpers; this function exists only to satisfy imports without failing
    application startup.
    """
    raise NotImplementedError("account_update_stream is not implemented in v3 helpers")


__all__ = [
    "BinaryDecoder",
    "book_ticker_batch_stream",
    "book_ticker_stream",
    "build_protobuf_decoder",
    "diff_depth_stream",
    "kline_stream",
    "mini_tickers_stream",
    "partial_depth_stream",
    "trade_stream",
    "account_update_stream",
]
