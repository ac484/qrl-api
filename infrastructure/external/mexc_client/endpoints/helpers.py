"""Helper mixins for user streams and convenience methods."""
from typing import Any, Dict, List, Optional

from .order import OrderEndpoints


class UserStreamMixin:
    async def create_listen_key(self) -> Dict[str, Any]:
        return await self._request("POST", "/api/v3/userDataStream", signed=True)

    async def keepalive_listen_key(self, listen_key: str) -> Dict[str, Any]:
        return await self._request(
            "PUT",
            "/api/v3/userDataStream",
            params={"listenKey": listen_key},
            signed=True,
        )

    async def get_listen_keys(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/userDataStream", signed=True)

    async def close_listen_key(self, listen_key: str) -> Dict[str, Any]:
        return await self._request(
            "DELETE",
            "/api/v3/userDataStream",
            params={"listenKey": listen_key},
            signed=True,
        )


class TradingHelpersMixin(OrderEndpoints):
    async def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
    ) -> Dict[str, Any]:
        if quantity is not None and quote_order_qty is not None:
            raise ValueError("Provide either quantity or quote_order_qty, not both")
        if quantity is None and quote_order_qty is None:
            raise ValueError("Either quantity or quote_order_qty is required for market orders")
        return await self.create_order(
            symbol=symbol,
            side=side.upper(),
            order_type="MARKET",
            quantity=quantity,
            quote_order_qty=quote_order_qty,
        )

    async def get_my_trades(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500,
    ) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"symbol": symbol, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return await self._request("GET", "/api/v3/myTrades", params=params, signed=True)

    async def transfer_between_sub_accounts(
        self,
        from_account_type: str,
        to_account_type: str,
        asset: str,
        amount: str,
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, Any] = {
            "fromAccountType": from_account_type,
            "toAccountType": to_account_type,
            "asset": asset,
            "amount": amount,
        }
        if from_account:
            params["fromAccount"] = from_account
        if to_account:
            params["toAccount"] = to_account
        return await self._request(
            "POST", "/api/v3/sub-account/universalTransfer", params=params, signed=True
        )


__all__ = ["UserStreamMixin", "TradingHelpersMixin"]
