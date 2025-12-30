"""Event handler helpers for websocket messages."""
from typing import Any, Callable, Coroutine

MessageHandler = Callable[[Any], Coroutine[Any, Any, None]]

__all__ = ["MessageHandler"]
