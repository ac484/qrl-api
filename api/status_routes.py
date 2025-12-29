"""
Status and health check API routes (aggregated).
"""
from fastapi import APIRouter

from api.status.dashboard import router as dashboard_router, root, dashboard
from api.status.api_info import router as api_info_router, api_info
from api.status.health import router as health_router, health_check, HealthResponse
from api.status.status import router as status_router, get_status, StatusResponse

router = APIRouter()
router.include_router(dashboard_router)
router.include_router(api_info_router)
router.include_router(health_router)
router.include_router(status_router)

__all__ = [
    "router",
    "root",
    "dashboard",
    "api_info",
    "health_check",
    "get_status",
    "HealthResponse",
    "StatusResponse",
]
