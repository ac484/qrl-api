"""
Test script to verify Redis TTL fixes and complete MEXC response storage

This test verifies:
1. Account balance is stored without TTL
2. Complete MEXC account fields are stored
3. Raw MEXC responses are stored permanently
"""
import asyncio
import json
import logging
from datetime import datetime
from redis_client import redis_client
from config import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_account_balance_no_ttl():
    """Test that account balance is stored without TTL"""
    logger.info("\n=== Test 1: Account Balance Storage (No TTL) ===")
    
    # Connect to Redis
    if not await redis_client.connect():
        logger.error("Failed to connect to Redis")
        return False
    
    # Create test account balance data with all MEXC fields
    test_data = {
        "success": True,
        "balances": {
            "QRL": {"free": "100.00", "locked": "0.00"},
            "USDT": {"free": "1000.00", "locked": "50.00"}
        },
        "makerCommission": 10,
        "takerCommission": 10,
        "canTrade": True,
        "canWithdraw": True,
        "canDeposit": True,
        "updateTime": int(datetime.now().timestamp() * 1000),
        "accountType": "SPOT",
        "permissions": ["SPOT"],
        "timestamp": datetime.now().isoformat()
    }
    
    # Store the data
    logger.info("Storing account balance...")
    success = await redis_client.set_account_balance(test_data)
    
    if not success:
        logger.error("Failed to store account balance")
        return False
    
    logger.info("✓ Account balance stored successfully")
    
    # Retrieve and verify the data
    logger.info("Retrieving account balance...")
    retrieved_data = await redis_client.get_account_balance()
    
    if not retrieved_data:
        logger.error("Failed to retrieve account balance")
        return False
    
    logger.info(f"✓ Retrieved account balance")
    
    # Verify all fields are present
    required_fields = [
        "balances", "makerCommission", "takerCommission", "canTrade",
        "canWithdraw", "canDeposit", "updateTime", "accountType", "permissions"
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in retrieved_data:
            missing_fields.append(field)
    
    if missing_fields:
        logger.error(f"Missing fields: {missing_fields}")
        return False
    
    logger.info(f"✓ All required fields present: {required_fields}")
    
    # Check TTL (should be -1 for no TTL)
    key = f"account:balance"
    ttl = await redis_client.client.ttl(key)
    
    logger.info(f"TTL for account:balance: {ttl}")
    
    if ttl == -1:
        logger.info("✓ Account balance has no TTL (permanent storage)")
        return True
    elif ttl == -2:
        logger.error("✗ Key does not exist")
        return False
    else:
        logger.error(f"✗ Account balance has TTL: {ttl} seconds (should be -1 for permanent)")
        return False


async def test_raw_mexc_response_storage():
    """Test that raw MEXC responses are stored permanently"""
    logger.info("\n=== Test 2: Raw MEXC Response Storage ===")
    
    # Create test MEXC response
    test_response = {
        "makerCommission": 10,
        "takerCommission": 10,
        "canTrade": True,
        "canWithdraw": True,
        "canDeposit": True,
        "updateTime": int(datetime.now().timestamp() * 1000),
        "accountType": "SPOT",
        "balances": [
            {"asset": "QRL", "free": "100.00", "locked": "0.00"},
            {"asset": "USDT", "free": "1000.00", "locked": "50.00"}
        ],
        "permissions": ["SPOT"]
    }
    
    # Store the raw response
    logger.info("Storing raw MEXC response...")
    success = await redis_client.set_raw_mexc_response(
        endpoint="account_info",
        response_data=test_response,
        metadata={"source": "test_script"}
    )
    
    if not success:
        logger.error("Failed to store raw MEXC response")
        return False
    
    logger.info("✓ Raw MEXC response stored successfully")
    
    # Retrieve and verify
    key = f"mexc:raw:account_info:latest"
    data = await redis_client.client.get(key)
    
    if not data:
        logger.error("Failed to retrieve raw MEXC response")
        return False
    
    retrieved = json.loads(data)
    logger.info(f"✓ Retrieved raw MEXC response")
    
    # Verify the response contains all original fields
    if "response" not in retrieved:
        logger.error("Missing 'response' field in stored data")
        return False
    
    original_fields = list(test_response.keys())
    stored_fields = list(retrieved["response"].keys())
    
    logger.info(f"Original fields: {original_fields}")
    logger.info(f"Stored fields: {stored_fields}")
    
    missing = set(original_fields) - set(stored_fields)
    if missing:
        logger.error(f"Missing fields in stored response: {missing}")
        return False
    
    logger.info("✓ All original fields present in stored response")
    
    # Check TTL
    ttl = await redis_client.client.ttl(key)
    logger.info(f"TTL for mexc:raw:account_info:latest: {ttl}")
    
    if ttl == -1:
        logger.info("✓ Raw MEXC response has no TTL (permanent storage)")
        return True
    elif ttl == -2:
        logger.error("✗ Key does not exist")
        return False
    else:
        logger.error(f"✗ Raw MEXC response has TTL: {ttl} seconds (should be -1)")
        return False


async def main():
    """Run all tests"""
    logger.info("Starting Redis TTL Fix Tests")
    logger.info(f"Redis URL: {config.REDIS_URL or f'{config.REDIS_HOST}:{config.REDIS_PORT}'}")
    
    try:
        # Run tests
        test1_passed = await test_account_balance_no_ttl()
        test2_passed = await test_raw_mexc_response_storage()
        
        # Summary
        logger.info("\n=== Test Summary ===")
        logger.info(f"Test 1 (Account Balance No TTL): {'PASSED' if test1_passed else 'FAILED'}")
        logger.info(f"Test 2 (Raw MEXC Response Storage): {'PASSED' if test2_passed else 'FAILED'}")
        
        if test1_passed and test2_passed:
            logger.info("\n✓ All tests PASSED")
            return 0
        else:
            logger.error("\n✗ Some tests FAILED")
            return 1
    
    finally:
        # Cleanup
        await redis_client.close()


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
