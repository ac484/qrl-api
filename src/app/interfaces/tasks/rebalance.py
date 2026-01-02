"""
Cloud Scheduler entrypoint for symmetric (equal-value) rebalance with order execution.

This endpoint can be called independently or via the 15-min-job integration.
Kept for manual triggering and backward compatibility with existing Cloud Scheduler jobs.

This endpoint now executes trades automatically:
1. Generates rebalance plan
2. If action is BUY or SELL, places market order on MEXC
3. Returns plan and order execution results
"""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.services.trading.rebalance_service import (
    RebalanceService,
)
from src.app.infrastructure.external import mexc_client, redis_client, QRL_USDT_SYMBOL
from src.app.interfaces.tasks.shared import (
    ensure_redis_connected,
    require_scheduler_auth,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/rebalance/symmetric")
async def task_rebalance_symmetric(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    """
    Generate symmetric (50/50 value) rebalance plan and execute order.

    This endpoint can be triggered:
    1. Directly by Cloud Scheduler (for standalone operation)
    2. Manually for testing/debugging
    3. As part of 15-min-job integration (recommended)

    Workflow:
    1. Generates rebalance plan based on account balance
    2. If action is BUY or SELL (not HOLD), executes market order on MEXC
    3. Returns plan and order execution results

    Authentication:
        Requires Cloud Scheduler authentication via X-CloudScheduler
        header or OIDC Authorization header.

    Returns:
        dict: Rebalance plan with action (HOLD/BUY/SELL), order execution results
    """
    # Step 1: Authenticate
    auth_method = require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[rebalance-symmetric] Authenticated via {auth_method}")

    # Step 2: Ensure Redis connection
    await ensure_redis_connected(redis_client)

    try:
        # Step 3: Generate rebalance plan
        balance_service = BalanceService(mexc_client, redis_client)
        rebalance_service = RebalanceService(balance_service, redis_client)
        plan = await rebalance_service.generate_plan()

        logger.info(
            f"[rebalance-symmetric] Plan generated - "
            f"Action: {plan.get('action')}, "
            f"Quantity: {plan.get('quantity', 0):.4f}"
        )

        # Step 4: Execute order if action is BUY or SELL
        order_result = None
        if plan.get("action") in ["BUY", "SELL"]:
            try:
                logger.info(
                    f"[rebalance-symmetric] Executing {plan['action']} order - "
                    f"Quantity: {plan['quantity']:.4f} QRL"
                )
                order = await mexc_client.place_market_order(
                    symbol=QRL_USDT_SYMBOL,
                    side=plan["action"],
                    quantity=plan["quantity"],
                )
                order_result = {
                    "executed": True,
                    "order_id": order.get("orderId"),
                    "status": order.get("status"),
                    "details": order,
                }
                logger.info(
                    f"[rebalance-symmetric] Order executed successfully - "
                    f"Order ID: {order.get('orderId')}, "
                    f"Status: {order.get('status')}"
                )
            except Exception as exc:
                order_result = {
                    "executed": False,
                    "error": str(exc),
                }
                logger.error(
                    f"[rebalance-symmetric] Order execution failed: {exc}",
                    exc_info=True,
                )
        else:
            logger.info(
                f"[rebalance-symmetric] No order executed - Action: {plan.get('action')}"
            )

        return {
            "status": "success",
            "task": "rebalance-symmetric",
            "auth": auth_method,
            "plan": plan,
            "order": order_result,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"[rebalance-symmetric] Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"[rebalance-symmetric] Execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router", "task_rebalance_symmetric"]
