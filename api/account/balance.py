"""
Account balance route with cache-aware balance service.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

from services.account import BalanceService

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


def _build_balance_service() -> BalanceService:
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.external.redis_client import redis_client

    return BalanceService(mexc_client, redis_client)


@router.get("/balance")
async def get_account_balance():
    """Get account balance with fallback to cached snapshot."""
    try:
        service = _build_balance_service()
        snapshot = await service.get_account_balance()
        BalanceService.to_usd_values(snapshot)
        return snapshot
    except ValueError as exc:
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:  # pragma: no cover - FastAPI will surface HTTP 500
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/balance/cache")
async def get_cached_balance():
    """Retrieve cached balance without hitting the exchange."""
    from infrastructure.external.redis_client import redis_client

    cached = await redis_client.get_cached_account_balance()
    if cached:
        cached["source"] = "cache"
        cached["timestamp"] = datetime.now().isoformat()
        return cached
    raise HTTPException(status_code=404, detail="No cached balance available")
