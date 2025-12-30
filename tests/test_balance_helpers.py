import pytest
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from infrastructure.external.mexc_client.account import build_balance_map
from services.account import BalanceService


class FakeMexcClient:
    def __init__(self, snapshot: dict | None, fail: bool = False):
        self.snapshot = snapshot
        self.fail = fail

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_balance_snapshot(self, symbol: str = "QRLUSDT"):
        if self.fail:
            raise RuntimeError("fail")
        return self.snapshot


class FakeRedis:
    def __init__(self):
        self.storage = {}

    @property
    def client(self):  # needed for mixin guard
        return True

    async def set_cached_account_balance(self, balance_data, ttl=45):
        self.storage["cache"] = balance_data
        return True

    async def get_cached_account_balance(self):
        return self.storage.get("cache")

    async def set_mexc_account_balance(self, balance_data):
        self.storage["mexc_balance"] = balance_data
        return True

    async def set_mexc_qrl_price(self, price, price_data=None):
        self.storage["price"] = price
        return True


def test_build_balance_map_totals():
    data = {
        "balances": [
            {"asset": "QRL", "free": "1", "locked": "2"},
            {"asset": "USDT", "free": "3", "locked": "0"},
        ]
    }
    balances = build_balance_map(data)
    assert balances["QRL"]["total"] == 3
    assert balances["USDT"]["total"] == 3


@pytest.mark.asyncio
async def test_balance_service_cache_fallback():
    cached = {
        "balances": {
            "QRL": {"free": "1", "locked": "0", "total": 1, "price": 1.0},
            "USDT": {"free": "5", "locked": "0", "total": 5},
        }
    }
    redis_client = FakeRedis()
    await redis_client.set_cached_account_balance(cached)
    service = BalanceService(FakeMexcClient(snapshot=None, fail=True), redis_client)

    result = await service.get_account_balance()
    assert result["source"] == "cache"
    assert result["balances"]["USDT"]["free"] == "5"


def test_to_usd_values_no_price():
    snapshot = {
        "balances": {
            "QRL": {"free": "0", "locked": "0", "total": 0},
            "USDT": {"free": "0", "locked": "0", "total": 0},
        },
        "prices": {},
    }
    out = BalanceService.to_usd_values(snapshot)
    assert out["balances"]["QRL"]["total"] == 0
