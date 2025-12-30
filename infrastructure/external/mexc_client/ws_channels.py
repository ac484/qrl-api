"""
Channel builders and protobuf decoder helpers for MEXC spot websocket v3.
"""
from __future__ import annotations

from typing import Any, Callable, Type

from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

BinaryDecoder = Callable[[bytes], Any]

_TRADE_INTERVALS = {"100ms", "10ms"}
_DEPTH_LIMITS = {5, 10, 20}
_KLINE_INTERVALS = {
    "Min1",
    "Min5",
    "Min15",
    "Min30",
    "Min60",
    "Hour4",
    "Hour8",
    "Day1",
    "Week1",
    "Month1",
}


def build_protobuf_decoder(message_cls: Type[Message]) -> BinaryDecoder:
    """
    Create a decoder that converts protobuf bytes into a Python dict.
    """

    def _decoder(raw: bytes) -> dict:
        message = message_cls()
        message.ParseFromString(raw)
        return MessageToDict(message, preserving_proto_field_name=True)

    return _decoder


def trade_stream(symbol: str, interval: str = "100ms") -> str:
    if interval not in _TRADE_INTERVALS:
        raise ValueError(f"interval must be one of {_TRADE_INTERVALS}")
    return f"spot@public.aggre.deals.v3.api.pb@{interval}@{symbol.upper()}"


def kline_stream(symbol: str, interval: str) -> str:
    if interval not in _KLINE_INTERVALS:
        raise ValueError(f"interval must be one of {_KLINE_INTERVALS}")
    return f"spot@public.kline.v3.api.pb@{symbol.upper()}@{interval}"


def diff_depth_stream(symbol: str, interval: str = "100ms") -> str:
    if interval not in _TRADE_INTERVALS:
        raise ValueError(f"interval must be one of {_TRADE_INTERVALS}")
    return f"spot@public.aggre.depth.v3.api.pb@{interval}@{symbol.upper()}"


def partial_depth_stream(symbol: str, depth: int = 5) -> str:
    if depth not in _DEPTH_LIMITS:
        raise ValueError(f"depth must be one of {_DEPTH_LIMITS}")
    return f"spot@public.limit.depth.v3.api.pb@{symbol.upper()}@{depth}"


def book_ticker_stream(symbol: str, interval: str = "100ms") -> str:
    if interval not in _TRADE_INTERVALS:
        raise ValueError(f"interval must be one of {_TRADE_INTERVALS}")
    return f"spot@public.aggre.bookTicker.v3.api.pb@{interval}@{symbol.upper()}"


def book_ticker_batch_stream(symbol: str) -> str:
    return f"spot@public.bookTicker.batch.v3.api.pb@{symbol.upper()}"


def mini_tickers_stream(timezone: str = "UTC+0") -> str:
    return f"spot@public.mini.ticker.v3.api.pb@{timezone}"
