"""
Cloud Task handler for syncing account balances (application layer).

Keeps existing behavior while living in the target architecture tree.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import Header, HTTPException, params

from src.app.infrastructure.config import config
from src.app.infrastructure.external import mexc_client, redis_client
from src.app.application.account.balance_service import BalanceService

logger = logging.getLogger(__name__)


def _require_scheduler_auth(
    x_cloudscheduler: Optional[str], authorization: Optional[str]
) -> str:
    if isinstance(x_cloudscheduler, params.Header):
        x_cloudscheduler = None
    if isinstance(authorization, params.Header):
        authorization = None
    if not x_cloudscheduler and not authorization:
        raise HTTPException(
            status_code=401, detail="Unauthorized - Cloud Scheduler only"
        )
    return "OIDC" if authorization else "X-CloudScheduler"


async def task_sync_balance(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
) -> dict[str, object]:
    auth_method = _require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[Cloud Task] 01-min-job authenticated via {auth_method}")

    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            logger.warning(
                "[Cloud Task] API keys not configured, skipping balance sync"
            )
            return {"status": "skipped", "reason": "API keys not configured"}

        # Use encapsulated BalanceService instead of direct API calls
        balance_service = BalanceService(mexc_client, redis_client)
        snapshot = await balance_service.get_account_balance()

        # Extract QRL and USDT balances from snapshot
        qrl_data = snapshot.get("balances", {}).get("QRL", {})
        usdt_data = snapshot.get("balances", {}).get("USDT", {})

        qrl_balance = float(qrl_data.get("free", 0))
        usdt_balance = float(usdt_data.get("free", 0))

        # Count all non-zero assets from raw account info
        all_balances = {}
        raw_account = snapshot.get("raw", {})
        for balance in raw_account.get("balances", []):
            asset = balance.get("asset")
            free = float(balance.get("free", 0))
            locked = float(balance.get("locked", 0))

            if free > 0 or locked > 0:
                all_balances[asset] = {
                    "free": str(free),
                    "locked": str(locked),
                    "total": str(free + locked),
                }

        logger.info(
            "[Cloud Task] Balance synced (via BalanceService) - "
            f"QRL: {qrl_balance:.2f}, USDT: {usdt_balance:.2f}, "
            f"Total assets: {len(all_balances)}"
        )

        return {
            "status": "success",
            "task": "01-min-job",
            "data": {
                "qrl_balance": qrl_balance,
                "usdt_balance": usdt_balance,
                "total_assets": len(all_balances),
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as exc:  # pragma: no cover - network call
        logger.error(f"[Cloud Task] Balance sync failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["task_sync_balance"]
