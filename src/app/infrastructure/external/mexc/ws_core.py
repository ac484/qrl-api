"""Compatibility wrapper for websocket core helpers."""
from src.app.infrastructure.external.mexc.ws.ws_core import (
    MEXCWebSocketClient,
    WS_BASE,
    websockets,
)

__all__ = ["MEXCWebSocketClient", "WS_BASE", "websockets"]
