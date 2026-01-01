"""
Tests for shared task utilities.
"""

import pytest
from fastapi import HTTPException

from src.app.interfaces.tasks.shared.task_utils import (
    ensure_redis_connected,
    require_scheduler_auth,
)


class MockRedisClient:
    """Mock Redis client for testing."""

    def __init__(self, connected=False, should_fail=False):
        self.connected = connected
        self.should_fail = should_fail
        self.connect_called = False

    async def connect(self):
        """Mock connect method."""
        self.connect_called = True
        if self.should_fail:
            raise Exception("Connection failed")
        self.connected = True


def test_require_scheduler_auth_with_cloudscheduler_header():
    """Test authentication with X-CloudScheduler header."""
    result = require_scheduler_auth(x_cloudscheduler="true", authorization=None)
    assert result == "X-CloudScheduler"


def test_require_scheduler_auth_with_oidc_token():
    """Test authentication with OIDC Authorization header."""
    result = require_scheduler_auth(
        x_cloudscheduler=None, authorization="Bearer token"
    )
    assert result == "OIDC"


def test_require_scheduler_auth_prefers_oidc_when_both_present():
    """Test that OIDC is preferred when both headers are present."""
    result = require_scheduler_auth(
        x_cloudscheduler="true", authorization="Bearer token"
    )
    assert result == "OIDC"


def test_require_scheduler_auth_fails_without_headers():
    """Test that authentication fails without valid headers."""
    with pytest.raises(HTTPException) as exc_info:
        require_scheduler_auth(x_cloudscheduler=None, authorization=None)

    assert exc_info.value.status_code == 401
    assert "Cloud Scheduler authentication required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_ensure_redis_connected_when_already_connected():
    """Test Redis connection check when already connected."""
    redis = MockRedisClient(connected=True)
    await ensure_redis_connected(redis)
    assert not redis.connect_called  # Should not call connect again


@pytest.mark.asyncio
async def test_ensure_redis_connected_when_not_connected():
    """Test Redis connection establishment when not connected."""
    redis = MockRedisClient(connected=False)
    await ensure_redis_connected(redis)
    assert redis.connect_called
    assert redis.connected


@pytest.mark.asyncio
async def test_ensure_redis_connected_fails_gracefully():
    """Test Redis connection failure handling."""
    redis = MockRedisClient(connected=False, should_fail=True)

    with pytest.raises(HTTPException) as exc_info:
        await ensure_redis_connected(redis)

    assert exc_info.value.status_code == 503
    assert "Redis connection failed" in exc_info.value.detail
