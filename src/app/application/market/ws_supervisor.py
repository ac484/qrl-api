"""
WebSocket Supervisor - Reconnection pattern from ✨.md

Implements the reconnection supervisor pattern:
- WS Client is always "killable"
- Automatic reconnection on failure
- Heartbeat monitoring (data flow, not just ping)
- Clean separation: Infrastructure (WS) from Application (supervision)
"""
import asyncio
import logging
from typing import AsyncIterator, Callable, Optional

logger = logging.getLogger(__name__)


class MarketStreamSupervisor:
    """
    Supervises WebSocket connection with automatic reconnection.
    
    From ✨.md Section 6.3:
    - WS Client is always "killable"
    - Heartbeat = "is data flowing"
    - Reconnects automatically on failure
    """

    def __init__(
        self,
        ws_client,
        on_message: Callable,
        reconnect_delay: float = 2.0,
    ):
        """
        Initialize supervisor.
        
        Args:
            ws_client: MEXCWebSocketClient instance
            on_message: Async callback for each message
            reconnect_delay: Seconds to wait before reconnecting
        """
        self.ws_client = ws_client
        self.on_message = on_message
        self.reconnect_delay = reconnect_delay
        self._running = False

    async def run(self) -> None:
        """
        Run supervisor loop with automatic reconnection.
        
        Pattern from ✨.md:
        - Trading system ≠ "always running"
        - Trading system = "ready to run anytime"
        """
        self._running = True
        while self._running:
            try:
                await self._run_once()
            except Exception as e:
                logger.warning(
                    f"WS died, reconnecting in {self.reconnect_delay}s",
                    exc_info=e,
                )
                await asyncio.sleep(self.reconnect_delay)

    async def _run_once(self) -> None:
        """
        Single connection lifecycle.
        
        Raises RuntimeError if heartbeat timeout occurs.
        """
        async with self.ws_client as stream:
            async for raw_message in stream:
                # Process message
                await self.on_message(raw_message)
                
                # Check heartbeat (data flow monitoring)
                if not self.ws_client.is_alive():
                    raise RuntimeError("Heartbeat timeout - no data flowing")

    def stop(self) -> None:
        """Stop the supervisor loop."""
        self._running = False


__all__ = ["MarketStreamSupervisor"]
