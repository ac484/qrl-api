"""
Cost Repository - Data access for cost tracking and P&L
Handles average cost, invested amounts, and profit/loss tracking
"""
from typing import Dict, Optional
import logging

from repositories.account.cost_calculator import (
    summarize_cost_data,
    update_after_buy_values,
    update_after_sell_values,
)

logger = logging.getLogger(__name__)


class CostRepository:
    """
    Repository for cost and P&L data storage and retrieval
    Wraps Redis client for cost-specific operations
    """

    def __init__(self, redis_client):
        self.redis = redis_client

    async def set_cost_data(
        self,
        avg_cost: float,
        total_invested: float,
        unrealized_pnl: float = 0,
        realized_pnl: float = 0,
    ) -> bool:
        return await self.redis.set_cost_data(
            avg_cost, total_invested, unrealized_pnl, realized_pnl
        )

    async def get_cost_data(self) -> Optional[Dict[str, str]]:
        return await self.redis.get_cost_data()

    async def calculate_pnl(self, current_price: float, current_quantity: float) -> Dict[str, float]:
        cost_data = await self.get_cost_data()
        if not cost_data:
            return {
                "avg_cost": 0,
                "current_value": 0,
                "total_invested": 0,
                "unrealized_pnl": 0,
                "unrealized_pnl_percent": 0,
                "realized_pnl": 0,
                "total_pnl": 0,
            }
        return summarize_cost_data(cost_data, current_price, current_quantity)

    async def update_after_buy(
        self, buy_price: float, buy_quantity: float, buy_amount_usdt: float
    ) -> bool:
        cost_data = await self.get_cost_data()
        if not cost_data:
            return await self.set_cost_data(
                avg_cost=buy_price,
                total_invested=buy_amount_usdt,
                unrealized_pnl=0,
                realized_pnl=0,
            )

        try:
            values = update_after_buy_values(cost_data, buy_price, buy_amount_usdt)
            return await self.set_cost_data(
                avg_cost=values["avg_cost"],
                total_invested=values["total_invested"],
                unrealized_pnl=0,
                realized_pnl=values["realized_pnl"],
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Failed to update cost after buy: {exc}")
            return False

    async def update_after_sell(
        self, sell_price: float, sell_quantity: float, sell_amount_usdt: float
    ) -> bool:
        cost_data = await self.get_cost_data()
        if not cost_data:
            logger.warning("No cost data found for sell update")
            return False

        try:
            avg_cost = float(cost_data.get("avg_cost", 0))
            values = update_after_sell_values(
                cost_data, avg_cost, sell_quantity, sell_amount_usdt
            )
            return await self.set_cost_data(
                avg_cost=values["avg_cost"],
                total_invested=values["total_invested"],
                unrealized_pnl=0,
                realized_pnl=values["realized_pnl"],
            )
        except Exception as exc:  # pragma: no cover - defensive
            logger.error(f"Failed to update cost after sell: {exc}")
            return False
