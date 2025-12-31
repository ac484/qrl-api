"""
Task interface aggregator aligned to `網頁結構.md`.

Wraps legacy handlers through per-task routers under `interfaces/tasks/mexc/*`
so behavior stays unchanged while the layout matches the target structure.
"""

from fastapi import APIRouter

from src.app.interfaces.tasks.mexc.sync_account import router as mexc_sync_account_router
from src.app.interfaces.tasks.mexc.sync_market import router as mexc_sync_market_router
from src.app.interfaces.tasks.mexc.sync_trades import router as mexc_sync_trades_router
from src.app.interfaces.tasks.runtime import router as runtime_router

router = APIRouter()
router.include_router(mexc_sync_account_router)
router.include_router(mexc_sync_market_router)
router.include_router(mexc_sync_trades_router)
router.include_router(runtime_router)

__all__ = ["router"]
