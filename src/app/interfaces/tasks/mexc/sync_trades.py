"""
Cloud task entrypoint for trade/cost update.

Delegates to the legacy handler to preserve existing behavior.
Renamed from /15-min-job to /sync-trades to avoid path conflict.
"""

from fastapi import APIRouter

from src.app.application.market.sync_cost import task_update_cost

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])
router.add_api_route("/sync-trades", task_update_cost, methods=["POST"])

__all__ = ["router"]
