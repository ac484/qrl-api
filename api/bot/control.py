"""
Bot control routes.
"""
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/bot", tags=["Trading Bot"])
logger = logging.getLogger(__name__)


class ControlRequest(BaseModel):
    action: str  # "start" or "stop"
    dry_run: Optional[bool] = True


@router.post("/control", response_model=Dict[str, Any])
async def control_bot(request: ControlRequest):
    """Control bot operations (start/stop) - Stateless mode."""
    try:
        action = request.action.upper()
        if action not in ["START", "STOP"]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action: {action}. Must be START or STOP",
            )
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
            "timestamp": datetime.now().isoformat(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to control bot: {e}")
        raise HTTPException(status_code=500, detail=str(e))
