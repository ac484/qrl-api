import sys
from pathlib import Path

import pytest

# Ensure project root is on sys.path for module imports
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.app.interfaces.http import market as market_routes


class DummyMexcClient:
    def __init__(self) -> None:
        self.ticker_called = False
        self.price_called = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get_ticker_24hr(self, symbol: str):
        self.ticker_called = True
        return {
            "symbol": symbol,
            "lastPrice": "0.123456",
            "priceChangePercent": "1.5",
        }

    async def get_ticker_price(self, symbol: str):
        self.price_called = True
        return {"symbol": symbol, "price": "0.123456"}


@pytest.mark.asyncio
async def test_get_ticker_uses_shared_client(monkeypatch):
    dummy_client = DummyMexcClient()
    monkeypatch.setattr(market_routes, "_get_mexc_client", lambda: dummy_client)

    result = await market_routes.ticker_endpoint("QRLUSDT")

    assert result["data"]["symbol"] == "QRLUSDT"
    assert dummy_client.ticker_called is True


@pytest.mark.asyncio
async def test_get_price_uses_shared_client(monkeypatch):
    dummy_client = DummyMexcClient()
    monkeypatch.setattr(market_routes, "_get_mexc_client", lambda: dummy_client)

    result = await market_routes.price_endpoint("QRLUSDT")

    assert result["price"] == "0.123456"
    assert dummy_client.price_called is True
