"""
Minimal MEXC WebSocket helpers (Occam-friendly).

- connect_user_stream: create listenKey then subscribe to private channels.
- connect_public_trades: subscribe to aggregated public trades for a symbol.
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncIterator, Iterable, Optional

import websockets

from infrastructure.external.mexc_client import MEXCClient

WS_BASE = "wss://wbs-api.mexc.com/ws"


async def _ws_loop(url: str, subs: Iterable[str]) -> AsyncIterator[dict]:
    async with websockets.connect(url, ping_interval=25, close_timeout=5) as ws:
        await ws.send(json.dumps({"method": "SUBSCRIPTION", "params": list(subs)}))
        while True:
            raw = await ws.recv()
            try:
                yield json.loads(raw)
            except Exception:
                yield {"raw": raw}


async def connect_public_trades(symbol: str, interval: str = "100ms") -> AsyncIterator[dict]:
    """
    Minimal public trades subscriber.
    Args:
        symbol: e.g., "BTCUSDT"
        interval: "100ms" or "10ms"
    """
    channel = f"spot@public.aggre.deals.v3.api.pb@{interval}@{symbol.upper()}"
    async for msg in _ws_loop(WS_BASE, [channel]):
        yield msg


async def connect_user_stream(
    mexc_client: Optional[MEXCClient] = None,
    channels: Optional[Iterable[str]] = None,
) -> AsyncIterator[dict]:
    """
    Minimal private stream subscriber.
    Steps: create listenKey -> connect -> subscribe private channels.
    """
    client = mexc_client or MEXCClient()
    async with client:
        listen_resp = await client._request("POST", "/api/v3/userDataStream", signed=True)
        listen_key = listen_resp.get("listenKey")
    url = f"{WS_BASE}?listenKey={listen_key}"
    subs = channels or [
        "spot@private.account.v3.api.pb",
        "spot@private.deals.v3.api.pb",
        "spot@private.orders.v3.api.pb",
    ]
    async for msg in _ws_loop(url, subs):
        yield msg


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
