"""
Exchange info route.
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/exchange-info")
async def get_exchange_info(symbol: Optional[str] = None):
    """Get exchange info / symbol trading rules."""
    from infrastructure.external import mexc_client

    try:
        async with mexc_client:
            info = await mexc_client.get_exchange_info(symbol)
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": info,
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get exchange info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
