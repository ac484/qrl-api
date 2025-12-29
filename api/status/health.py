"""Health check route."""
from datetime import datetime
import logging
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Status"])
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    redis_connected: bool
    mexc_api_configured: bool
    timestamp: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    from infrastructure.config import config

    mexc_api_configured = bool(config.MEXC_API_KEY and config.MEXC_SECRET_KEY)
    status = "healthy" if mexc_api_configured else "degraded"
    logger.info(f"Health check: {status} (MEXC: {mexc_api_configured})")
    return HealthResponse(
        status=status,
        redis_connected=False,
        mexc_api_configured=mexc_api_configured,
        timestamp=datetime.now().isoformat(),
    )
