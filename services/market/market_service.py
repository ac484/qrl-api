"""Market service coordinating price retrieval and caching."""
from datetime import datetime
from typing import Dict, Any

from infrastructure.config.config import config
from infrastructure.external.mexc_client.client import mexc_client as default_mexc_client
from repositories.market.price_repository import PriceRepository


class MarketService:
    """Fetches market data and maintains cache consistency."""

    def __init__(
        self,
        price_repository: PriceRepository,
        mexc_client=default_mexc_client,
    ):
        self.price_repository = price_repository
        self.mexc_client = mexc_client

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        if self.price_repository.connected:
            cached_ticker = await self.price_repository.get_cached_ticker(symbol)
            if cached_ticker:
                return {
                    "symbol": symbol,
                    "data": cached_ticker,
                    "timestamp": cached_ticker.get("cached_at"),
                    "cached": True,
                }

        ticker = await self.mexc_client.get_ticker_24hr(symbol)

        if self.price_repository.connected:
            await self.price_repository.cache_ticker(symbol, ticker)

        return {
            "symbol": symbol,
            "data": ticker,
            "timestamp": datetime.now().isoformat(),
            "cached": False,
        }

    async def get_price(self, symbol: str) -> Dict[str, Any]:
        price_data = await self.mexc_client.get_ticker_price(symbol)

        if self.price_repository.connected and symbol == config.TRADING_SYMBOL:
            price = float(price_data.get("price", 0))
            await self.price_repository.cache_price(price)
            await self.price_repository.cache_price_with_ttl(price)

        return {
            "symbol": symbol,
            "price": price_data,
            "timestamp": datetime.now().isoformat(),
        }


__all__ = ["MarketService"]
