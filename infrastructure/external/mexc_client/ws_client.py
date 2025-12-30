"""
Convenience helpers wrapping the websocket core and channel builders.
"""
from __future__ import annotations

import asyncio
from contextlib import suppress
from typing import Any, AsyncIterator, Iterable, Optional

from infrastructure.external.mexc_client import MEXCClient
from infrastructure.external.mexc_client.ws_channels import (
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
from infrastructure.external.mexc_client.ws_core import MEXCWebSocketClient, WS_BASE


async def _keepalive_listen_key(
    client: MEXCClient, listen_key: str, interval: int
) -> None:
    while True:
        await asyncio.sleep(interval)
        await client.keepalive_listen_key(listen_key)


async def connect_public_trades(
    symbol: str,
    interval: str = "100ms",
    binary_decoder: Optional[BinaryDecoder] = None,
) -> AsyncIterator[Any]:
    channel = trade_stream(symbol, interval)
    async with MEXCWebSocketClient(
        subscriptions=[channel], binary_decoder=binary_decoder
    ) as stream:
        async for msg in stream:
            yield msg


async def connect_user_stream(
    mexc_client: Optional[MEXCClient] = None,
    channels: Optional[Iterable[str]] = None,
    listen_key: Optional[str] = None,
    binary_decoder: Optional[BinaryDecoder] = None,
    keepalive_interval: Optional[int] = 25 * 60,
    close_listen_key_on_exit: bool = False,
) -> AsyncIterator[Any]:
    client = mexc_client or MEXCClient()
    async with client:
        if not listen_key:
            listen_resp = await client.create_listen_key()
            listen_key = listen_resp.get("listenKey")
        if not listen_key:
            raise RuntimeError("listenKey was not returned by MEXC")

        keepalive_task: Optional[asyncio.Task[None]] = None
        if keepalive_interval:
            keepalive_task = asyncio.create_task(
                _keepalive_listen_key(client, listen_key, keepalive_interval)
            )

        url = f"{WS_BASE}?listenKey={listen_key}"
        subs = list(
            channels
            or [
                "spot@private.account.v3.api.pb",
                "spot@private.deals.v3.api.pb",
                "spot@private.orders.v3.api.pb",
            ]
        )

        try:
            async with MEXCWebSocketClient(
                url=url, subscriptions=subs, binary_decoder=binary_decoder
            ) as stream:
                async for msg in stream:
                    yield msg
        finally:
            if keepalive_task:
                keepalive_task.cancel()
                with suppress(asyncio.CancelledError):
                    await keepalive_task
            if close_listen_key_on_exit:
                await client.close_listen_key(listen_key)


__all__ = [
    "MEXCWebSocketClient",
    "connect_public_trades",
    "connect_user_stream",
    "trade_stream",
    "kline_stream",
    "diff_depth_stream",
    "partial_depth_stream",
    "book_ticker_stream",
    "book_ticker_batch_stream",
    "mini_tickers_stream",
    "build_protobuf_decoder",
]
