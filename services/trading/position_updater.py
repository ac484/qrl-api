"""
Position updater encapsulating post-trade updates.
"""
from datetime import datetime
from typing import Dict


class PositionUpdater:
    def __init__(self, cost_repo, position_repo):
        self.cost_repo = cost_repo
        self.position_repo = position_repo

    async def update_after_buy(self, position_data: Dict, quantity: float, price: float):
        await self.cost_repo.update_after_buy(
            buy_price=price, buy_quantity=quantity, buy_amount_usdt=price * quantity
        )
        new_position = {
            "total_qrl": position_data.get("total_qrl", 0) + quantity,
            "average_cost": position_data.get("average_cost", price),
            "last_updated": datetime.now().isoformat(),
        }
        await self.position_repo.set_position(new_position)

    async def update_after_sell(self, position_data: Dict, quantity: float, price: float):
        await self.cost_repo.update_after_sell(
            sell_price=price, sell_quantity=quantity, sell_amount_usdt=price * quantity
        )
        new_position = {
            "total_qrl": position_data.get("total_qrl", 0) - quantity,
            "average_cost": position_data.get("average_cost"),
            "last_updated": datetime.now().isoformat(),
        }
        await self.position_repo.set_position(new_position)
