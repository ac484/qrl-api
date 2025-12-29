"""
Bot execute routes.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/bot", tags=["Trading Bot"])
logger = logging.getLogger(__name__)


class ExecuteRequest(BaseModel):
    action: str  # "BUY", "SELL", or "AUTO"
    dry_run: Optional[bool] = True


class ExecuteResponse(BaseModel):
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/execute", response_model=ExecuteResponse)
async def execute_trading(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """Execute trading operation manually."""
    from infrastructure.bot import TradingBot
    from infrastructure.config import config

    try:
        action = request.action.upper()
        if action not in ["BUY", "SELL", "AUTO"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Must be BUY, SELL, or AUTO",
            )
        logger.info(f"Manual execution requested: {action} (dry_run={request.dry_run})")

        bot = TradingBot(symbol=config.TRADING_SYMBOL, dry_run=request.dry_run)

        async def run_bot():
            try:
                result = await bot.run_trading_cycle()
                logger.info(f"Trading cycle completed: {result}")
            except Exception as e:
                logger.error(f"Trading cycle failed: {e}", exc_info=True)

        background_tasks.add_task(run_bot)

        return ExecuteResponse(
            success=True,
            action=action,
            message=f"Trading execution started in background ({'DRY RUN' if request.dry_run else 'LIVE'} mode)",
            data={"dry_run": request.dry_run, "timestamp": datetime.now().isoformat()},
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute trading: {e}")
        return ExecuteResponse(
            success=False,
            action=request.action,
            message=f"Execution failed: {str(e)}",
            data=None,
        )
