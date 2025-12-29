"""
Trading workflow orchestrator (6-phase) extracted from TradingService.
"""
import logging
from datetime import datetime
from typing import Dict

from services.trading.balance_resolver import BalanceResolver
from services.trading.price_resolver import PriceResolver
from services.trading.position_updater import PositionUpdater

logger = logging.getLogger(__name__)


class TradingWorkflow:
    def __init__(
        self,
        price_resolver: PriceResolver,
        balance_resolver: BalanceResolver,
        position_updater: PositionUpdater,
        position_repo,
        price_repo,
        trade_repo,
        cost_repo,
        trading_strategy,
        risk_manager,
        position_manager,
    ):
        self.price_resolver = price_resolver
        self.balance_resolver = balance_resolver
        self.position_updater = position_updater
        self.position_repo = position_repo
        self.price_repo = price_repo
        self.trade_repo = trade_repo
        self.cost_repo = cost_repo
        self.trading_strategy = trading_strategy
        self.risk_manager = risk_manager
        self.position_manager = position_manager

    async def execute(self, symbol: str = "QRLUSDT") -> Dict:
        # Phase 1: handled by caller (bot status)
        current_price = await self.price_resolver.get_current_price(symbol)
        price_history = await self.price_resolver.get_price_history(current_price)

        prices = [float(p.get("price", current_price)) for p in price_history]
        short_prices = prices[-12:]
        long_prices = prices

        position_data = await self.position_repo.get_position()
        avg_cost = float(position_data.get("average_cost", 0)) if position_data else 0

        signal = self.trading_strategy.generate_signal(
            price=current_price,
            short_prices=short_prices,
            long_prices=long_prices,
            avg_cost=avg_cost,
        )
        if signal == "HOLD":
            return {
                "success": True,
                "action": "HOLD",
                "reason": "No trading signal",
                "current_price": current_price,
                "price": current_price,
                "quantity": 0,
                "timestamp": datetime.now().isoformat(),
            }

        daily_trades = await self.trade_repo.get_daily_trades()
        last_trade_time = await self.trade_repo.get_last_trade_time()
        position_layers = await self.position_repo.get_position_layers()

        usdt_balance = await self.balance_resolver.get_usdt_balance()
        risk_check = self.risk_manager.check_all_risks(
            signal=signal,
            daily_trades=daily_trades,
            last_trade_time=last_trade_time,
            position_layers=position_layers,
            usdt_balance=usdt_balance,
        )
        if not risk_check.get("passed", False):
            return {
                "success": False,
                "action": signal,
                "reason": f"Risk check failed: {risk_check.get('reason')}",
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
            }

        if signal == "BUY":
            quantity_result = self.position_manager.calculate_buy_quantity(
                usdt_balance=usdt_balance, price=current_price
            )
            quantity = quantity_result.get("quantity", 0)
        else:
            total_qrl = float(position_data.get("total_qrl", 0)) if position_data else 0
            core_qrl = float(position_data.get("core_qrl", 0)) if position_data else 0
            quantity_result = self.position_manager.calculate_sell_quantity(
                total_qrl=total_qrl, core_qrl=core_qrl
            )
            quantity = quantity_result.get("quantity", 0)

        if quantity <= 0:
            return {
                "success": False,
                "action": signal,
                "reason": "Insufficient quantity",
                "current_price": current_price,
                "timestamp": datetime.now().isoformat(),
            }

        return {
            "success": True,
            "action": signal,
            "quantity": quantity,
            "price": current_price,
            "timestamp": datetime.now().isoformat(),
        }

    async def finalize_order(self, signal: str, quantity: float, order: Dict, current_price: float, position_data: Dict):
        if signal == "BUY":
            await self.position_updater.update_after_buy(position_data, quantity, current_price)
        else:
            await self.position_updater.update_after_sell(position_data, quantity, current_price)

        await self.trade_repo.increment_daily_trades()
        await self.trade_repo.set_last_trade_time(datetime.now().timestamp())
        await self.trade_repo.add_trade_record(
            {
                "symbol": "QRLUSDT",
                "side": signal,
                "quantity": quantity,
                "price": current_price,
                "timestamp": datetime.now().isoformat(),
                "order_id": order.get("orderId"),
            }
        )
