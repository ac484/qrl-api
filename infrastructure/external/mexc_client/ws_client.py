"""
MEXC WebSocket helpers with protobuf-friendly decoding and live subs/unsubs.

- MEXCWebSocketClient: lightweight wrapper that handles SUBSCRIPTION/UNSUBSCRIPTION,
  PING/PONG, and optional protobuf decoding for binary frames.
- Channel builders for public market streams (trades, klines, depth, book tickers).
- User-data helpers that create/extend listen keys before opening the stream.
"""
from __future__ import annotations

import asyncio
import json
from contextlib import suppress
from typing import Any, AsyncIterator, Callable, Iterable, Optional, Sequence, Set, Type

import websockets
from websockets.exceptions import ConnectionClosed
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message

from infrastructure.external.mexc_client import MEXCClient

WS_BASE = "wss://wbs-api.mexc.com/ws"
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
    Build a decoder that converts protobuf bytes into a Python dict.
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


class MEXCWebSocketClient:
    """
    Lightweight websocket client that supports live SUBSCRIPTION/UNSUBSCRIPTION,
    optional protobuf decoding, and explicit PING/PONG messages.
    """

    def __init__(
        self,
        url: str = WS_BASE,
        subscriptions: Optional[Iterable[str]] = None,
        binary_decoder: Optional[BinaryDecoder] = None,
        heartbeat: Optional[int] = 20,
        close_timeout: int = 5,
    ) -> None:
        self.url = url
        self.subscriptions: Set[str] = set(subscriptions or [])
        self._binary_decoder = binary_decoder
        self._heartbeat = heartbeat
        self._close_timeout = close_timeout
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._ping_task: Optional[asyncio.Task[None]] = None

    async def __aenter__(self) -> "MEXCWebSocketClient":
        self._ws = await websockets.connect(
            self.url,
            ping_interval=None,  # we send explicit PING frames expected by MEXC
            close_timeout=self._close_timeout,
        )
        if self.subscriptions:
            await self.subscribe(self.subscriptions)
        if self._heartbeat:
            self._ping_task = asyncio.create_task(self._auto_ping())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._ping_task:
            self._ping_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._ping_task
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def _auto_ping(self) -> None:
        while True:
            await asyncio.sleep(self._heartbeat)  # type: ignore[arg-type]
            await self.send_ping()

    async def _send(
        self, method: str, params: Optional[Sequence[str]] = None
    ) -> None:
        if not self._ws:
            raise RuntimeError("WebSocket connection is not open")
        payload: dict[str, Any] = {"method": method}
        if params is not None:
            payload["params"] = list(params)
        await self._ws.send(json.dumps(payload))

    async def subscribe(self, channels: Iterable[str]) -> None:
        new_channels = [c for c in channels if c not in self.subscriptions]
        if not new_channels:
            return
        await self._send("SUBSCRIPTION", new_channels)
        self.subscriptions.update(new_channels)

    async def unsubscribe(self, channels: Iterable[str]) -> None:
        targets = list(channels)
        if not targets:
            return
        await self._send("UNSUBSCRIPTION", targets)
        for channel in targets:
            self.subscriptions.discard(channel)

    async def send_ping(self) -> None:
        await self._send("PING")

    async def send_pong(self) -> None:
        await self._send("PONG")

    def _is_ping(self, payload: Any) -> bool:
        if isinstance(payload, str):
            return payload.upper() == "PING"
        if isinstance(payload, dict):
            return payload.get("method", "").upper() == "PING"
        return False

    async def recv(self) -> Any:
        if not self._ws:
            raise RuntimeError("WebSocket connection is not open")
        while True:
            raw = await self._ws.recv()
            parsed = self._parse_message(raw)
            if self._is_ping(parsed):
                await self.send_pong()
                return {"type": "ping"}
            return parsed

    def _parse_message(self, raw: Any) -> Any:
        if isinstance(raw, bytes):
            return self._decode_binary(raw)
        if isinstance(raw, str):
            if raw.upper() in {"PING", "PONG"}:
                return raw.upper()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw}
        return raw

    def _decode_binary(self, raw: bytes) -> Any:
        if self._binary_decoder:
            try:
                return self._binary_decoder(raw)
            except Exception:
                return {"raw": raw}
        return {"raw": raw}

    def __aiter__(self) -> "MEXCWebSocketClient":
        return self

    async def __anext__(self) -> Any:
        try:
            return await self.recv()
        except ConnectionClosed:
            raise StopAsyncIteration


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
    """
    Subscribe to aggregated public trades for a symbol.
    """
    channel = trade_stream(symbol, interval)
    async with MEXCWebSocketClient(
        subscriptions=[channel],
        binary_decoder=binary_decoder,
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
    """
    Private stream subscriber.
    Steps: create listenKey -> connect -> subscribe private channels -> optional keepalive.
    """
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
                url=url,
                subscriptions=subs,
                binary_decoder=binary_decoder,
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


async def demo_public(symbol: str = "BTCUSDT", take: int = 3) -> None:
    count = 0
    async for msg in connect_public_trades(symbol):
        print(msg)
        count += 1
        if count >= take:
            break


async def demo_private(take: int = 3) -> None:
    count = 0
    async for msg in connect_user_stream():
        print(msg)
        count += 1
        if count >= take:
            break


if __name__ == "__main__":
    asyncio.run(demo_public())
