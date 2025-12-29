import pytest

from domain.risk_manager import RiskManager
from domain.trading_strategy import TradingStrategy
from infrastructure.config.config import config as structured_config
from services.market.market_service import MarketService
from services.trading.trading_service import TradingService


def test_config_wrapper_reuses_singleton():
    from config import config as base_config

    assert structured_config is base_config


def test_trading_strategy_signal_direction():
    strategy = TradingStrategy(short_period=2, long_period=3)

    assert strategy.generate_signal([1, 2, 3, 4, 5]) == "BUY"
    assert strategy.generate_signal([5, 4, 3, 2, 1]) == "SELL"
    assert strategy.generate_signal([1, 1]) == "HOLD"


class DummyTradeRepo:
    def __init__(self):
        self.daily = 0
        self.last = None

    async def get_daily_trades(self):
        return self.daily

    async def get_last_trade_time(self):
        return self.last

    async def increment_daily_trades(self):
        self.daily += 1
        return self.daily

    async def set_last_trade_time(self, timestamp=None):
        self.last = timestamp
        return True


class DummyBot:
    def __init__(self, mexc_client=None, redis_client=None, symbol: str = "", dry_run: bool = False):
        self.symbol = symbol
        self.dry_run = dry_run

    async def execute_cycle(self):
        return {"success": True, "action": "HOLD", "message": "ok"}


@pytest.mark.asyncio
async def test_trading_service_allows_dependency_injection():
    trade_repo = DummyTradeRepo()
    service = TradingService(
        mexc_client=None,
        redis_client=None,
        trade_repository=trade_repo,
        risk_manager=RiskManager(max_daily_trades=10, min_trade_interval=0),
        bot_factory=DummyBot,
    )

    result = await service.execute(dry_run=True)

    assert result["success"] is True
    assert result.get("action") == "HOLD"
    assert trade_repo.daily == 0


class DummyPriceRepo:
    connected = False

    async def get_cached_ticker(self, symbol: str):
        return {}

    async def cache_ticker(self, symbol: str, ticker):
        self.cached_ticker = ticker
        return True

    async def cache_price(self, price: float, volume=None):
        self.cached_price = price
        return True

    async def cache_price_with_ttl(self, price: float, volume=None):
        self.cached_price_ttl = price
        return True


class DummyMexcClient:
    async def get_ticker_24hr(self, symbol: str):
        return {"symbol": symbol, "lastPrice": "1.0", "cached_at": ""}

    async def get_ticker_price(self, symbol: str):
        return {"symbol": symbol, "price": "1.0"}


@pytest.mark.asyncio
async def test_market_service_calls_client_when_no_cache():
    price_repo = DummyPriceRepo()
    market_service = MarketService(price_repo, DummyMexcClient())

    ticker = await market_service.get_ticker("TEST")
    price = await market_service.get_price("TEST")

    assert ticker["data"]["symbol"] == "TEST"
    assert price["symbol"] == "TEST"
