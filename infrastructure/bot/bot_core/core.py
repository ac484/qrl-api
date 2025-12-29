"""Trading bot entry orchestrating the six phases."""
import logging
import time
from typing import Dict, Any, List

from infrastructure.bot.bot_core.startup import phase_startup
from infrastructure.bot.bot_core.data_collection import phase_data_collection
from infrastructure.bot.bot_core.strategy import phase_strategy
from infrastructure.bot.bot_core.risk import phase_risk_control
from infrastructure.bot.bot_core.execution import phase_execution
from infrastructure.bot.bot_core.cleanup import phase_cleanup

logger = logging.getLogger(__name__)


class TradingBot:
    """QRL/USDT Trading Bot with MEXC API Integration (Async)."""

    def __init__(self, mexc_client, redis_client, symbol: str, dry_run: bool = False):
        self.mexc = mexc_client
        self.redis = redis_client
        self.symbol = symbol
        self.dry_run = dry_run
        self.execution_log: List[str] = []

    def _log(self, message: str, level: str = "info"):
        self.execution_log.append(f"[{level.upper()}] {message}")
        getattr(logger, level)(message)

    async def execute_cycle(self) -> Dict[str, Any]:
        self._log(f"Starting trading cycle for {self.symbol} (dry_run={self.dry_run})")
        start_time = time.time()
        result = {"success": False, "action": None, "phases": {}, "message": "", "execution_log": []}

        try:
            if not await phase_startup(self):
                result["message"] = "Startup phase failed"
                result["execution_log"] = self.execution_log
                return result

            market_data = await phase_data_collection(self)
            if not market_data:
                result["message"] = "Data collection phase failed"
                result["execution_log"] = self.execution_log
                return result

            signal = await phase_strategy(self, market_data)
            result["phases"]["strategy"] = {"signal": signal}

            risk_check = await phase_risk_control(self, signal, market_data)
            result["phases"]["risk_control"] = risk_check

            if not risk_check["allowed"]:
                result.update(
                    {
                        "success": True,
                        "action": "HOLD",
                        "message": risk_check["reason"],
                        "execution_log": self.execution_log,
                    }
                )
                return result

            if signal in ["BUY", "SELL"]:
                execution_result = await phase_execution(self, signal, market_data, risk_check)
                result["phases"]["execution"] = execution_result
                result["action"] = signal
                result["success"] = execution_result.get("success", False)
            else:
                result["success"] = True
                result["action"] = "HOLD"

            await phase_cleanup(self, result)
            elapsed = time.time() - start_time
            result["message"] = f"Trading cycle completed in {elapsed:.2f}s"
            result["execution_log"] = self.execution_log
            self._log(f"Trading cycle completed: {result['action']}")
            return result
        except Exception as e:
            self._log(f"Trading cycle error: {e}", "error")
            result["message"] = f"Error: {str(e)}"
            result["execution_log"] = self.execution_log
            return result
