"""
Market price route.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for a symbol (Direct MEXC API)."""
    from infrastructure.external import mexc_client

    try:
        logger.info(f"Fetching price for {symbol} from MEXC API")
        async with mexc_client:
            price_data = await mexc_client.get_ticker_price(symbol)
            price = float(price_data.get("price", 0))
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "price": str(price),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
