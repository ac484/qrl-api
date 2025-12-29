"""Position layers repository mixin."""
from datetime import datetime
from typing import Dict

from infrastructure.config.config import config


class PositionLayersRepoMixin:
    @property
    def _redis_client(self):
        return getattr(self, "client", None)

    async def set_position_layers(self, core_qrl: float, swing_qrl: float, active_qrl: float) -> bool:
        client = self._redis_client
        if not client:
            return False
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position:layers"
            total_qrl = core_qrl + swing_qrl + active_qrl
            core_pct = core_qrl / total_qrl if total_qrl > 0 else 0
            layers = {
                "core_qrl": str(core_qrl),
                "swing_qrl": str(swing_qrl),
                "active_qrl": str(active_qrl),
                "total_qrl": str(total_qrl),
                "core_percent": str(core_pct),
                "last_adjust": datetime.now().isoformat(),
            }
            await client.hset(key, mapping=layers)
            return True
        except Exception:
            return False

    async def get_position_layers(self) -> Dict[str, str]:
        client = self._redis_client
        if not client:
            return {}
        try:
            key = f"bot:{config.TRADING_SYMBOL}:position:layers"
            return await client.hgetall(key)
        except Exception:
            return {}
