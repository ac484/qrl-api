"""
State Manager - Pure Redis state persistence logic

Responsibility: Manage bot state in Redis ONLY
Layer: Infrastructure (persistence)
"""
import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class StateManager:
    """
    Manage trading bot state persistence

    Single Responsibility: Save/load bot state from Redis
    No business logic, no orchestration, pure persistence
    """

    def __init__(self, redis_client):
        """
        Initialize state manager

        Args:
            redis_client: Redis client for state persistence
        """
        self.redis = redis_client

    async def get_bot_status(self) -> Dict:
        """
        Get current bot running status from Redis

        Returns:
            Dict with bot status {running: bool, ...}
        """
        try:
            status = await self.redis.get_bot_status()
            return status if status else {"running": False}
        except Exception as e:
            logger.error(f"Failed to get bot status: {str(e)}")
            return {"running": False, "error": str(e)}

    async def start_bot(self) -> Dict:
        """
        Set bot status to running in Redis

        Returns:
            Dict with success status and timestamp
        """
        try:
            await self.redis.set_bot_status(
                {"running": True, "started_at": datetime.now().isoformat()}
            )
            logger.info("Bot status set to running")
            return {
                "success": True,
                "message": "Bot started successfully",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def stop_bot(self) -> Dict:
        """
        Set bot status to stopped in Redis

        Returns:
            Dict with success status and timestamp
        """
        try:
            await self.redis.set_bot_status(
                {"running": False, "stopped_at": datetime.now().isoformat()}
            )
            logger.info("Bot status set to stopped")
            return {
                "success": True,
                "message": "Bot stopped successfully",
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Failed to stop bot: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def is_bot_running(self, bot_status: Dict) -> bool:
        """
        Check if bot is running from status dict

        Args:
            bot_status: Bot status dictionary

        Returns:
            True if bot is running, False otherwise
            Defaults to True if status is unknown (allow scheduled cycles)
        """
        running_flag = bot_status.get("running")
        # If status missing/unknown, assume running to allow scheduled cycles
        return running_flag if running_flag is not None else True
