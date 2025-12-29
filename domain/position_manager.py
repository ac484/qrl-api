"""Position management logic separated from infrastructure concerns."""
from typing import Any, Dict, Optional

from domain.interfaces import PositionRepositoryProtocol, CostRepositoryProtocol


class PositionManager:
    """Co-ordinates position and cost tracking across repositories."""

    def __init__(
        self,
        position_repo: PositionRepositoryProtocol,
        cost_repo: CostRepositoryProtocol,
    ):
        self.position_repo = position_repo
        self.cost_repo = cost_repo

    async def update_position(self, position_data: Dict[str, Any]) -> bool:
        """Persist position data through the repository."""
        return await self.position_repo.set_position(position_data)

    async def update_layers(
        self, core_qrl: float, swing_qrl: float, active_qrl: float
    ) -> bool:
        """Persist layered position data."""
        return await self.position_repo.set_position_layers(core_qrl, swing_qrl, active_qrl)

    async def snapshot(self) -> Dict[str, Any]:
        """Return a combined snapshot of position and cost data."""
        position = await self.position_repo.get_position()
        layers = await self.position_repo.get_position_layers()
        cost_data = await self.cost_repo.get_cost_data()
        return {
            "position": position,
            "layers": layers,
            "cost": cost_data,
        }

    async def update_costs(
        self, avg_cost: float, total_invested: float, unrealized_pnl: float
    ) -> bool:
        """Persist cost data through the repository."""
        return await self.cost_repo.set_cost_data(avg_cost, total_invested, unrealized_pnl)

    async def get_costs(self) -> Dict[str, Any]:
        """Retrieve stored cost data."""
        return await self.cost_repo.get_cost_data()


__all__ = ["PositionManager"]
