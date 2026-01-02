"""
Debug endpoint to diagnose rebalance issues.

This endpoint provides detailed information about:
- Current portfolio balance
- Rebalance plan calculation
- Threshold checks
- What would happen if order were placed
"""

import logging
from typing import Optional

from fastapi import APIRouter, Header

from src.app.application.account.balance_service import BalanceService
from src.app.application.trading.services.trading.rebalance_service import (
    RebalanceService,
)
from src.app.infrastructure.external import mexc_client, redis_client, QRL_USDT_SYMBOL
from src.app.infrastructure.utils import safe_float

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Debug"])


@router.get("/debug/rebalance-status")
async def debug_rebalance_status():
    """
    Get detailed rebalance status without requiring authentication.
    
    Returns comprehensive information about:
    - Current portfolio state
    - Calculated rebalance plan
    - Threshold checks and why decisions are made
    - Exchange constraints (min order size, etc.)
    
    Use this to diagnose why rebalance isn't triggering.
    """
    try:
        # Get balance snapshot
        balance_service = BalanceService(mexc_client, redis_client)
        snapshot = await balance_service.get_account_balance()
        
        # Generate rebalance plan
        rebalance_service = RebalanceService(balance_service, redis_client)
        plan = rebalance_service.compute_plan(snapshot)
        
        # Extract key values
        qrl_data = snapshot.get("balances", {}).get("QRL", {})
        usdt_data = snapshot.get("balances", {}).get("USDT", {})
        price_entry = snapshot.get("prices", {}).get(QRL_USDT_SYMBOL)
        price = safe_float(price_entry or qrl_data.get("price"))
        
        qrl_total = safe_float(qrl_data.get("total", 0))
        qrl_available = safe_float(qrl_data.get("available", 0))
        usdt_total = safe_float(usdt_data.get("total", 0))
        usdt_available = safe_float(usdt_data.get("available", 0))
        
        total_value = qrl_total * price + usdt_total
        target_value = total_value * 0.5
        qrl_value = qrl_total * price
        delta = qrl_value - target_value
        notional = abs(delta)
        
        # Calculate thresholds
        min_notional_usdt = rebalance_service.min_notional_usdt
        threshold_pct = rebalance_service.threshold_pct
        deviation_pct = (notional / total_value * 100) if total_value > 0 else 0
        
        # Check conditions
        checks = {
            "price_valid": price > 0,
            "total_value_valid": total_value > 0,
            "notional_exceeds_min": notional >= min_notional_usdt,
            "deviation_exceeds_threshold": (notional / total_value) >= threshold_pct if total_value > 0 else False,
            "has_available_qrl": qrl_available > 0,
            "has_available_usdt": usdt_available > 0,
        }
        
        # Calculate portfolio ratios
        qrl_ratio = (qrl_value / total_value * 100) if total_value > 0 else 0
        usdt_ratio = (usdt_total / total_value * 100) if total_value > 0 else 0
        
        # Get exchange info for min order size
        try:
            exchange_info = await mexc_client.get_exchange_info(QRL_USDT_SYMBOL)
            symbol_info = exchange_info.get("symbols", [{}])[0] if exchange_info.get("symbols") else {}
            filters = {f.get("filterType"): f for f in symbol_info.get("filters", [])}
            lot_size = filters.get("LOT_SIZE", {})
            min_notional = filters.get("MIN_NOTIONAL", {})
        except Exception as e:
            logger.warning(f"Could not fetch exchange info: {e}")
            lot_size = {}
            min_notional = {}
        
        return {
            "status": "success",
            "timestamp": plan.get("timestamp"),
            "portfolio": {
                "qrl_total": qrl_total,
                "qrl_available": qrl_available,
                "qrl_locked": qrl_total - qrl_available,
                "usdt_total": usdt_total,
                "usdt_available": usdt_available,
                "usdt_locked": usdt_total - usdt_available,
                "price": price,
                "qrl_value_usdt": qrl_value,
                "total_value_usdt": total_value,
                "qrl_ratio_pct": round(qrl_ratio, 2),
                "usdt_ratio_pct": round(usdt_ratio, 2),
            },
            "rebalance_plan": plan,
            "threshold_analysis": {
                "notional_usdt": notional,
                "min_notional_usdt": min_notional_usdt,
                "deviation_pct": round(deviation_pct, 2),
                "threshold_pct": threshold_pct * 100,
                "delta_from_target": delta,
                "target_qrl_value": target_value,
                "current_qrl_value": qrl_value,
            },
            "condition_checks": checks,
            "should_trade": all([
                checks["price_valid"],
                checks["total_value_valid"],
                checks["notional_exceeds_min"],
                checks["deviation_exceeds_threshold"],
            ]),
            "exchange_constraints": {
                "min_qty": lot_size.get("minQty"),
                "max_qty": lot_size.get("maxQty"),
                "step_size": lot_size.get("stepSize"),
                "min_notional": min_notional.get("minNotional"),
            },
        }
        
    except Exception as exc:
        logger.error(f"Debug endpoint failed: {exc}", exc_info=True)
        return {
            "status": "error",
            "error": str(exc),
        }


__all__ = ["router"]
