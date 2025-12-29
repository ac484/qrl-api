"""Price resolver for market service."""
from infrastructure.utils.type_safety import safe_float


class PriceResolver:
    def __init__(self, mexc_client, price_repo):
        self.mexc = mexc_client
        self.price_repo = price_repo

    async def current_price(self, symbol: str) -> float:
        cached = await self.price_repo.get_latest_price(symbol)
        if cached:
            return safe_float(cached)
        async with self.mexc:
            ticker = await self.mexc.get_ticker_24hr(symbol)
            price = safe_float(ticker.get("lastPrice", 0))
            await self.price_repo.set_latest_price(symbol, price)
            return price
