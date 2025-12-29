"""Unified sub-account facade mixin."""
import logging
from typing import Any, Dict, List

from infrastructure.config.config import config

logger = logging.getLogger(__name__)


class SubAccountFacadeMixin:
    async def get_sub_accounts(self) -> List[Dict[str, Any]]:
        try:
            if config.is_broker_mode:
                result = await self.get_broker_sub_accounts()
                return result.get("data", [])
            result = await self.get_sub_accounts_spot()
            return result.get("subAccounts", [])
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning(f"Failed to get sub-accounts: {exc}")
            return []

    async def get_sub_account_balance(self, identifier: str) -> Dict[str, Any]:
        if config.is_broker_mode:
            return await self.get_broker_sub_account_assets(identifier)
        raise NotImplementedError(
            "Spot API does not support querying sub-account balance from main account. "
            "You must use the sub-account's own API key to query its balance."
        )
