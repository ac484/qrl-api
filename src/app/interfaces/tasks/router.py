"""
Task interface aggregator for Cloud Scheduler endpoints.

This module consolidates all scheduled task routers:
- 15-min-job: Cost/PnL update + Rebalance (primary integration)
- rebalance/symmetric: Standalone rebalance endpoint (manual/legacy)
- MEXC sync tasks: Market data, account, and trade synchronization
"""

from fastapi import APIRouter

from src.app.interfaces.tasks.mexc.sync_account import (
    router as mexc_sync_account_router,
)
from src.app.interfaces.tasks.mexc.sync_market import router as mexc_sync_market_router
from src.app.interfaces.tasks.mexc.sync_trades import router as mexc_sync_trades_router
from src.app.interfaces.tasks.rebalance import router as rebalance_router

# Dynamic import for 15-min-job (file has hyphen in name)
import sys
from pathlib import Path

router = APIRouter()

# Register MEXC sync task routers
router.include_router(mexc_sync_account_router)
router.include_router(mexc_sync_market_router)
router.include_router(mexc_sync_trades_router)

# Register 15-min-job router (primary integration)
# Import module with hyphen in filename
try:
    task_15min_path = Path(__file__).parent / "15-min-job.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "fifteen_min_job_module", task_15min_path
    )
    if spec and spec.loader:
        fifteen_min_job_module = importlib.util.module_from_spec(spec)
        sys.modules["fifteen_min_job_module"] = fifteen_min_job_module
        spec.loader.exec_module(fifteen_min_job_module)
        router.include_router(fifteen_min_job_module.router)
except Exception as e:
    # Log but don't fail - allows graceful degradation
    import logging

    logging.getLogger(__name__).warning(
        f"Failed to load 15-min-job router: {e}", exc_info=True
    )

# Register standalone rebalance router (manual/legacy support)
router.include_router(rebalance_router)

__all__ = ["router"]
