"""
Price resolver for trading workflow (current price + history fill).
"""
from typing import List


class PriceResolver:
    def __init__(self, mexc_client, price_repo):
        self.mexc = mexc_client
        self.price_repo = price_repo

    async def get_current_price(self, symbol: str) -> float:
        price_data = await self.price_repo.get_latest_price(symbol)
        if price_data:
            return float(price_data)
        async with self.mexc:
            ticker = await self.mexc.get_ticker_24hr(symbol)
            current_price = float(ticker.get("lastPrice", 0))
            await self.price_repo.set_latest_price(symbol, current_price)
            return current_price

    async def get_price_history(self, current_price: float) -> List[dict]:
        price_history = await self.price_repo.get_price_history(limit=60)
        if not price_history or len(price_history) < 60:
            price_history = price_history or []
            price_history = price_history + [{"price": current_price}] * (60 - len(price_history))
        return price_history
