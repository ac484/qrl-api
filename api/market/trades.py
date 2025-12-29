"""
Recent trades route.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/trades/{symbol}")
async def get_recent_trades(symbol: str, limit: int = 200):
    """Get recent trades for a symbol (Direct MEXC API)."""
    from infrastructure.external import mexc_client

    try:
        logger.info(f"Fetching recent trades for {symbol} from MEXC API")
        async with mexc_client:
            trades = await mexc_client.get_recent_trades(symbol, limit)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get recent trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
