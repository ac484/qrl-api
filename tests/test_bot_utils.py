import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from infrastructure.bot.bot_utils import (
    calculate_moving_average,
    derive_ma_pair,
    compute_cost_metrics,
)


def test_moving_average_basic():
    prices = [1, 2, 3, 4]
    assert calculate_moving_average(prices, 2) == 3.5
    assert calculate_moving_average(prices, 4) == 2.5


def test_moving_average_insufficient_history():
    assert calculate_moving_average([1, 2], 3) == 0.0


def test_derive_ma_pair_and_signal_readiness():
    prices = [1, 2, 3, 4, 5]
    ma_pair = derive_ma_pair(prices, short_period=2, long_period=4)
    assert ma_pair is not None
    short_ma, long_ma = ma_pair
    assert short_ma == 4.5
    assert long_ma == 3.5


def test_cost_metrics_with_and_without_avg_cost():
    metrics = compute_cost_metrics(price=2.0, qrl_balance=5.0, avg_cost=1.0)
    assert metrics["avg_cost"] == 1.0
    assert metrics["total_invested"] == 5.0
    assert metrics["unrealized_pnl"] == 5.0

    metrics_default = compute_cost_metrics(price=2.0, qrl_balance=5.0, avg_cost=None)
    assert metrics_default["avg_cost"] == 2.0
    assert metrics_default["unrealized_pnl"] == 0.0
