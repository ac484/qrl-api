"""Status route."""
from datetime import datetime
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Status"])
logger = logging.getLogger(__name__)


class StatusResponse(BaseModel):
    bot_status: str
    daily_trades: int
    position: Optional[Dict[str, Any]] = None
    position_layers: Optional[Dict[str, Any]] = None
    timestamp: str


@router.get("/status", response_model=StatusResponse)
async def get_status():
    logger.info("Status retrieved - Direct API mode (no Redis)")
    return StatusResponse(
        bot_status="running",
        daily_trades=0,
        position=None,
        position_layers=None,
        timestamp=datetime.now().isoformat(),
    )
