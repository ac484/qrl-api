"""
Helper functions for cost and P&L calculations.
Extracted from CostRepository for clearer responsibilities.
"""
from typing import Dict
import logging

from infrastructure.utils.type_safety import safe_float

logger = logging.getLogger(__name__)


def calculate_unrealized_pnl(avg_cost: float, current_price: float, current_quantity: float) -> Dict[str, float]:
    current_value = current_price * current_quantity
    cost_basis = avg_cost * current_quantity
    unrealized_pnl = current_value - cost_basis
    unrealized_pct = (unrealized_pnl / cost_basis) * 100 if cost_basis > 0 else 0
    return {
        "avg_cost": avg_cost,
        "current_value": current_value,
        "unrealized_pnl": unrealized_pnl,
        "unrealized_pnl_percent": unrealized_pct,
    }


def summarize_cost_data(cost_data: Dict[str, str], current_price: float, current_quantity: float) -> Dict[str, float]:
    try:
        avg_cost = safe_float(cost_data.get("avg_cost"))
        total_invested = safe_float(cost_data.get("total_invested"))
        realized_pnl = safe_float(cost_data.get("realized_pnl"))

        pnl = calculate_unrealized_pnl(avg_cost, current_price, current_quantity)
        pnl.update(
            {
                "total_invested": total_invested,
                "realized_pnl": realized_pnl,
                "total_pnl": pnl["unrealized_pnl"] + realized_pnl,
            }
        )
        return pnl
    except Exception as exc:  # pragma: no cover - defensive
        logger.error(f"Failed to summarize cost data: {exc}")
        return {
            "avg_cost": 0,
            "current_value": 0,
            "total_invested": 0,
            "unrealized_pnl": 0,
            "unrealized_pnl_percent": 0,
            "realized_pnl": 0,
            "total_pnl": 0,
        }


def update_after_buy_values(cost_data: Dict[str, str], buy_price: float, buy_amount_usdt: float) -> Dict[str, float]:
    old_total_invested = safe_float(cost_data.get("total_invested"))
    realized_pnl = safe_float(cost_data.get("realized_pnl"))
    new_total_invested = old_total_invested + buy_amount_usdt
    return {
        "avg_cost": buy_price,
        "total_invested": new_total_invested,
        "realized_pnl": realized_pnl,
    }


def update_after_sell_values(cost_data: Dict[str, str], avg_cost: float, sell_quantity: float, sell_amount_usdt: float) -> Dict[str, float]:
    realized_pnl = safe_float(cost_data.get("realized_pnl"))
    cost_basis = avg_cost * sell_quantity
    sale_pnl = sell_amount_usdt - cost_basis
    return {
        "avg_cost": avg_cost,
        "realized_pnl": realized_pnl + sale_pnl,
        "total_invested": max(0, safe_float(cost_data.get("total_invested")) - cost_basis),
    }

__all__ = [
    "calculate_unrealized_pnl",
    "summarize_cost_data",
    "update_after_buy_values",
    "update_after_sell_values",
]
