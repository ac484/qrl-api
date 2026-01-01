"""
15-minute scheduled task: Cost/PnL update + Rebalance execution.

This task runs every 15 minutes via Cloud Scheduler and performs:
1. Updates cost basis and unrealized/realized PnL
2. Generates and stores rebalance plan
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.services.trading.rebalance_service import (
    RebalanceService,
)
from src.app.infrastructure.external import mexc_client, redis_client
from src.app.interfaces.tasks.shared import (
    ensure_redis_connected,
    require_scheduler_auth,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/15-min-job")
async def task_15_min_job(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    """
    15-minute scheduled task handler.

    Executes two operations:
    1. Cost/PnL update (future implementation)
    2. Symmetric rebalance plan generation

    Authentication:
        Requires Cloud Scheduler authentication via X-CloudScheduler
        header or OIDC Authorization header.

    Returns:
        dict: Task execution results including rebalance plan
    """
    start_time = datetime.now()

    # Step 1: Authenticate
    auth_method = require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[15-min-job] Started - authenticated via {auth_method}")

    # Step 2: Ensure Redis connection
    await ensure_redis_connected(redis_client)

    try:
        # Step 3: Cost/PnL update (placeholder for future implementation)
        cost_update_result = {
            "status": "not_implemented",
            "message": "Cost/PnL update pending implementation",
        }

        # Step 4: Execute rebalance
        logger.info("[15-min-job] Executing rebalance plan generation...")
        balance_service = BalanceService(mexc_client, redis_client)
        rebalance_service = RebalanceService(balance_service, redis_client)
        rebalance_plan = await rebalance_service.generate_plan()

        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        logger.info(
            f"[15-min-job] Completed successfully in {duration_ms}ms - "
            f"Rebalance action: {rebalance_plan.get('action', 'UNKNOWN')}"
        )

        return {
            "status": "success",
            "task": "15-min-job",
            "auth": auth_method,
            "timestamp": end_time.isoformat(),
            "duration_ms": duration_ms,
            "cost_update": cost_update_result,
            "rebalance": rebalance_plan,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"[15-min-job] Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"[15-min-job] Execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router", "task_15_min_job"]
