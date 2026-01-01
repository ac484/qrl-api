"""Trading endpoints mixin for MEXC client."""
from typing import Dict, Optional, Any


class TradeRepoMixin:
    async def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
        price: Optional[float] = None,
        time_in_force: str = "GTC",
    ) -> Dict[str, Any]:  # type: ignore[name-defined]
        params = {"symbol": symbol, "side": side, "type": order_type}
        if quantity:
            params["quantity"] = quantity
        if quote_order_qty:
            params["quoteOrderQty"] = quote_order_qty
        if price:
            params["price"] = price
        if order_type == "LIMIT":
            params["timeInForce"] = time_in_force
        return await self._request("POST", "/api/v3/order", params=params, signed=True)

    async def cancel_order(self, symbol: str, order_id: Optional[int] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:  # type: ignore[name-defined]
        params = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        if orig_client_order_id:
            params["origClientOrderId"] = orig_client_order_id
        return await self._request(
            "DELETE", "/api/v3/order", params=params, signed=True
        )

    async def get_order(self, symbol: str, order_id: Optional[int] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:  # type: ignore[name-defined]
        params = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        if orig_client_order_id:
            params["origClientOrderId"] = orig_client_order_id
        return await self._request("GET", "/api/v3/order", params=params, signed=True)

    async def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:  # type: ignore[name-defined]
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request(
            "GET", "/api/v3/openOrders", params=params, signed=True
        )

    async def get_all_orders(self, symbol: str, limit: int = 500) -> Dict[str, Any]:  # type: ignore[name-defined]
        params = {"symbol": symbol, "limit": limit}
        return await self._request(
            "GET", "/api/v3/allOrders", params=params, signed=True
        )


# Backward-compatible alias expected by package exports
TradeRepository = TradeRepoMixin

__all__ = ["TradeRepoMixin", "TradeRepository"]
