"""MEXC spot websocket client."""
from __future__ import annotations

import asyncio, json
from contextlib import suppress

import websockets
from websockets.exceptions import ConnectionClosed

WS_BASE = "wss://wbs-api.mexc.com/ws"


class MEXCWebSocketClient:
    """Websocket client with SUB/UNSUB and explicit PING/PONG."""

    def __init__(
        self,
        url=WS_BASE,
        subscriptions=None,
        binary_decoder=None,
        heartbeat: float = 20,
        close_timeout: float = 5,
    ):
        """heartbeat and close_timeout are expressed in seconds."""
        self.url = url
        self._pending = set(subscriptions or [])
        self.subscriptions = set()
        self._binary_decoder = binary_decoder
        self._heartbeat = heartbeat
        self._close_timeout = close_timeout
        self._ws = None
        self._ping_task = None

    async def __aenter__(self):
        self._ws = await websockets.connect(
            self.url, ping_interval=None, close_timeout=self._close_timeout
        )
        if self._pending:
            await self.subscribe(self._pending)
        if self._heartbeat:
            self._ping_task = asyncio.create_task(self._auto_ping())
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._ping_task:
            self._ping_task.cancel()
            with suppress(asyncio.CancelledError):
                await self._ping_task
        if self._ws:
            await self._ws.close()
            self._ws = None

    async def _auto_ping(self):
        while True:
            await asyncio.sleep(self._heartbeat)
            await self.send_ping()

    async def _send(self, method, params=None):
        if not self._ws:
            raise RuntimeError("WebSocket connection is not open")
        message = {"method": method}
        if params is not None:
            message["params"] = list(params)
        await self._ws.send(json.dumps(message))

    async def subscribe(self, channels):
        new_channels = [c for c in channels if c not in self.subscriptions]
        if not new_channels:
            return
        await self._send("SUBSCRIPTION", new_channels)
        self.subscriptions.update(new_channels)

    async def unsubscribe(self, channels):
        targets = list(channels)
        if not targets:
            return
        await self._send("UNSUBSCRIPTION", targets)
        for channel in targets:
            self.subscriptions.discard(channel)

    async def send_ping(self):
        await self._send("PING")

    async def send_pong(self):
        await self._send("PONG")

    def _parse(self, raw):
        if isinstance(raw, bytes):
            if self._binary_decoder:
                try:
                    return self._binary_decoder(raw)
                except Exception:
                    return {"raw": raw}
            return {"raw": raw}
        if isinstance(raw, str):
            if raw.upper() in {"PING", "PONG"}:
                return raw.upper()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {"raw": raw}
        return raw

    def _is_ping(self, payload):
        if isinstance(payload, str):
            return payload == "PING"
        if isinstance(payload, dict):
            return payload.get("method", "").upper() == "PING"
        return False

    async def recv(self):
        if not self._ws:
            raise RuntimeError("WebSocket connection is not open")
        while True:
            raw = await self._ws.recv()
            parsed = self._parse(raw)
            if self._is_ping(parsed):
                await self.send_pong()
                return {"type": "ping"}
            return parsed

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self.recv()
        except ConnectionClosed:
            raise StopAsyncIteration


__all__ = ["MEXCWebSocketClient", "WS_BASE"]
