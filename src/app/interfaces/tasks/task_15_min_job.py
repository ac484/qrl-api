"""
15-minute scheduled task: Cost/PnL update + Rebalance execution with order placement.

This task runs every 15 minutes via Cloud Scheduler and performs:
1. Updates cost basis and unrealized/realized PnL (planned)
2. Generates and stores rebalance plan
3. Executes market orders on MEXC when rebalance is needed
"""

import logging
from datetime import datetime
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


@router.post("/15-min-job")
async def task_15_min_job(
    x_cloudscheduler: Optional[str] = Header(None, alias="X-CloudScheduler"),
    authorization: Optional[str] = Header(None),
):
    """
    15-minute scheduled task handler with order execution.

    Executes three operations:
    1. Cost/PnL update (future implementation)
    2. Symmetric rebalance plan generation
    3. Automatic order execution when rebalance is needed

    Workflow:
    - Generates rebalance plan based on account balance
    - If action is BUY or SELL, executes market order on MEXC
    - Logs detailed execution results

    Authentication:
        Requires Cloud Scheduler authentication via X-CloudScheduler
        header or OIDC Authorization header.

    Returns:
        dict: Task execution results including rebalance plan and order details
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

        # Get balance snapshot for debugging
        snapshot = await balance_service.get_account_balance()

        qrl_total = snapshot.get("balances", {}).get("QRL", {}).get("total", 0)
        usdt_total = snapshot.get("balances", {}).get("USDT", {}).get("total", 0)
        price = snapshot.get("prices", {}).get("QRLUSDT", 0)

        # Calculate portfolio metrics for debugging
        qrl_value = qrl_total * price
        total_value = qrl_value + usdt_total
        deviation_pct = (
            abs((qrl_value / total_value * 100) - 50) if total_value > 0 else 0
        )

        logger.info(
            f"[15-min-job] Balance snapshot - "
            f"QRL: {qrl_total:.4f}, "
            f"USDT: {usdt_total:.4f}, "
            f"Price: {price:.6f}, "
            f"QRL Value: {qrl_value:.2f} USDT, "
            f"Total Value: {total_value:.2f} USDT, "
            f"Deviation: {deviation_pct:.2f}% from 50/50, "
            f"Source: {snapshot.get('source', 'unknown')}"
        )

        rebalance_plan = await rebalance_service.generate_plan(snapshot)

        # Step 5: Execute order if action is BUY or SELL
        order_result = None
        if rebalance_plan.get("action") in ["BUY", "SELL"]:
            try:
                logger.info(
                    f"[15-min-job] Executing {rebalance_plan['action']} order - "
                    f"Quantity: {rebalance_plan['quantity']:.4f} QRL"
                )
                order = await mexc_client.place_market_order(
                    symbol=QRL_USDT_SYMBOL,
                    side=rebalance_plan["action"],
                    quantity=rebalance_plan["quantity"],
                )
                order_result = {
                    "executed": True,
                    "order_id": order.get("orderId"),
                    "status": order.get("status"),
                    "details": order,
                }
                logger.info(
                    f"[15-min-job] Order executed successfully - "
                    f"Order ID: {order.get('orderId')}, "
                    f"Status: {order.get('status')}"
                )
            except Exception as exc:
                order_result = {
                    "executed": False,
                    "error": str(exc),
                }
                logger.error(
                    f"[15-min-job] Order execution failed: {exc}", exc_info=True
                )
        else:
            logger.info(
                f"[15-min-job] No order executed - "
                f"Action: {rebalance_plan.get('action')}, "
                f"Reason: {rebalance_plan.get('reason')}"
            )

        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        logger.info(
            f"[15-min-job] Completed successfully in {duration_ms}ms - "
            f"Rebalance action: {rebalance_plan.get('action', 'UNKNOWN')}, "
            f"quantity: {rebalance_plan.get('quantity', 0):.4f}, "
            f"reason: {rebalance_plan.get('reason', 'N/A')}, "
            f"order_executed: {order_result.get('executed') if order_result else False}"
        )

        return {
            "status": "success",
            "task": "15-min-job",
            "auth": auth_method,
            "timestamp": end_time.isoformat(),
            "duration_ms": duration_ms,
            "cost_update": cost_update_result,
            "rebalance": rebalance_plan,
            "order": order_result,
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
