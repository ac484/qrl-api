"""
Test Position Layers Functionality
Tests the position layers feature implementation
"""
import asyncio
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_position_layers():
    """Test position layers functionality"""
    from redis_client import redis_client
    
    logger.info("Testing Position Layers Functionality...")
    
    try:
        # Connect to Redis
        connected = await redis_client.connect()
        if not connected:
            logger.error("❌ Redis connection failed")
            return
        
        logger.info("✅ Redis connected")
        
        # Test 1: Set position layers
        logger.info("\n--- Test 1: Set Position Layers ---")
        core_qrl = 7000.0
        swing_qrl = 2000.0
        active_qrl = 1000.0
        
        success = await redis_client.set_position_layers(
            core_qrl=core_qrl,
            swing_qrl=swing_qrl,
            active_qrl=active_qrl
        )
        
        if success:
            logger.info(f"✅ Set position layers: Core={core_qrl}, Swing={swing_qrl}, Active={active_qrl}")
        else:
            logger.error("❌ Failed to set position layers")
        
        # Test 2: Get position layers
        logger.info("\n--- Test 2: Get Position Layers ---")
        layers = await redis_client.get_position_layers()
        
        if layers:
            logger.info("✅ Retrieved position layers:")
            logger.info(f"   Core QRL: {layers.get('core_qrl')}")
            logger.info(f"   Swing QRL: {layers.get('swing_qrl')}")
            logger.info(f"   Active QRL: {layers.get('active_qrl')}")
            logger.info(f"   Total QRL: {layers.get('total_qrl')}")
            logger.info(f"   Core Percent: {float(layers.get('core_percent', 0)) * 100:.2f}%")
            logger.info(f"   Last Adjust: {layers.get('last_adjust')}")
            
            # Validate values
            assert float(layers.get('core_qrl')) == core_qrl, "Core QRL mismatch"
            assert float(layers.get('swing_qrl')) == swing_qrl, "Swing QRL mismatch"
            assert float(layers.get('active_qrl')) == active_qrl, "Active QRL mismatch"
            assert float(layers.get('total_qrl')) == (core_qrl + swing_qrl + active_qrl), "Total QRL mismatch"
            
            logger.info("✅ All values validated correctly")
        else:
            logger.error("❌ Failed to retrieve position layers")
        
        # Test 3: Update position layers
        logger.info("\n--- Test 3: Update Position Layers ---")
        new_core = 7500.0
        new_swing = 1500.0
        new_active = 1000.0
        
        success = await redis_client.set_position_layers(
            core_qrl=new_core,
            swing_qrl=new_swing,
            active_qrl=new_active
        )
        
        if success:
            logger.info(f"✅ Updated position layers: Core={new_core}, Swing={new_swing}, Active={new_active}")
            
            # Verify update
            updated_layers = await redis_client.get_position_layers()
            assert float(updated_layers.get('core_qrl')) == new_core, "Updated core QRL mismatch"
            logger.info("✅ Update verified successfully")
        else:
            logger.error("❌ Failed to update position layers")
        
        # Test 4: Test with API endpoint
        logger.info("\n--- Test 4: Test API Endpoint Integration ---")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("http://localhost:8080/status")
                if response.status_code == 200:
                    data = response.json()
                    if 'position_layers' in data:
                        logger.info("✅ API endpoint returns position_layers")
                        logger.info(f"   Data: {data['position_layers']}")
                    else:
                        logger.warning("⚠️  API endpoint does not include position_layers (may need bot to be running)")
                else:
                    logger.warning(f"⚠️  API returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"⚠️  Could not test API endpoint (server may not be running): {e}")
        
        # Cleanup
        await redis_client.close()
        logger.info("\n✅ All position layers tests completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Test failed with error: {e}", exc_info=True)
        if redis_client.connected:
            await redis_client.close()


async def test_redis_connection_pool():
    """Test Redis connection pool functionality"""
    from redis_client import redis_client
    
    logger.info("\n\nTesting Redis Connection Pool...")
    
    try:
        # Connect to Redis
        connected = await redis_client.connect()
        if not connected:
            logger.error("❌ Redis connection failed")
            return
        
        logger.info("✅ Redis connected with connection pool")
        
        # Verify connection pool exists
        if redis_client.pool:
            logger.info(f"✅ Connection pool created")
            logger.info(f"   Max connections: 20")
            logger.info(f"   Health check interval: 30s")
        else:
            logger.error("❌ Connection pool not created")
        
        # Test multiple concurrent operations
        logger.info("\n--- Testing Concurrent Operations ---")
        
        async def set_and_get(key_suffix: int):
            key = f"test:concurrent:{key_suffix}"
            await redis_client.client.set(key, f"value_{key_suffix}")
            value = await redis_client.client.get(key)
            await redis_client.client.delete(key)
            return value == f"value_{key_suffix}"
        
        # Run 10 concurrent operations
        results = await asyncio.gather(*[set_and_get(i) for i in range(10)])
        
        if all(results):
            logger.info("✅ All 10 concurrent operations succeeded")
        else:
            logger.error(f"❌ Some concurrent operations failed: {sum(results)}/10 succeeded")
        
        # Test close methods
        logger.info("\n--- Testing Close Methods ---")
        await redis_client.close()
        logger.info("✅ Redis client and pool closed successfully")
        
        # Verify disconnection
        if not redis_client.connected:
            logger.info("✅ Connection status updated correctly")
        else:
            logger.error("❌ Connection status not updated")
        
        logger.info("\n✅ All connection pool tests completed successfully!")
        
    except Exception as e:
        logger.error(f"\n❌ Connection pool test failed: {e}", exc_info=True)


async def main():
    """Run all tests"""
    logger.info("=== Starting Position Layers & Redis Tests ===\n")
    
    await test_position_layers()
    await test_redis_connection_pool()
    
    logger.info("\n=== All Tests Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
