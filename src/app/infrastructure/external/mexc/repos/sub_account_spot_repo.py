"""Spot sub-account endpoints (regular users)."""
import time
from typing import Any, Dict, Optional


class SubAccountSpotRepoMixin:
    async def get_sub_accounts_spot(
        self, sub_account_id: Optional[str] = None, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        params = {"page": page, "limit": limit, "timestamp": int(time.time() * 1000)}
        if sub_account_id:
            params["subAccountId"] = sub_account_id
        return await self._request(
            "GET", "/api/v3/sub-account/list", params=params, signed=True
        )

    async def sub_account_universal_transfer(
        self,
        asset: str,
        amount: str,
        from_account: Optional[str] = None,
        to_account: Optional[str] = None,
        client_tran_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {
            "asset": asset,
            "amount": amount,
            "timestamp": int(time.time() * 1000),
        }
        if from_account:
            params["fromAccount"] = from_account
        if to_account:
            params["toAccount"] = to_account
        if client_tran_id:
            params["clientTranId"] = client_tran_id
        return await self._request(
            "POST", "/api/v3/sub-account/universalTransfer", params=params, signed=True
        )

    async def create_sub_account_api_key(
        self,
        sub_account_id: str,
        permissions: str,
        ip_restriction: Optional[str] = None,
        note: Optional[str] = None,
    ) -> Dict[str, Any]:
        params = {
            "subAccountId": sub_account_id,
            "permissions": permissions,
            "timestamp": int(time.time() * 1000),
        }
        if ip_restriction:
            params["ipRestriction"] = ip_restriction
        if note:
            params["note"] = note
        return await self._request(
            "POST", "/api/v3/sub-account/apiKey", params=params, signed=True
        )

    async def delete_sub_account_api_key(
        self, sub_account_id: str, api_key: str
    ) -> Dict[str, Any]:
        params = {
            "subAccountId": sub_account_id,
            "apiKey": api_key,
            "timestamp": int(time.time() * 1000),
        }
        return await self._request(
            "DELETE", "/api/v3/sub-account/apiKey", params=params, signed=True
        )


# Backward-compatible alias expected by package exports
SubAccountSpotRepository = SubAccountSpotRepoMixin

__all__ = ["SubAccountSpotRepoMixin", "SubAccountSpotRepository"]
