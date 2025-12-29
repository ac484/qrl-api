"""Trading service orchestrating bot execution with risk checks."""
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from domain.position_manager import PositionManager
from domain.risk_manager import RiskManager
from domain.trading_strategy import TradingStrategy
from infrastructure.bot.bot_core import TradingBot
from infrastructure.config.config import config
from infrastructure.external.mexc_client.client import mexc_client as default_mexc_client
from infrastructure.external.redis_client.client import redis_client as default_redis_client
from repositories.account.cost_repository import CostRepository
from repositories.account.position_repository import PositionRepository
from repositories.market.price_repository import PriceRepository
from repositories.trade.trade_repository import TradeRepository


class TradingService:
    """Coordinates trading flows with risk management and persistence."""

    def __init__(
        self,
        mexc_client=default_mexc_client,
        redis_client=default_redis_client,
        trade_repository: Optional[TradeRepository] = None,
        price_repository: Optional[PriceRepository] = None,
        position_repository: Optional[PositionRepository] = None,
        cost_repository: Optional[CostRepository] = None,
        risk_manager: Optional[RiskManager] = None,
        strategy: Optional[TradingStrategy] = None,
        bot_factory=TradingBot,
    ):
        self.mexc_client = mexc_client
        self.redis_client = redis_client
        self.trade_repository = trade_repository or TradeRepository(redis_client)
        self.price_repository = price_repository or PriceRepository(redis_client)
        self.position_repository = position_repository or PositionRepository(redis_client)
        self.cost_repository = cost_repository or CostRepository(redis_client)
        self.risk_manager = risk_manager or RiskManager()
        self.strategy = strategy or TradingStrategy()
        self.bot_factory = bot_factory
        self.position_manager = PositionManager(self.position_repository, self.cost_repository)

    async def _evaluate_risk(self) -> Dict[str, Any]:
        daily_trades = 0
        last_trade_time = None

        if hasattr(self.trade_repository, "get_daily_trades"):
            daily_trades = await self.trade_repository.get_daily_trades()
        if hasattr(self.trade_repository, "get_last_trade_time"):
            last_trade_time = await self.trade_repository.get_last_trade_time()

        return self.risk_manager.evaluate(daily_trades, last_trade_time)

    async def execute(self, dry_run: bool = False) -> Dict[str, Any]:
        """Execute a trading cycle with a risk pre-check."""
        risk = await self._evaluate_risk()
        if not risk.get("allowed", False):
            return {
                "success": True,
                "action": "HOLD",
                "message": risk.get("reason", "Risk check failed"),
                "phases": {"risk": risk},
            }

        bot = self.bot_factory(
            mexc_client=self.mexc_client,
            redis_client=self.redis_client,
            symbol=config.TRADING_SYMBOL,
            dry_run=dry_run,
        )

        result = await bot.execute_cycle()

        if result.get("action") in {"BUY", "SELL"}:
            if hasattr(self.trade_repository, "increment_daily_trades"):
                await self.trade_repository.increment_daily_trades()
            if hasattr(self.trade_repository, "set_last_trade_time"):
                await self.trade_repository.set_last_trade_time(
                    int(datetime.now(timezone.utc).timestamp())
                )

        return result


__all__ = ["TradingService"]
