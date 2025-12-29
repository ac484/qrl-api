"""Account endpoints mixin."""
from typing import Any, Dict, Optional

from infrastructure.external.mexc_client.account import build_balance_map, fetch_balance_snapshot


class AccountRepoMixin:
    async def get_account_info(self) -> Dict[str, Any]:
        return await self._request("GET", "/api/v3/account", signed=True)

    async def get_asset_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        account_info = await self.get_account_info()
        if asset:
            for balance in account_info.get("balances", []):
                if balance.get("asset") == asset:
                    return balance
            return {"asset": asset, "free": "0", "locked": "0"}
        return account_info

    async def get_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        account_info = await self.get_account_info()
        balances = build_balance_map(account_info)
        if asset:
            return balances.get(asset, {"asset": asset, "free": "0", "locked": "0", "total": 0})
        return balances

    async def get_balance_snapshot(self) -> Dict[str, Any]:
        return await fetch_balance_snapshot(self)
