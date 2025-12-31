"""
Runtime keepalive task endpoint.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/runtime")
async def runtime_keepalive():
    """
    Lightweight runtime health endpoint for task keepalive probes.
    """
    return {"success": True, "message": "01-min-job"}


__all__ = ["router", "runtime_keepalive"]
