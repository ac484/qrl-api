"""
Cloud Scheduler entrypoint for intelligent rebalance with order execution.

Implements the strategy documented in:
- docs/INTELLIGENT_REBALANCE_FORMULAS.md
- docs/INTELLIGENT_REBALANCE_EXECUTION_GUIDE.md

This endpoint enhances the symmetric rebalance with:
- MA (Moving Average) cross signals
- Cost basis validation
- Position tier management
- Automatic order execution when signals trigger
"""

import logging
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.services.trading.intelligent_rebalance_service import (
    IntelligentRebalanceService,
)
from src.app.infrastructure.external import mexc_client, redis_client, QRL_USDT_SYMBOL
from src.app.interfaces.tasks.shared import (
    ensure_redis_connected,
    require_scheduler_auth,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/rebalance/intelligent")
async def task_rebalance_intelligent(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    """
    Generate intelligent rebalance plan with MA signals and execute order.

    This endpoint implements an enhanced rebalancing strategy that includes:
    - MA (Moving Average) cross signal detection (MA_7 vs MA_25)
    - Cost basis validation (buy low, sell high)
    - Position tier management (70% core, 20% swing, 10% active)
    - Automatic order execution when conditions are met

    Decision logic:
    - BUY: Golden cross (MA_7 > MA_25) + price <= cost_avg
    - SELL: Death cross (MA_7 < MA_25) + price >= cost_avg * 1.03
    - HOLD: Otherwise or when within threshold

    Workflow:
    1. Calculates MA indicators from market data
    2. Generates intelligent rebalance plan
    3. If action is BUY or SELL, executes market order on MEXC
    4. Returns plan and order execution results

    Authentication:
        Requires Cloud Scheduler authentication via X-CloudScheduler
        header or OIDC Authorization header.

    Returns:
        dict: Intelligent rebalance plan with:
            - action: HOLD/BUY/SELL
            - MA indicators: ma_short, ma_long, signal
            - position_tiers: core, swing, active
            - signal_validation: price vs cost analysis
            - order: execution results (if BUY/SELL)
    """
    # Step 1: Authenticate
    auth_method = require_scheduler_auth(x_cloudscheduler, authorization)
    logger.info(f"[rebalance-intelligent] Authenticated via {auth_method}")

    # Step 2: Ensure Redis connection
    await ensure_redis_connected(redis_client)

    try:
        # Step 3: Generate intelligent rebalance plan
        balance_service = BalanceService(mexc_client, redis_client)
        intelligent_service = IntelligentRebalanceService(
            balance_service=balance_service,
            mexc_client=mexc_client,
            redis_client=redis_client,
        )
        plan = await intelligent_service.generate_plan()

        logger.info(
            f"[rebalance-intelligent] Plan generated - "
            f"Action: {plan.get('action')}, "
            f"Quantity: {plan.get('quantity', 0):.4f}, "
            f"MA Signal: {plan.get('ma_indicators', {}).get('signal', 'N/A')}"
        )

        # Step 4: Execute order if action is BUY or SELL
        order_result = None
        if plan.get("action") in ["BUY", "SELL"]:
            try:
                logger.info(
                    f"[rebalance-intelligent] Executing {plan['action']} order - "
                    f"Quantity: {plan['quantity']:.4f} QRL, "
                    f"MA Signal: {plan.get('ma_indicators', {}).get('signal')}"
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
                    f"[rebalance-intelligent] Order executed successfully - "
                    f"Order ID: {order.get('orderId')}, "
                    f"Status: {order.get('status')}"
                )
            except Exception as exc:
                order_result = {
                    "executed": False,
                    "error": str(exc),
                }
                logger.error(
                    f"[rebalance-intelligent] Order execution failed: {exc}",
                    exc_info=True,
                )
        else:
            logger.info(
                f"[rebalance-intelligent] No order executed - "
                f"Action: {plan.get('action')}, "
                f"Reason: {plan.get('reason')}"
            )

        return {
            "status": "success",
            "task": "rebalance-intelligent",
            "auth": auth_method,
            "plan": plan,
            "order": order_result,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        logger.error(f"[rebalance-intelligent] Validation error: {exc}")
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error(f"[rebalance-intelligent] Execution failed: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


__all__ = ["router", "task_rebalance_intelligent"]
