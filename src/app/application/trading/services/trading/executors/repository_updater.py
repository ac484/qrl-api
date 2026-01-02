"""Repository Updater - Persist trade results (Infrastructure layer)"""
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class RepositoryUpdater:
    """Update repositories after trade execution"""

    def __init__(self, position_repo, trade_repo, cost_repo):
        self.position_repo = position_repo
        self.trade_repo = trade_repo
        self.cost_repo = cost_repo

    async def update_after_trade(self, signal: str, qty: float, price: float, order: Dict, symbol: str):
        """Update all repositories after successful trade"""
        await self._update_trade_stats(signal, qty, price, order, symbol)
        await self._update_position_and_cost(signal, qty, price)

    async def _update_trade_stats(self, signal: str, qty: float, price: float, order: Dict, symbol: str):
        """Update trade statistics"""
        await self.trade_repo.increment_daily_trades()
        await self.trade_repo.set_last_trade_time(datetime.now().timestamp())
        await self.trade_repo.add_trade_record({
            "symbol": symbol, "side": signal, "quantity": qty, "price": price,
            "timestamp": datetime.now().isoformat(), "order_id": order.get("orderId")
        })

    async def _update_position_and_cost(self, signal: str, qty: float, price: float):
        """Update position and cost basis"""
        pos = await self.position_repo.get_position()
        
        if signal == "BUY":
            cost_data = await self.cost_repo.update_after_buy(qty, price)
            await self.position_repo.set_position({
                "total_qrl": pos.get("total_qrl", 0) + qty,
                "average_cost": cost_data.get("new_average_cost"),
                "last_updated": datetime.now().isoformat()
            })
        else:
            await self.cost_repo.update_after_sell(qty, price)
            await self.position_repo.set_position({
                "total_qrl": pos.get("total_qrl", 0) - qty,
                "average_cost": pos.get("average_cost"),
                "last_updated": datetime.now().isoformat()
            })
