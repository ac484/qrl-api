"""
Account trades route.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


@router.get("/trades")
async def get_trades(symbol: str = "QRLUSDT", limit: int = 50):
    """Get user's trade history (real-time from MEXC API)."""
    from infrastructure.external.mexc_client import mexc_client

    try:
        async with mexc_client:
            trades = await mexc_client.get_my_trades(symbol, limit=limit)
            logger.info(f"Retrieved {len(trades)} trades for {symbol}")
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "trades": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get trades for {symbol}: {e}")
        return {
            "success": False,
            "symbol": symbol,
            "trades": [],
            "error": str(e),
        }
