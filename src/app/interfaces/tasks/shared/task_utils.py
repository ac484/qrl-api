"""
Shared utility functions for Cloud Scheduler tasks.

This module provides common functionality for authentication,
Redis connection management, and error handling across all
scheduled tasks.
"""

import logging
from typing import Optional

from fastapi import HTTPException

from src.app.infrastructure.external import RedisClient

logger = logging.getLogger(__name__)


def require_scheduler_auth(
    x_cloudscheduler: Optional[str] = None,
    authorization: Optional[str] = None,
) -> str:
    """
    Validate Cloud Scheduler authentication.

    Accepts either X-CloudScheduler header or OIDC Authorization header.
    This is a security requirement - only Cloud Scheduler should be able
    to trigger these endpoints.

    Args:
        x_cloudscheduler: X-CloudScheduler header value
        authorization: Authorization header value (OIDC token)

    Returns:
        str: Authentication method used ("X-CloudScheduler" or "OIDC")

    Raises:
        HTTPException: 401 if neither auth method is present
    """
    if not x_cloudscheduler and not authorization:
        logger.warning("Unauthorized task access attempt - no valid auth headers")
        raise HTTPException(
            status_code=401,
            detail="Unauthorized - Cloud Scheduler authentication required",
        )

    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"Task authenticated via {auth_method}")
    return auth_method


async def ensure_redis_connected(redis_client: RedisClient) -> None:
    """
    Ensure Redis client is connected.

    Args:
        redis_client: RedisClient instance to check/connect

    Raises:
        HTTPException: 503 if Redis connection fails
    """
    try:
        if not redis_client.connected:
            logger.info("Redis not connected, establishing connection...")
            await redis_client.connect()
            logger.info("Redis connection established")
    except Exception as exc:
        logger.error(f"Failed to connect to Redis: {exc}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail=f"Redis connection failed: {str(exc)}",
        )


__all__ = [
    "require_scheduler_auth",
    "ensure_redis_connected",
]
