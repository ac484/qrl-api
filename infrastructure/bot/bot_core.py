"""
Trading bot core logic (Async).
"""
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from infrastructure.config.config import config

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
            if not await self._phase_1_startup():
                result["message"] = "Startup phase failed"
                result["execution_log"] = self.execution_log
                return result

            market_data = await self._phase_2_data_collection()
            if not market_data:
                result["message"] = "Data collection phase failed"
                result["execution_log"] = self.execution_log
                return result

            signal = await self._phase_3_strategy(market_data)
            result["phases"]["strategy"] = {"signal": signal}

            risk_check = await self._phase_4_risk_control(signal, market_data)
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
                execution_result = await self._phase_5_execution(signal, market_data, risk_check)
                result["phases"]["execution"] = execution_result
                result["action"] = signal
                result["success"] = execution_result.get("success", False)
            else:
                result["success"] = True
                result["action"] = "HOLD"

            await self._phase_6_cleanup(result)
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

    async def _phase_1_startup(self) -> bool:
        self._log("Phase 1: Startup & Validation")
        if not self.redis.connected:
            self._log("Redis not connected", "error")
            return False
        position = await self.redis.get_position()
        self._log(f"Current position loaded: {len(position)} fields")
        layers = await self.redis.get_position_layers()
        if layers:
            self._log(f"Position layers: core={layers.get('core_qrl', '0')} QRL")
        return True

    async def _phase_2_data_collection(self) -> Optional[Dict[str, Any]]:
        self._log("Phase 2: Data Collection")
        try:
            ticker = await self.mexc.get_ticker_24hr(self.symbol)
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            price_change_pct = float(ticker.get("priceChangePercent", 0))
            self._log(f"Price: {price}, Volume 24h: {volume_24h}, Change: {price_change_pct}%")
            await self.redis.set_latest_price(price, volume_24h)
            await self.redis.add_price_to_history(price)
            price_history = await self.redis.get_price_history(limit=config.MA_LONG_PERIOD)

            qrl_balance = 0
            usdt_balance = 0
            if config.MEXC_API_KEY and config.MEXC_SECRET_KEY:
                try:
                    account_info = await self.mexc.get_account_info()
                    for balance in account_info.get("balances", []):
                        asset = balance.get("asset")
                        if asset == "QRL":
                            qrl_balance = float(balance.get("free", 0))
                        elif asset == "USDT":
                            usdt_balance = float(balance.get("free", 0))
                    self._log(f"Balance: {qrl_balance} QRL, {usdt_balance} USDT")
                    position_data = {"qrl_balance": str(qrl_balance), "usdt_balance": str(usdt_balance)}
                    await self.redis.set_position(position_data)

                    cost_data = await self.redis.get_cost_data()
                    avg_cost = float(cost_data.get("avg_cost", 0)) if cost_data.get("avg_cost") else price
                    total_invested = qrl_balance * avg_cost
                    unrealized_pnl = (price - avg_cost) * qrl_balance if avg_cost > 0 else 0
                    await self.redis.set_cost_data(
                        avg_cost=avg_cost,
                        total_invested=total_invested,
                        unrealized_pnl=unrealized_pnl,
                    )
                except Exception as e:
                    self._log(f"Failed to get account balance: {e}", "warning")

            return {
                "price": price,
                "volume_24h": volume_24h,
                "price_change_pct": price_change_pct,
                "price_history": price_history,
                "qrl_balance": qrl_balance,
                "usdt_balance": usdt_balance,
            }
        except Exception as e:
            self._log(f"Data collection error: {e}", "error")
            return None

    async def _phase_3_strategy(self, market_data: Dict[str, Any]) -> str:
        self._log("Phase 3: Strategy Execution")
        price = market_data.get("price", 0)
        price_history = market_data.get("price_history", [])
        if not price_history or len(price_history) < config.MA_LONG_PERIOD:
            self._log("Insufficient price history for MA calculation", "warning")
            return "HOLD"
        short_ma = sum(price_history[-config.MA_SHORT_PERIOD:]) / config.MA_SHORT_PERIOD
        long_ma = sum(price_history[-config.MA_LONG_PERIOD:]) / config.MA_LONG_PERIOD
        self._log(f"MA Short: {short_ma:.5f}, MA Long: {long_ma:.5f}")
        if short_ma > long_ma * (1 + config.SIGNAL_THRESHOLD):
            return "BUY"
        if short_ma < long_ma * (1 - config.SIGNAL_THRESHOLD):
            return "SELL"
        return "HOLD"

    async def _phase_4_risk_control(self, signal: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        self._log("Phase 4: Risk Control")
        if signal == "HOLD":
            return {"allowed": False, "reason": "No trading signal"}
        if signal == "BUY":
            usdt_balance = market_data.get("usdt_balance", 0)
            if usdt_balance <= 0:
                return {"allowed": False, "reason": "Insufficient USDT"}
        if signal == "SELL":
            qrl_balance = market_data.get("qrl_balance", 0)
            if qrl_balance <= 0:
                return {"allowed": False, "reason": "No QRL to sell"}
        return {"allowed": True, "reason": "Risk checks passed"}

    async def _phase_5_execution(self, signal: str, market_data: Dict[str, Any], risk_check: Dict[str, Any]):
        self._log("Phase 5: Execution")
        price = market_data.get("price", 0)
        quantity = config.BASE_ORDER_USDT / price if signal == "BUY" else market_data.get("qrl_balance", 0)
        if quantity <= 0:
            return {"success": False, "message": "Quantity is zero"}
        if self.dry_run:
            self._log(f"DRY RUN: {signal} {quantity} QRL at {price}")
            return {"success": True, "dry_run": True, "quantity": quantity, "price": price}
        order = await self.mexc.place_market_order(symbol=self.symbol, side=signal, quantity=quantity)
        self._log(f"Order executed: {order}")
        return {"success": True, "order": order, "quantity": quantity, "price": price}

    async def _phase_6_cleanup(self, result: Dict[str, Any]):
        self._log("Phase 6: Cleanup & Reporting")
        result["completed_at"] = datetime.now().isoformat()
