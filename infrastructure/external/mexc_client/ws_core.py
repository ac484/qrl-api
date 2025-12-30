"""Backward compatible websocket core import."""
import websockets

from infrastructure.external.mexc_client.websocket.client import (
    MEXCWebSocketClient,
    WS_BASE,
)

__all__ = ["MEXCWebSocketClient", "WS_BASE", "websockets"]
