"""Lightweight manager for websocket clients."""
from contextlib import asynccontextmanager
from typing import AsyncIterator, Iterable, Optional

from .client import MEXCWebSocketClient, WS_BASE


@asynccontextmanager
async def websocket_manager(
    subscriptions: Optional[Iterable[str]] = None,
    url: str = WS_BASE,
    **kwargs,
) -> AsyncIterator[MEXCWebSocketClient]:
    async with MEXCWebSocketClient(url=url, subscriptions=list(subscriptions or []), **kwargs) as client:
        yield client


__all__ = ["websocket_manager"]
