"""
Account HTTP routes aligned to target architecture.
"""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.account.list_orders import get_orders
from src.app.application.account.list_trades import get_trades

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


def _build_balance_service() -> BalanceService:
    from src.app.infrastructure.external import mexc_client
    from src.app.infrastructure.external import redis_client
    return BalanceService(mexc_client, redis_client)


def _get_mexc_client():
    from src.app.infrastructure.external import mexc_client
    return mexc_client


def _has_credentials(mexc_client) -> bool:
    settings = getattr(mexc_client, "settings", None)
    return bool(getattr(settings, "api_key", None) and getattr(settings, "secret_key", None))


async def _cache_orders(payload):
    try:
        from src.app.infrastructure.external import redis_client

        if not redis_client.connected:
            await redis_client.connect()
        await redis_client.set_mexc_raw_response("openOrders", payload)
    except Exception as exc:
        logger.warning(f"Failed to cache orders: {exc}")
        return False
    return True


async def _get_cached_orders():
    try:
        from src.app.infrastructure.external import redis_client

        if not redis_client.connected:
            await redis_client.connect()
        cached = await redis_client.get_mexc_raw_response("openOrders")
        if cached:
            orders = cached.get("orders") or cached.get("data") or []
            return {
                "success": True,
                "source": "cache",
                "symbol": cached.get("symbol") or "QRLUSDT",
                "orders": orders,
                "count": len(orders),
                "timestamp": datetime.now().isoformat(),
                "note": "served from cache",
            }
    except Exception as exc:
        logger.warning(f"Failed to load cached orders: {exc}")
    return None


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
    except Exception as exc:
        logger.error(f"Failed to get account balance: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/balance/cache")
async def get_cached_balance():
    """Retrieve cached balance without hitting the exchange."""
    from src.app.infrastructure.external import redis_client

    cached = await redis_client.get_cached_account_balance()
    if cached:
        cached["source"] = "cache"
        cached["timestamp"] = datetime.now().isoformat()
        return cached
    raise HTTPException(status_code=404, detail="No cached balance available")


@router.get("/orders")
async def orders_endpoint():
    """Get user's open orders for QRL/USDT (real-time from MEXC API)."""
    mexc_client = _get_mexc_client()

    try:
        from src.app.infrastructure.external.mexc.account import QRL_USDT_SYMBOL

        if not _has_credentials(mexc_client):
            cached = await _get_cached_orders()
            if cached:
                return cached
            return {
                "success": True,
                "source": "cache",
                "symbol": QRL_USDT_SYMBOL,
                "orders": [],
                "count": 0,
                "timestamp": datetime.now().isoformat(),
                "note": "API credentials missing; returning empty orders",
            }

        result = await get_orders(QRL_USDT_SYMBOL, mexc_client)
        await _cache_orders(result)
        return result
    except Exception as e:
        logger.error(f"Failed to get orders: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def trades_endpoint(symbol: str = "QRLUSDT", limit: int = 50):
    """Get user's trade history (real-time from MEXC API)."""
    try:
        mexc_client = _get_mexc_client()
        result = await get_trades(symbol, mexc_client, limit=limit)
        return result
    except Exception as e:
        logger.error(f"Failed to get trades: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-accounts")
async def get_configured_sub_account():
    """Get configured sub-account balance (alias for convenience)."""
    mexc_client = _get_mexc_client()
    from src.app.infrastructure.config import config

    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(status_code=401, detail="API keys not configured")

        sub_account_id = config.active_sub_account_identifier
        if not sub_account_id:
            raise HTTPException(
                status_code=400,
                detail="Sub-account not configured - set SUB_ACCOUNT_ID or SUB_ACCOUNT_NAME",
            )

        async with mexc_client:
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            balance_data = await mexc_client.get_sub_account_balance(sub_account_id)
            logger.info(f"Retrieved sub-account balance for {sub_account_id}")
            return {
                "success": True,
                "mode": mode,
                "sub_account_id": sub_account_id,
                "balance": balance_data,
                "timestamp": datetime.now().isoformat(),
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
