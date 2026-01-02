"""
Cost basis tracking for trading positions.

Retrieves and manages cost basis data for position tracking and profitability analysis.
"""

from typing import Optional

from src.app.infrastructure.utils import safe_float


class CostTracker:
    """
    Track and retrieve cost basis for trading positions.

    Provides cost basis data from Redis cache or returns default estimates
    when no stored data is available.
    """

    def __init__(self, redis_client=None, default_cost: float = 0.05) -> None:
        """
        Initialize cost tracker.

        Args:
            redis_client: Redis client for cost basis storage
            default_cost: Default cost estimate when no data available
        """
        self.redis = redis_client
        self.default_cost = default_cost

    async def get_cost_basis(self, symbol: str, quantity: float = 0) -> float:
        """
        Get cost basis for a symbol from Redis or return default.

        Args:
            symbol: Trading symbol (e.g., "QRL")
            quantity: Position quantity (unused, for future use)

        Returns:
            Cost basis as float, or default if not found
        """
        if not self.redis:
            return self.default_cost

        try:
            # Try to get stored cost basis
            if hasattr(self.redis, "get_position_cost_basis"):
                cost_basis = await self.redis.get_position_cost_basis(symbol)
                if cost_basis:
                    return safe_float(cost_basis)

            # Fallback to default estimate
            return self.default_cost

        except Exception:
            return self.default_cost  # Fallback on error


__all__ = ["CostTracker"]
