"""
Aggregate trades route.
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/market", tags=["Market Data"])
logger = logging.getLogger(__name__)


@router.get("/agg-trades/{symbol}")
async def get_agg_trades(
    symbol: str,
    limit: int = 200,
    from_id: Optional[int] = None,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
):
    """Get compressed aggregate trades list."""
    from infrastructure.external import mexc_client

    try:
        async with mexc_client:
            trades = await mexc_client.get_aggregate_trades(
                symbol=symbol,
                limit=limit,
                from_id=from_id,
                start_time=start_time,
                end_time=end_time,
            )
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "data": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get aggregate trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
