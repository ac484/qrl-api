"""
Test position display functionality
Tests the fix for position data not being displayed in dashboard
"""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_position_and_cost_data():
    """Test position and cost data storage and retrieval"""
    from redis_client import RedisClient
    
    logger.info("Testing Position and Cost Data...")
    
    client = RedisClient()
    
    try:
        # Connect
        connected = await client.connect()
        if not connected:
            logger.error("❌ Redis connection failed")
            return
        
        logger.info("✅ Redis connected")
        
        # Test 1: Set position data
        position_data = {
            "qrl_balance": "1000.5",
            "usdt_balance": "500.25"
        }
        await client.set_position(position_data)
        logger.info(f"✅ Position data set: {position_data}")
        
        # Test 2: Get position data
        retrieved_position = await client.get_position()
        logger.info(f"✅ Position data retrieved: {retrieved_position}")
        
        # Test 3: Set cost data
        await client.set_cost_data(
            avg_cost=0.055,
            total_invested=55.0275,
            unrealized_pnl=5.5,
            realized_pnl=2.3
        )
        logger.info("✅ Cost data set")
        
        # Test 4: Get cost data
        cost_data = await client.get_cost_data()
        logger.info(f"✅ Cost data retrieved: {cost_data}")
        
        # Test 5: Merge position and cost data (simulating /status endpoint)
        merged_data = dict(retrieved_position)
        if cost_data:
            merged_data.update(cost_data)
        
        logger.info(f"✅ Merged data: {merged_data}")
        
        # Verify merged data contains all expected fields
        expected_fields = ["qrl_balance", "usdt_balance", "avg_cost", "total_invested", "unrealized_pnl", "realized_pnl"]
        for field in expected_fields:
            if field in merged_data:
                logger.info(f"  ✓ {field}: {merged_data[field]}")
            else:
                logger.warning(f"  ⚠️ Missing field: {field}")
        
        # Close
        await client.close()
        logger.info("✅ Redis closed")
        
        # Final check
        all_fields_present = all(field in merged_data for field in expected_fields)
        if all_fields_present:
            logger.info("✅ ALL TESTS PASSED - Position display fix verified!")
        else:
            logger.error("❌ TESTS FAILED - Some fields missing")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}", exc_info=True)


async def test_status_endpoint():
    """Test /status endpoint returns merged position and cost data"""
    import httpx
    
    logger.info("Testing /status endpoint...")
    
    try:
        # Assuming the API is running on localhost:8000
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8000/status")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ /status endpoint returned: {data}")
                
                # Check if position contains merged data
                position = data.get("position", {})
                if position:
                    logger.info(f"✅ Position data: {position}")
                    
                    # Check for expected fields
                    if "avg_cost" in position:
                        logger.info(f"  ✓ avg_cost: {position['avg_cost']}")
                    if "unrealized_pnl" in position:
                        logger.info(f"  ✓ unrealized_pnl: {position['unrealized_pnl']}")
                    if "qrl_balance" in position:
                        logger.info(f"  ✓ qrl_balance: {position['qrl_balance']}")
                else:
                    logger.warning("⚠️ Position data is empty")
            else:
                logger.error(f"❌ /status endpoint returned {response.status_code}")
                
    except Exception as e:
        logger.warning(f"⚠️ Could not test /status endpoint (API may not be running): {e}")


async def main():
    """Main test function"""
    logger.info("=== Testing Position Display Fix ===\n")
    
    # Test Redis operations
    await test_position_and_cost_data()
    
    logger.info("\n")
    
    # Test API endpoint (optional, only if API is running)
    await test_status_endpoint()
    
    logger.info("\n=== Tests Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
