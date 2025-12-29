"""Shared helpers for the QRL/USDT trading bot."""
from typing import List, Optional, Tuple

from infrastructure.utils.type_safety import safe_float

__all__ = [
    "calculate_moving_average",
    "derive_ma_pair",
    "compute_cost_metrics",
]


def calculate_moving_average(prices: List[float], period: int) -> float:
    """Return the moving average of the last *period* prices or 0 when insufficient."""
    if period <= 0 or len(prices) < period:
        return 0.0
    window = prices[-period:]
    return sum(window) / period if window else 0.0


def derive_ma_pair(
    prices: List[float], short_period: int, long_period: int
) -> Optional[Tuple[float, float]]:
    """
    Compute short/long moving averages when history is sufficient.

    Returns None when there is not enough history for the long period.
    """
    if long_period <= 0 or len(prices) < long_period:
        return None
    short_ma = calculate_moving_average(prices, short_period)
    long_ma = calculate_moving_average(prices, long_period)
    return short_ma, long_ma


def compute_cost_metrics(price: float, qrl_balance: float, avg_cost: Optional[float]) -> dict:
    """Derive cost metrics with safe defaults for unrealized PnL calculation."""
    effective_avg_cost = safe_float(avg_cost, price if price is not None else 0.0)
    if effective_avg_cost <= 0:
        return {"avg_cost": 0.0, "total_invested": 0.0, "unrealized_pnl": 0.0}

    total_invested = qrl_balance * effective_avg_cost
    unrealized_pnl = (price - effective_avg_cost) * qrl_balance
    return {
        "avg_cost": effective_avg_cost,
        "total_invested": total_invested,
        "unrealized_pnl": unrealized_pnl,
    }
