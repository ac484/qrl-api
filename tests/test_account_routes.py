import sys
from pathlib import Path

import pytest
from fastapi import HTTPException
from types import SimpleNamespace

# Ensure project root is on sys.path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.app.interfaces.http import account as account_routes
import importlib
from src.app.infrastructure.external.mexc.account import fetch_balance_snapshot

mexc_module = importlib.import_module("src.app.infrastructure.external.mexc")


class DummyMexcClient:
    def __init__(self) -> None:
        self.account_called = False
        self.price_called = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_account_info(self):
        self.account_called = True
        return {
            "balances": [
                {"asset": "QRL", "free": "2", "locked": "3"},
                {"asset": "USDT", "free": "5", "locked": "1"},
            ],
            "accountType": "SPOT",
            "canTrade": True,
        }

    async def get_ticker_price(self, symbol: str):
        self.price_called = True
        return {"symbol": symbol, "price": "0.5"}

    async def get_balance_snapshot(self):
        return await fetch_balance_snapshot(self)


class DummyMexcClientMissingPrice(DummyMexcClient):
    async def get_ticker_price(self, symbol: str):
        self.price_called = True
        return {"symbol": symbol, "price": None}


class DummyMexcWithSettings:
    def __init__(self, api_key=None, secret_key=None):
        self.settings = SimpleNamespace(api_key=api_key, secret_key=secret_key)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False


class DummyRedis:
    def __init__(self, cached=None):
        self.connected = True
        self.cached = cached or {}
        self.saved = None

    async def connect(self):
        self.connected = True
        return True

    async def get_mexc_raw_response(self, endpoint):
        return self.cached

    async def set_mexc_raw_response(self, endpoint, payload):
        self.saved = payload
        return True


@pytest.mark.asyncio
async def test_balance_includes_qrl_value(monkeypatch):
    dummy_client = DummyMexcClient()
    import src.app.infrastructure.external as external

    monkeypatch.setattr(external, "mexc_client", dummy_client)
    monkeypatch.setattr(external, "redis_client", DummyRedis())

    result = await account_routes.get_account_balance()

    assert dummy_client.account_called is True
    assert dummy_client.price_called is True
    assert result["balances"]["QRL"]["total"] == 5.0
    assert result["balances"]["QRL"]["value_usdt"] == pytest.approx(2.5)
    assert result["prices"]["QRLUSDT"] == 0.5
    assert result["balances"]["USDT"]["total"] == 6.0


@pytest.mark.asyncio
async def test_balance_requires_price(monkeypatch):
    dummy_client = DummyMexcClientMissingPrice()
    import src.app.infrastructure.external as external

    monkeypatch.setattr(external, "mexc_client", dummy_client)
    monkeypatch.setattr(external, "redis_client", DummyRedis())

    with pytest.raises(HTTPException):
        await account_routes.get_account_balance()


@pytest.mark.asyncio
async def test_has_credentials_reads_settings():
    client = DummyMexcWithSettings(api_key="k", secret_key="s")
    assert account_routes._has_credentials(client) is True


@pytest.mark.asyncio
async def test_orders_endpoint_uses_cache_when_no_credentials(monkeypatch):
    dummy_client = DummyMexcWithSettings()
    cached_payload = {"orders": [{"id": 1}], "symbol": "TEST"}
    dummy_redis = DummyRedis(cached=cached_payload)

    import src.app.infrastructure.external as external

    monkeypatch.setattr(external, "redis_client", dummy_redis)
    monkeypatch.setattr(account_routes, "_get_mexc_client", lambda: dummy_client)

    result = await account_routes.orders_endpoint()

    assert result["source"] == "cache"
    assert result["orders"] == cached_payload["orders"]


@pytest.mark.asyncio
async def test_orders_endpoint_caches_api_response(monkeypatch):
    dummy_client = DummyMexcWithSettings(api_key="k", secret_key="s")
    dummy_redis = DummyRedis()

    import src.app.infrastructure.external as external

    monkeypatch.setattr(external, "redis_client", dummy_redis)
    monkeypatch.setattr(account_routes, "_get_mexc_client", lambda: dummy_client)

    async def fake_get_orders(symbol, mexc_client):
        return {"success": True, "source": "api", "symbol": symbol, "orders": [{"id": 2}], "count": 1, "timestamp": "now"}

    monkeypatch.setattr(account_routes, "get_orders", fake_get_orders)

    result = await account_routes.orders_endpoint()

    assert result["orders"] == [{"id": 2}]
    assert dummy_redis.saved is not None
