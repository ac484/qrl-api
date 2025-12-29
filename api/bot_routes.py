"""
Trading bot control API routes
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
import logging

router = APIRouter(prefix="/bot", tags=["Trading Bot"])
logger = logging.getLogger(__name__)


class ControlRequest(BaseModel):
    """Bot control request"""
    action: str  # "start" or "stop"
    dry_run: Optional[bool] = True


class ExecuteRequest(BaseModel):
    """Manual trade execution request"""
    action: str  # "BUY", "SELL", or "AUTO"
    dry_run: Optional[bool] = True


class ExecuteResponse(BaseModel):
    """Trade execution response"""
    success: bool
    action: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.post("/control", response_model=Dict[str, Any])
async def control_bot(request: ControlRequest):
    """
    Control bot operations (start/stop) - Stateless mode
    
    Args:
        request: Control request with action and dry_run flag
        
    Returns:
        Status of the control operation
    """
    try:
        action = request.action.upper()
        
        if action not in ["START", "STOP"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Must be START or STOP"
            )
        
        # No state storage (stateless mode)
        if action == "START":
            logger.info(f"Bot start requested (dry_run={request.dry_run})")
            message = f"Bot start signal sent in {'DRY RUN' if request.dry_run else 'LIVE'} mode"
        else:
            logger.info("Bot stop requested")
            message = "Bot stop signal sent"
        
        return {
            "success": True,
            "action": action,
            "dry_run": request.dry_run,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/execute", response_model=ExecuteResponse)
async def execute_trading(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """
    Execute trading operation manually
    
    Args:
        request: Execution request with action (BUY/SELL/AUTO) and dry_run flag
        background_tasks: FastAPI background tasks
        
    Returns:
        Execution result
    """
    from infrastructure.bot import TradingBot
    from infrastructure.config import config
    
    try:
        action = request.action.upper()
        
        if action not in ["BUY", "SELL", "AUTO"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Must be BUY, SELL, or AUTO"
            )
        
        logger.info(f"Manual execution requested: {action} (dry_run={request.dry_run})")
        
        # Create bot instance
        bot = TradingBot(
            symbol=config.TRADING_SYMBOL,
            dry_run=request.dry_run
        )
        
        # Execute in background
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
            data={
                "dry_run": request.dry_run,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute trading: {e}")
        return ExecuteResponse(
            success=False,
            action=request.action,
            message=f"Execution failed: {str(e)}",
            data=None
        )
