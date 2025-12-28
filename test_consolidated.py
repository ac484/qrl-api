"""
Consolidated test suite for QRL Trading API
Merges common test patterns from multiple test files to reduce duplication
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from config import config
from redis_client import redis_client
from mexc_client import mexc_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestRedisOperations:
    """Consolidated Redis operation tests"""
    
    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test Redis connection and health check"""
        connected = await redis_client.connect()
        assert connected, "Failed to connect to Redis"
        
        health = await redis_client.health_check()
        assert health, "Redis health check failed"
    
    @pytest.mark.asyncio
    async def test_bot_status_operations(self):
        """Test bot status set/get operations"""
        # Set status
        result = await redis_client.set_bot_status("running", {"test": True})
        assert result, "Failed to set bot status"
        
        # Get status
        status = await redis_client.get_bot_status()
        assert status.get("status") == "running"
        assert status.get("metadata", {}).get("test") is True
    
    @pytest.mark.asyncio
    async def test_position_operations(self):
        """Test position data operations"""
        test_position = {
            "qrl_balance": "100.5",
            "usdt_balance": "500.25",
            "total_value": "600.75"
        }
        
        # Set position
        result = await redis_client.set_position(test_position)
        assert result, "Failed to set position"
        
        # Get position
        position = await redis_client.get_position()
        assert float(position.get("qrl_balance", 0)) == 100.5
    
    @pytest.mark.asyncio
    async def test_price_caching(self):
        """Test price caching with TTL"""
        test_price = 0.123456
        test_volume = 1000.0
        
        # Set cached price
        await redis_client.set_cached_price(test_price, test_volume)
        
        # Get cached price
        price_data = await redis_client.get_cached_price()
        assert price_data is not None
        assert abs(float(price_data.get("price", 0)) - test_price) < 0.000001


class TestMEXCAPIIntegration:
    """Consolidated MEXC API integration tests"""
    
    @pytest.mark.asyncio
    async def test_get_ticker_with_mock(self):
        """Test ticker fetching with mocked response"""
        mock_ticker = {
            "symbol": "QRLUSDT",
            "lastPrice": "0.123456",
            "volume": "1000.0"
        }
        
        with patch.object(mexc_client, 'get_ticker_24hr', new=AsyncMock(return_value=mock_ticker)):
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            assert ticker["symbol"] == "QRLUSDT"
            assert ticker["lastPrice"] == "0.123456"
    
    @pytest.mark.asyncio
    async def test_account_balance_with_mock(self):
        """Test account balance fetching with mocked response"""
        mock_balance = {
            "balances": [
                {"asset": "QRL", "free": "100.0", "locked": "0.0"},
                {"asset": "USDT", "free": "500.0", "locked": "0.0"}
            ]
        }
        
        with patch.object(mexc_client, 'get_account_info', new=AsyncMock(return_value=mock_balance)):
            balance = await mexc_client.get_account_info()
            assert len(balance["balances"]) == 2


class TestConfigurationManagement:
    """Consolidated configuration tests"""
    
    def test_broker_mode_detection(self):
        """Test broker mode configuration"""
        # Test SPOT mode
        assert not config.is_broker_mode or config.SUB_ACCOUNT_MODE == "BROKER"
    
    def test_cache_ttl_configuration(self):
        """Test cache TTL settings"""
        assert config.CACHE_TTL_PRICE > 0
        assert config.CACHE_TTL_TICKER > 0
        assert config.CACHE_TTL_ACCOUNT > 0
    
    def test_trading_symbol_configuration(self):
        """Test trading symbol configuration"""
        assert config.TRADING_SYMBOL == "QRLUSDT"
        assert config.TRADING_SYMBOL.endswith("USDT")


class TestDataFlow:
    """Test end-to-end data flow"""
    
    @pytest.mark.asyncio
    async def test_price_update_flow(self):
        """Test complete price update flow: MEXC -> Redis -> Cache"""
        mock_ticker = {
            "symbol": "QRLUSDT",
            "lastPrice": "0.123456",
            "volume": "1000.0",
            "priceChange": "0.001",
            "priceChangePercent": "0.81"
        }
        
        with patch.object(mexc_client, 'get_ticker_24hr', new=AsyncMock(return_value=mock_ticker)):
            # Fetch from MEXC
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            
            # Store in Redis
            price = float(ticker["lastPrice"])
            volume = float(ticker["volume"])
            await redis_client.set_latest_price(price, volume)
            
            # Verify stored data
            stored_price = await redis_client.get_latest_price()
            assert stored_price is not None
            assert abs(float(stored_price.get("price", 0)) - price) < 0.000001
    
    @pytest.mark.asyncio
    async def test_balance_update_flow(self):
        """Test complete balance update flow: MEXC -> Redis -> Processing"""
        mock_account = {
            "balances": [
                {"asset": "QRL", "free": "100.0", "locked": "0.0"},
                {"asset": "USDT", "free": "500.0", "locked": "0.0"}
            ],
            "accountType": "SPOT",
            "canTrade": True
        }
        
        with patch.object(mexc_client, 'get_account_info', new=AsyncMock(return_value=mock_account)):
            # Fetch from MEXC
            account = await mexc_client.get_account_info()
            
            # Process balances
            qrl_balance = 0.0
            usdt_balance = 0.0
            for balance in account["balances"]:
                if balance["asset"] == "QRL":
                    qrl_balance = float(balance["free"])
                elif balance["asset"] == "USDT":
                    usdt_balance = float(balance["free"])
            
            # Store in Redis
            position_data = {
                "qrl_balance": str(qrl_balance),
                "usdt_balance": str(usdt_balance)
            }
            await redis_client.set_position(position_data)
            
            # Verify
            position = await redis_client.get_position()
            assert float(position.get("qrl_balance", 0)) == 100.0
            assert float(position.get("usdt_balance", 0)) == 500.0


async def run_all_tests():
    """Run all tests"""
    logger.info("Starting consolidated test suite...")
    
    # Connect to Redis
    await redis_client.connect()
    
    try:
        # Run test classes
        test_redis = TestRedisOperations()
        await test_redis.test_redis_connection()
        await test_redis.test_bot_status_operations()
        await test_redis.test_position_operations()
        await test_redis.test_price_caching()
        
        test_config = TestConfigurationManagement()
        test_config.test_broker_mode_detection()
        test_config.test_cache_ttl_configuration()
        test_config.test_trading_symbol_configuration()
        
        test_flow = TestDataFlow()
        await test_flow.test_price_update_flow()
        await test_flow.test_balance_update_flow()
        
        logger.info("✅ All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        raise
    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(run_all_tests())
