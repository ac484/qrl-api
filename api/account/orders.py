"""
Account open orders route.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


def _has_credentials(mexc_client) -> bool:
    return bool(getattr(mexc_client, "api_key", None) and getattr(mexc_client, "secret_key", None))


@router.get("/orders")
async def get_orders():
    """Get user's open orders for QRL/USDT (real-time from MEXC API)."""
    from infrastructure.external.mexc_client import mexc_client

    symbol = QRL_USDT_SYMBOL
    if not _has_credentials(mexc_client):
        raise HTTPException(status_code=503, detail="MEXC API credentials required for orders")

    try:
        async with mexc_client:
            orders = await mexc_client.get_open_orders(symbol)
            logger.info(f"Retrieved {len(orders)} open orders for {symbol}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "orders": orders,
                "count": len(orders),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get orders for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
