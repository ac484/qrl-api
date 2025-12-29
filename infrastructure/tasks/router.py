"""
Aggregate task routers.
"""
from fastapi import APIRouter
from infrastructure.tasks.mexc_tasks import router as mexc_tasks_router

router = APIRouter()
router.include_router(mexc_tasks_router)

__all__ = ["router"]
