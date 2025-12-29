"""
Orderbook route.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 50):
    """Get order book (depth) for a symbol (Direct MEXC API)."""
    from infrastructure.external import mexc_client

    try:
        logger.info(f"Fetching order book for {symbol} from MEXC API")
        async with mexc_client:
            orderbook = await mexc_client.get_order_book(symbol, limit)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": orderbook,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get order book for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
