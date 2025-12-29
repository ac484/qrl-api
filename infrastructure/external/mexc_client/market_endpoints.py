"""
Public market endpoint helpers extracted from MEXC client core for clarity.
"""
from typing import Any, Dict, List, Optional


class MarketEndpointsMixin:
    """Public market endpoints for MEXC spot API."""

    async def ping(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/ping")

    async def get_server_time(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/time")

    async def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/api/v3/exchangeInfo", params=params)

    async def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/24hr", params=params)

    async def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/price", params=params)

    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        params = {"symbol": symbol, "limit": limit}
        return await self._request("GET", "/api/v3/depth", params=params)

    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        return await self.get_order_book(symbol, limit)

    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        params = {"symbol": symbol, "limit": limit}
        return await self._request("GET", "/api/v3/trades", params=params)

    async def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[List]:
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._request("GET", "/api/v3/klines", params=params)

    async def get_aggregate_trades(
        self,
        symbol: str,
        limit: int = 500,
        from_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"symbol": symbol, "limit": limit}
        if from_id is not None:
            params["fromId"] = from_id
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        return await self._request("GET", "/api/v3/aggTrades", params=params)

    async def get_book_ticker(self, symbol: str) -> Dict[str, Any]:
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/bookTicker", params=params)

__all__ = ["MarketEndpointsMixin"]
