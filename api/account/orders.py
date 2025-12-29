"""
Account open orders route.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


@router.get("/orders")
async def get_orders(symbol: str = "QRLUSDT", limit: int = 50):
    """Get user's open orders (real-time from MEXC API)."""
    from infrastructure.external.mexc_client import mexc_client

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
