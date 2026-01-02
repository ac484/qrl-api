"""
Intelligent rebalance service with MA signals and position tiers.

Implements the strategy documented in:
- docs/INTELLIGENT_REBALANCE_FORMULAS.md
- docs/INTELLIGENT_REBALANCE_EXECUTION_GUIDE.md

Key features:
- MA (Moving Average) cross signal detection (MA_7 vs MA_25)
- Position tier management (70% core, 20% swing, 10% active)
- Cost basis tracking
- Enhanced decision logic (symmetric + MA + cost basis)
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from src.app.infrastructure.external import QRL_USDT_SYMBOL
from src.app.infrastructure.utils import safe_float

# Import extracted modules
from ..indicators import MACalculator
from ..position import CostTracker


class IntelligentRebalanceService:
    """
    Intelligent rebalance planner with MA signals and position management.

    Extends symmetric rebalance with:
    - MA cross signals (golden cross/death cross)
    - Cost basis validation (buy low, sell high)
    - Position tier allocation (core 70%, swing 20%, active 10%)
    """

    def __init__(
        self,
        balance_service,
        mexc_client,
        redis_client=None,
        target_ratio: float = 0.5,
        min_notional_usdt: float = 5.0,
        threshold_pct: float = 0.01,
        core_ratio: float = 0.7,
        swing_ratio: float = 0.2,
        active_ratio: float = 0.1,
        ma_short_period: int = 7,
        ma_long_period: int = 25,
    ) -> None:
        self.balance_service = balance_service
        self.mexc = mexc_client
        self.redis = redis_client
        self.target_ratio = target_ratio
        self.min_notional_usdt = min_notional_usdt
        self.threshold_pct = threshold_pct
        self.core_ratio = core_ratio
        self.swing_ratio = swing_ratio
        self.active_ratio = active_ratio
        self.ma_short_period = ma_short_period
        self.ma_long_period = ma_long_period
        
        # Initialize extracted components
        self.ma_calculator = MACalculator(ma_short_period, ma_long_period)
        self.cost_tracker = CostTracker(redis_client, default_cost=0.05)

    async def generate_plan(
        self, snapshot: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Build an intelligent rebalance plan based on live or provided balances.

        Steps:
        1. Get account balance snapshot
        2. Calculate MA indicators
        3. Detect trading signals
        4. Compute rebalance plan
        5. Validate against risk rules
        6. Record plan to Redis
        """
        # Step 1: Get balance snapshot
        snapshot = snapshot or await self.balance_service.get_account_balance()

        # Step 2: Calculate MA indicators
        ma_data = await self._calculate_ma_indicators()

        # Step 3: Compute plan with MA signals
        plan = await self.compute_plan(snapshot, ma_data)

        # Step 4: Record plan
        await self._record_plan(plan)

        return plan

    async def _calculate_ma_indicators(self) -> Dict[str, Any]:
        """
        Calculate MA_7 and MA_25 from recent price data.

        Uses MEXC klines API to get historical prices and delegates
        calculation to MACalculator component.
        
        Returns MA values and signal strength.
        """
        try:
            # Get recent klines for MA calculation
            klines = await self.mexc.get_klines(
                symbol=QRL_USDT_SYMBOL,
                interval="5m",  # 5-minute candles
                limit=self.ma_long_period,
            )

            # Delegate MA calculation to extracted component
            return await self.ma_calculator.calculate_from_klines(
                klines, self.mexc, QRL_USDT_SYMBOL
            )

        except Exception as e:
            return {
                "ma_short": 0.0,
                "ma_long": 0.0,
                "signal": "ERROR",
                "signal_strength": 0.0,
                "error": str(e),
            }

    async def compute_plan(
        self, snapshot: Dict[str, Any], ma_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute intelligent rebalance plan with MA signals and cost basis.

        Decision logic:
        - BUY: Golden cross + price <= cost_avg
        - SELL: Death cross + price >= cost_avg * 1.03
        - HOLD: Otherwise
        """
        qrl_data = snapshot.get("balances", {}).get("QRL", {})
        usdt_data = snapshot.get("balances", {}).get("USDT", {})
        price_entry = snapshot.get("prices", {}).get(QRL_USDT_SYMBOL)
        price = safe_float(price_entry or qrl_data.get("price"))

        qrl_total = safe_float(qrl_data.get("total", 0))
        qrl_available = safe_float(qrl_data.get("available", 0))
        usdt_total = safe_float(usdt_data.get("total", 0))
        usdt_available = safe_float(usdt_data.get("available", 0))

        # Get cost basis from Redis or estimate
        cost_avg = await self._get_cost_basis(qrl_total)

        # Calculate position tiers
        qrl_core = qrl_total * self.core_ratio
        qrl_swing = qrl_total * self.swing_ratio
        qrl_active = qrl_total * self.active_ratio
        qrl_tradeable = qrl_total - qrl_core  # swing + active

        # Calculate values for symmetric rebalance
        total_value = qrl_total * price + usdt_total
        target_value = total_value * self.target_ratio
        qrl_value = qrl_total * price
        delta = qrl_value - target_value
        notional = abs(delta)
        quantity = notional / price if price > 0 else 0

        # Build base plan
        plan: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "price": price,
            "cost_avg": cost_avg,
            "qrl_balance": qrl_total,
            "qrl_available": qrl_available,
            "usdt_balance": usdt_total,
            "usdt_available": usdt_available,
            "qrl_value_usdt": qrl_value,
            "usdt_value_usdt": usdt_total,
            "total_value_usdt": total_value,
            "target_value_usdt": target_value,
            "target_ratio": self.target_ratio,
            "quantity": quantity,
            "notional_usdt": notional,
            "position_tiers": {
                "core": qrl_core,
                "swing": qrl_swing,
                "active": qrl_active,
                "tradeable": qrl_tradeable,
            },
            "ma_indicators": ma_data,
        }

        # Check basic preconditions
        if price <= 0 or total_value <= 0:
            plan.update({"action": "HOLD", "reason": "Insufficient price or balance"})
            return plan

        if notional < self.min_notional_usdt or (
            total_value > 0 and (notional / total_value) < self.threshold_pct
        ):
            plan.update({"action": "HOLD", "reason": "Within threshold"})
            return plan

        # Intelligent decision based on MA signals and cost basis
        signal = ma_data.get("signal", "UNKNOWN")
        ma_short = ma_data.get("ma_short", 0)
        ma_long = ma_data.get("ma_long", 0)

        # BUY signal: Golden cross + price at or below cost
        if signal == "GOLDEN_CROSS" and price <= cost_avg * 1.00:
            # QRL below target - good time to buy
            if delta < 0:
                buy_qty = min(quantity, usdt_available / price if price > 0 else 0)
                if buy_qty <= 0:
                    plan.update({"action": "HOLD", "reason": "Insufficient USDT"})
                    return plan

                plan.update(
                    {
                        "action": "BUY",
                        "reason": "Golden cross + QRL below target + price favorable",
                        "quantity": buy_qty,
                        "notional_usdt": buy_qty * price,
                        "signal_validation": {
                            "ma_short": ma_short,
                            "ma_long": ma_long,
                            "price_vs_cost": (
                                (price - cost_avg) / cost_avg * 100
                                if cost_avg > 0
                                else 0
                            ),
                        },
                    }
                )
                return plan

        # SELL signal: Death cross + price above cost with profit
        elif signal == "DEATH_CROSS" and price >= cost_avg * 1.03:
            # QRL above target - good time to sell
            if delta > 0:
                # Limit sell to tradeable positions only (respect core holding)
                sell_qty = min(quantity, qrl_tradeable, qrl_available)
                if sell_qty <= 0:
                    plan.update(
                        {
                            "action": "HOLD",
                            "reason": "No tradeable QRL (core protected)",
                        }
                    )
                    return plan

                plan.update(
                    {
                        "action": "SELL",
                        "reason": "Death cross + QRL above target + price profitable",
                        "quantity": sell_qty,
                        "notional_usdt": sell_qty * price,
                        "signal_validation": {
                            "ma_short": ma_short,
                            "ma_long": ma_long,
                            "price_vs_cost": (
                                (price - cost_avg) / cost_avg * 100
                                if cost_avg > 0
                                else 0
                            ),
                            "profit_margin": (
                                ((price - cost_avg) / cost_avg * 100)
                                if cost_avg > 0
                                else 0
                            ),
                        },
                    }
                )
                return plan

        # No clear signal - HOLD
        plan.update(
            {
                "action": "HOLD",
                "reason": f"No clear signal (MA: {signal}, price vs cost: {((price - cost_avg) / cost_avg * 100):.2f}%)",
            }
        )
        return plan

    async def _get_cost_basis(self, qrl_total: float) -> float:
        """
        Get current QRL cost basis from Redis or estimate from position data.

        Delegates to CostTracker component for cost basis retrieval.
        """
        return await self.cost_tracker.get_cost_basis("QRL", qrl_total)

    async def _record_plan(self, plan: Dict[str, Any]) -> None:
        """Record plan to Redis for audit and monitoring."""
        if not self.redis or not hasattr(self.redis, "set_rebalance_plan"):
            return
        try:
            await self.redis.set_rebalance_plan(plan)
        except Exception:
            # Best-effort logging only
            pass


__all__ = ["IntelligentRebalanceService"]
