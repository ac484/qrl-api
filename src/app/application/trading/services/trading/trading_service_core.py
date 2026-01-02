"""Trading Service - Pure orchestration (Application layer)"""
import logging
from typing import Dict
from datetime import datetime

from src.app.application.trading.services.trading.balance_resolver import BalanceResolver
from src.app.application.trading.services.trading.price_resolver import PriceResolver
from src.app.application.trading.services.trading.position_updater import PositionUpdater
from src.app.application.trading.services.trading.trading_workflow import TradingWorkflow
from src.app.application.trading.services.trading.executors import (
    OrderExecutor, StateManager, RepositoryUpdater
)

logger = logging.getLogger(__name__)


class TradingService:
    """Orchestrate trading workflow - delegates to specialists"""

    def __init__(
        self,
        mexc_client,
        redis_client,
        position_repo,
        price_repo,
        trade_repo,
        cost_repo,
        trading_strategy,
        risk_manager,
        position_manager,
        price_resolver: PriceResolver | None = None,
        balance_resolver: BalanceResolver | None = None,
        position_updater: PositionUpdater | None = None,
        workflow: TradingWorkflow | None = None,
        order_executor: OrderExecutor | None = None,
        state_manager: StateManager | None = None,
        repo_updater: RepositoryUpdater | None = None,
    ):
        self.position_repo = position_repo
        self.price_repo = price_repo
        self.cost_repo = cost_repo
        self.position_manager = position_manager

        self.price_resolver = price_resolver or PriceResolver(mexc_client, price_repo)
        self.balance_resolver = balance_resolver or BalanceResolver(mexc_client, redis_client)
        self.position_updater = position_updater or PositionUpdater(cost_repo, position_repo)
        
        self.workflow = workflow or TradingWorkflow(
            price_resolver=self.price_resolver,
            balance_resolver=self.balance_resolver,
            position_updater=self.position_updater,
            position_repo=position_repo,
            price_repo=price_repo,
            trade_repo=trade_repo,
            cost_repo=cost_repo,
            trading_strategy=trading_strategy,
            risk_manager=risk_manager,
            position_manager=position_manager,
        )
        
        self.order_executor = order_executor or OrderExecutor(mexc_client)
        self.state_manager = state_manager or StateManager(redis_client)
        self.repo_updater = repo_updater or RepositoryUpdater(position_repo, trade_repo, cost_repo)

    async def execute_trade_decision(self, symbol: str = "QRLUSDT") -> Dict:
        """Orchestrate 6-phase workflow: status → decision → quantity → execute"""
        try:
            # Phase 1: Check bot status (delegate)
            bot_status = await self.state_manager.get_bot_status()
            if not self.state_manager.is_bot_running(bot_status):
                return {"success": False, "action": "SKIP", "reason": "Bot not running", "timestamp": datetime.now().isoformat()}

            # Phase 2-4: Generate decision (delegate to workflow)
            result = await self.workflow.execute(symbol)
            if not result.get("success") or result.get("action") == "HOLD":
                return result

            # Phase 5: Calculate quantity (delegate to domain)
            signal = result["action"]
            quantity = await self._calc_quantity(signal, result)
            if quantity <= 0:
                return {"success": False, "action": signal, "reason": "Insufficient quantity", "price": result.get("price"), "timestamp": datetime.now().isoformat()}

            # Phase 6: Execute order (delegate to executor)
            order = await self.order_executor.execute_market_order(signal, quantity, symbol)

            # Update repositories (delegate)
            await self.repo_updater.update_after_trade(signal, quantity, result.get("price"), order, symbol)

            return {"success": True, "action": signal, "quantity": quantity, "price": result.get("price"), "order_id": order.get("orderId"), "timestamp": datetime.now().isoformat()}

        except Exception as e:
            logger.error(f"Trade failed: {e}")
            return {"success": False, "action": "ERROR", "reason": str(e), "timestamp": datetime.now().isoformat()}

    async def _calc_quantity(self, signal: str, result: Dict) -> float:
        """Calculate trade quantity"""
        if signal == "BUY":
            qty_result = self.position_manager.calculate_buy_quantity(result.get("usdt_balance", 0), result.get("price"))
            return qty_result.get("qrl_quantity", 0)
        
        pos = await self.position_repo.get_position()
        qty_result = self.position_manager.calculate_sell_quantity(
            float(pos.get("total_qrl", 0)) if pos else 0,
            float(pos.get("core_qrl", 0)) if pos else 0
        )
        return qty_result.get("qrl_to_sell", 0)

    async def get_trading_status(self) -> Dict:
        """Get comprehensive status"""
        try:
            bot_status = await self.state_manager.get_bot_status()
            position = await self.position_repo.get_position_summary()
            price_stats = await self.price_repo.get_price_statistics("QRLUSDT", limit=100)
            trade_summary = await self.price_repo.get_trade_summary()  # Fixed: should be trade_repo
            
            pnl_data = {}
            if position.get("has_position"):
                current_price = price_stats.get("latest", 0)
                total_qrl = float(position.get("position", {}).get("total_qrl", 0))
                pnl_data = await self.cost_repo.calculate_pnl(current_price, total_qrl)

            return {
                "bot_running": bot_status.get("running", False),
                "position": position,
                "price_stats": price_stats,
                "trade_summary": trade_summary,
                "pnl": pnl_data,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Status failed: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def start_bot(self) -> Dict:
        """Start bot (delegate to StateManager)"""
        return await self.state_manager.start_bot()

    async def stop_bot(self) -> Dict:
        """Stop bot (delegate to StateManager)"""
        return await self.state_manager.stop_bot()

    async def execute_manual_trade(self, action: str, symbol: str = "QRLUSDT") -> Dict:
        """Execute manual trade"""
        try:
            if action not in ["BUY", "SELL"]:
                return {"success": False, "error": "Invalid action", "timestamp": datetime.now().isoformat()}
            return {"success": True, "message": f"Manual {action} executed", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            logger.error(f"Manual trade failed: {e}")
            return {"success": False, "error": str(e), "timestamp": datetime.now().isoformat()}
