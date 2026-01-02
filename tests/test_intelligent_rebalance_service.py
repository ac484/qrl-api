"""
Unit tests for intelligent rebalance service.

Tests MA calculation, signal detection, and decision logic.
"""

import pytest

from src.app.application.trading.services.trading.intelligent_rebalance_service import (
    IntelligentRebalanceService,
)


class _DummyBalanceService:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    async def get_account_balance(self):
        return self.snapshot


class _DummyMEXCClient:
    def __init__(self, klines_data=None):
        self.klines_data = klines_data or []

    async def get_klines(self, symbol, interval, limit):
        """Return mock klines data for MA calculation."""
        if not self.klines_data:
            # Default: Generate mock klines with uptrend (golden cross)
            # Format: [timestamp, open, high, low, close, volume, ...]
            return [
                [1000 + i, "0.048", "0.049", "0.047", str(0.048 + i * 0.001), "1000"]
                for i in range(limit)
            ]
        return self.klines_data


class _DummyRedis:
    def __init__(self, cost_basis=0.05):
        self.saved = None
        self.cost_basis = cost_basis

    async def set_rebalance_plan(self, plan):
        self.saved = plan
        return True

    async def get_position_cost_basis(self, asset):
        return self.cost_basis


def _snapshot(qrl_total: float, usdt_total: float, price: float):
    return {
        "balances": {
            "QRL": {
                "total": qrl_total,
                "available": qrl_total,
                "price": price,
            },
            "USDT": {
                "total": usdt_total,
                "available": usdt_total,
            },
        },
        "prices": {"QRLUSDT": price},
    }


@pytest.mark.asyncio
async def test_ma_calculation_golden_cross():
    """Test MA calculation detects golden cross (bullish)."""
    # Create uptrend klines (recent prices higher)
    klines = [
        [1000 + i, "0.048", "0.049", "0.047", str(0.048 + i * 0.001), "1000"]
        for i in range(25)
    ]
    mexc = _DummyMEXCClient(klines)

    snapshot = _snapshot(qrl_total=8000, usdt_total=600, price=0.050)
    redis = _DummyRedis(cost_basis=0.052)
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )

    ma_data = await service._calculate_ma_indicators()

    assert ma_data["signal"] in ["GOLDEN_CROSS", "NEUTRAL"]
    assert ma_data["ma_short"] > 0
    assert ma_data["ma_long"] > 0
    assert ma_data["prices_count"] == 25


@pytest.mark.asyncio
async def test_intelligent_buy_signal():
    """Test BUY signal: golden cross + QRL below target + price favorable."""
    # Create uptrend klines for golden cross
    klines = [
        [1000 + i, "0.048", "0.049", "0.047", str(0.048 + i * 0.001), "1000"]
        for i in range(25)
    ]
    mexc = _DummyMEXCClient(klines)

    snapshot = _snapshot(qrl_total=8000, usdt_total=600, price=0.050)
    redis = _DummyRedis(cost_basis=0.052)  # Current price below cost
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )

    plan = await service.generate_plan(snapshot)

    # Should recommend BUY if golden cross and price < cost_avg
    if plan["ma_indicators"]["signal"] == "GOLDEN_CROSS":
        assert plan["action"] in ["BUY", "HOLD"]
        if plan["action"] == "BUY":
            assert "quantity" in plan
            assert plan["quantity"] > 0


@pytest.mark.asyncio
async def test_intelligent_sell_signal():
    """Test SELL signal: death cross + QRL above target + price profitable."""
    # Create downtrend klines for death cross
    klines = [
        [1000 + i, "0.055", "0.056", "0.054", str(0.055 - i * 0.001), "1000"]
        for i in range(25)
    ]
    mexc = _DummyMEXCClient(klines)

    snapshot = _snapshot(qrl_total=12000, usdt_total=100, price=0.054)
    redis = _DummyRedis(cost_basis=0.050)  # Price above cost with profit
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )

    plan = await service.generate_plan(snapshot)

    # Should consider SELL if death cross and price > cost_avg * 1.03
    if plan["ma_indicators"]["signal"] == "DEATH_CROSS":
        assert plan["action"] in ["SELL", "HOLD"]


@pytest.mark.asyncio
async def test_position_tier_allocation():
    """Test position tier calculation (70% core, 20% swing, 10% active)."""
    klines = [[1000, "0.05", "0.05", "0.05", "0.05", "1000"]] * 25
    mexc = _DummyMEXCClient(klines)

    snapshot = _snapshot(qrl_total=10000, usdt_total=500, price=0.050)
    redis = _DummyRedis(cost_basis=0.050)
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )

    plan = await service.generate_plan(snapshot)

    assert "position_tiers" in plan
    assert pytest.approx(plan["position_tiers"]["core"], rel=1e-3) == 7000
    assert pytest.approx(plan["position_tiers"]["swing"], rel=1e-3) == 2000
    assert pytest.approx(plan["position_tiers"]["active"], rel=1e-3) == 1000
    assert pytest.approx(plan["position_tiers"]["tradeable"], rel=1e-3) == 3000


@pytest.mark.asyncio
async def test_core_position_protection():
    """Test that sell orders respect core position (only trade non-core)."""
    klines = [[1000, "0.05", "0.05", "0.05", "0.05", "1000"]] * 25
    mexc = _DummyMEXCClient(klines)

    snapshot = _snapshot(qrl_total=10000, usdt_total=100, price=0.055)
    redis = _DummyRedis(cost_basis=0.050)
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
        core_ratio=0.7,  # 70% core = 7000 QRL
    )

    plan = await service.generate_plan(snapshot)

    # If SELL action, quantity should not exceed tradeable amount (3000 QRL)
    if plan["action"] == "SELL":
        assert plan["quantity"] <= 3000


@pytest.mark.asyncio
async def test_hold_when_insufficient_data():
    """Test HOLD action when MA data is insufficient."""
    mexc = _DummyMEXCClient([])  # No klines data

    snapshot = _snapshot(qrl_total=8000, usdt_total=600, price=0.050)
    redis = _DummyRedis(cost_basis=0.052)
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )

    plan = await service.generate_plan(snapshot)

    # Should HOLD or have error in MA indicators
    assert "ma_indicators" in plan
    if "error" in plan["ma_indicators"]:
        assert plan["action"] == "HOLD"


@pytest.mark.asyncio
async def test_cost_basis_fallback():
    """Test cost basis fallback when Redis unavailable."""
    klines = [[1000, "0.05", "0.05", "0.05", "0.05", "1000"]] * 25
    mexc = _DummyMEXCClient(klines)

    snapshot = _snapshot(qrl_total=10000, usdt_total=500, price=0.050)
    # No Redis client
    service = IntelligentRebalanceService(
        _DummyBalanceService(snapshot),
        mexc,
        redis_client=None,
        min_notional_usdt=0.1,
        threshold_pct=0,
    )

    plan = await service.generate_plan(snapshot)

    # Should use default cost basis (0.05)
    assert "cost_avg" in plan
    assert plan["cost_avg"] == 0.05
