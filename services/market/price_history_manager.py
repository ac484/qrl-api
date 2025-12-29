"""Price history manager encapsulating history add/stats."""
class PriceHistoryManager:
    def __init__(self, price_repo):
        self.price_repo = price_repo

    async def add(self, symbol: str, price: float):
        await self.price_repo.add_price_to_history(symbol, price)
        await self.price_repo.set_cached_price(symbol, price)

    async def statistics(self, symbol: str, limit: int = 100):
        return await self.price_repo.get_price_statistics(symbol, limit=limit)
