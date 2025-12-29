"""
Best bid/ask route.
"""
import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/book-ticker/{symbol}")
async def get_book_ticker(symbol: str):
    """Best bid/ask for a symbol."""
    from infrastructure.external import mexc_client

    try:
        async with mexc_client:
            book = await mexc_client.get_book_ticker(symbol)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": book,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get book ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
