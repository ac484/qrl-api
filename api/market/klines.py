"""
Klines route.
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException

from infrastructure.external.mexc_client.account import QRL_USDT_SYMBOL

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str,
    interval: str = "1m",
    limit: int = 100,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
    """Get candlestick (kline) data."""
    from infrastructure.external import mexc_client

    if symbol != QRL_USDT_SYMBOL:
        raise HTTPException(status_code=404, detail="Only QRLUSDT is supported")

    try:
        async with mexc_client:
            klines = await mexc_client.get_klines(
                symbol=symbol,
                interval=interval,
                limit=limit,
                start_time=start_time,
                end_time=end_time,
            )
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "interval": interval,
                "data": klines,
                "count": len(klines),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
