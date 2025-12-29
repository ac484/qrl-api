"""
Trading bot control API routes (aggregated).
"""
from fastapi import APIRouter

from api.bot.control import router as control_router, control_bot
from api.bot.execute import router as execute_router, execute_trading, ExecuteRequest, ExecuteResponse

router = APIRouter()
router.include_router(control_router)
router.include_router(execute_router)

__all__ = [
    "router",
    "control_bot",
    "execute_trading",
    "ExecuteRequest",
    "ExecuteResponse",
]
