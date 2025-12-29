"""Account position persistence helpers."""
from typing import Any, Dict

from infrastructure.external.redis_client.client import redis_client


class PositionRepository:
    """Provides access to position data stored in Redis."""

    def __init__(self, client=redis_client):
        self.client = client

    @property
    def connected(self) -> bool:
        return getattr(self.client, "connected", False)

    async def set_position(self, position_data: Dict[str, Any]) -> bool:
        if not self.connected:
            return False
        return await self.client.set_position(position_data)

    async def get_position(self) -> Dict[str, Any]:
        if not self.connected:
            return {}
        return await self.client.get_position()

    async def set_position_layers(self, core_qrl: float, swing_qrl: float, active_qrl: float) -> bool:
        if not self.connected:
            return False
        return await self.client.set_position_layers(core_qrl, swing_qrl, active_qrl)

    async def get_position_layers(self) -> Dict[str, Any]:
        if not self.connected:
            return {}
        return await self.client.get_position_layers()


__all__ = ["PositionRepository"]
