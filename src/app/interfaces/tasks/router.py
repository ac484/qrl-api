"""
Task interface aggregator for Cloud Scheduler endpoints.

This module consolidates all scheduled task routers:
- task_15_min_job: Cost/PnL update + Rebalance (primary integration)
- rebalance/symmetric: Standalone symmetric rebalance endpoint (manual/legacy)
- rebalance/intelligent: Enhanced rebalance with MA signals and position tiers
- MEXC sync tasks: Market data, account, and trade synchronization
"""

import logging

from fastapi import APIRouter

from src.app.interfaces.tasks.mexc.sync_account import (
    router as mexc_sync_account_router,
)
from src.app.interfaces.tasks.mexc.sync_market import router as mexc_sync_market_router
from src.app.interfaces.tasks.mexc.sync_trades import router as mexc_sync_trades_router

logger = logging.getLogger(__name__)

router = APIRouter()

# Register MEXC sync task routers
router.include_router(mexc_sync_account_router)
router.include_router(mexc_sync_market_router)
router.include_router(mexc_sync_trades_router)

# Register 15-min-job router (primary integration)
# Fixed: Use standard Python module name instead of hyphenated filename
try:
    from src.app.interfaces.tasks.task_15_min_job import router as task_15min_router

    router.include_router(task_15min_router)
    logger.info("Successfully registered 15-min-job router")
except Exception as e:
    # Log but don't fail - allows graceful degradation
    logger.warning(f"Failed to load 15-min-job router: {e}", exc_info=True)

# Register standalone rebalance router (manual/legacy support)
try:
    from src.app.interfaces.tasks.rebalance import router as rebalance_router

    router.include_router(rebalance_router)
    logger.info("Successfully registered rebalance router")
except Exception as e:
    # Log but don't fail - allows graceful degradation
    logger.warning(f"Failed to load rebalance router: {e}", exc_info=True)

# Register intelligent rebalance router (enhanced strategy with MA signals)
try:
    from src.app.interfaces.tasks.intelligent_rebalance import (
        router as intelligent_rebalance_router,
    )

    router.include_router(intelligent_rebalance_router)
    logger.info("Successfully registered intelligent rebalance router")
except Exception as e:
    # Log but don't fail - allows graceful degradation
    logger.warning(f"Failed to load intelligent rebalance router: {e}", exc_info=True)

__all__ = ["router"]
