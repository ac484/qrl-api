"""
簡單的 API 測試腳本
測試 MEXC API 和 Redis 連接
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mexc_api():
    """測試 MEXC API 連接"""
    from mexc_client import MEXCClient
    
    logger.info("Testing MEXC API...")
    
    async with MEXCClient() as client:
        # Test ping
        try:
            ping_result = await client.ping()
            logger.info(f"✅ Ping: {ping_result}")
        except Exception as e:
            logger.error(f"❌ Ping failed: {e}")
        
        # Test server time
        try:
            time_result = await client.get_server_time()
            logger.info(f"✅ Server time: {time_result}")
        except Exception as e:
            logger.error(f"❌ Server time failed: {e}")
        
        # Test ticker
        try:
            ticker = await client.get_ticker_price("QRLUSDT")
            logger.info(f"✅ QRL/USDT Price: {ticker}")
        except Exception as e:
            logger.error(f"❌ Get ticker failed: {e}")


async def test_redis():
    """測試 Redis 連接"""
    from redis_client import RedisClient
    
    logger.info("Testing Redis...")
    
    client = RedisClient()
    
    try:
        # Connect
        connected = await client.connect()
        if connected:
            logger.info("✅ Redis connected")
        else:
            logger.error("❌ Redis connection failed")
            return
        
        # Health check
        health = await client.health_check()
        logger.info(f"✅ Redis health check: {health}")
        
        # Set and get bot status
        await client.set_bot_status("testing", {"test": "data"})
        status = await client.get_bot_status()
        logger.info(f"✅ Bot status: {status}")
        
        # Set latest price
        await client.set_latest_price(0.055, 1000000)
        price = await client.get_latest_price()
        logger.info(f"✅ Latest price: {price}")
        
        # Close
        await client.close()
        logger.info("✅ Redis closed")
        
    except Exception as e:
        logger.error(f"❌ Redis test failed: {e}")


async def main():
    """主測試函數"""
    logger.info("=== Starting API Tests ===\n")
    
    # Test MEXC API
    await test_mexc_api()
    
    logger.info("\n")
    
    # Test Redis (需要 Redis 運行)
    try:
        await test_redis()
    except Exception as e:
        logger.warning(f"⚠️ Redis test skipped (Redis not available): {e}")
    
    logger.info("\n=== Tests Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
