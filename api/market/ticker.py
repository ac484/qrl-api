"""
Market ticker route.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get 24-hour ticker data for a symbol (Direct MEXC API)."""
    from infrastructure.external import mexc_client

    try:
        logger.info(f"Fetching ticker for {symbol} from MEXC API")
        async with mexc_client:
            ticker = await mexc_client.get_ticker_24hr(symbol)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": ticker,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
