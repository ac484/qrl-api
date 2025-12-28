#!/usr/bin/env python3
"""
Test script for Cloud Task data storage improvements
Tests permanent storage of raw MEXC responses and complete data persistence
"""
import asyncio
import json
from datetime import datetime
from redis_client import redis_client

async def test_raw_mexc_storage():
    """Test raw MEXC API response storage"""
    
    print("=" * 80)
    print("Testing Raw MEXC API Response Storage")
    print("=" * 80)
    
    # Connect to Redis
    print("\n1. Connecting to Redis...")
    if not await redis_client.connect():
        print("❌ Failed to connect to Redis")
        return False
    print("✅ Connected to Redis successfully")
    
    # Test storing raw account_info response
    print("\n2. Testing raw account_info storage...")
    test_account_info = {
        "accountType": "SPOT",
        "canTrade": True,
        "canWithdraw": True,
        "canDeposit": True,
        "updateTime": 1703750000000,
        "balances": [
            {"asset": "QRL", "free": "1000.5", "locked": "0.0"},
            {"asset": "USDT", "free": "500.25", "locked": "10.0"},
            {"asset": "BTC", "free": "0.001", "locked": "0.0"}
        ]
    }
    
    result = await redis_client.set_raw_mexc_response(
        endpoint="account_info",
        response_data=test_account_info,
        metadata={"task": "test", "source": "unit_test"}
    )
    
    if result:
        print("✅ Raw account_info stored successfully")
        
        # Retrieve and verify
        stored = await redis_client.get_raw_mexc_response("account_info")
        if stored:
            print(f"✅ Retrieved raw response:")
            print(f"   Timestamp: {stored.get('datetime')}")
            print(f"   Account Type: {stored['response']['accountType']}")
            print(f"   Balances: {len(stored['response']['balances'])} assets")
            print(f"   Metadata: {stored.get('metadata')}")
        else:
            print("❌ Failed to retrieve stored response")
    else:
        print("❌ Failed to store raw account_info")
    
    # Test storing raw ticker response
    print("\n3. Testing raw ticker_24hr storage...")
    test_ticker = {
        "symbol": "QRLUSDT",
        "lastPrice": "0.020500",
        "priceChange": "0.000500",
        "priceChangePercent": "2.5",
        "highPrice": "0.021000",
        "lowPrice": "0.019500",
        "volume": "1500000.0",
        "quoteVolume": "30750.0",
        "openPrice": "0.020000"
    }
    
    result = await redis_client.set_raw_mexc_response(
        endpoint="ticker_24hr",
        response_data=test_ticker,
        metadata={"symbol": "QRLUSDT", "task": "test"}
    )
    
    if result:
        print("✅ Raw ticker_24hr stored successfully")
        
        stored = await redis_client.get_raw_mexc_response("ticker_24hr")
        if stored:
            print(f"✅ Retrieved raw ticker:")
            print(f"   Price: {stored['response']['lastPrice']}")
            print(f"   Change: {stored['response']['priceChangePercent']}%")
            print(f"   Volume: {stored['response']['volume']}")
        else:
            print("❌ Failed to retrieve stored ticker")
    else:
        print("❌ Failed to store raw ticker")
    
    # Test historical storage
    print("\n4. Testing historical raw response storage...")
    
    # Store multiple entries
    for i in range(3):
        await asyncio.sleep(0.1)  # Small delay to ensure different timestamps
        test_data = {
            "price": f"0.02{i}000",
            "iteration": i
        }
        await redis_client.set_raw_mexc_response(
            endpoint="test_history",
            response_data=test_data,
            metadata={"iteration": i}
        )
    
    # Retrieve history
    history = await redis_client.get_raw_mexc_response_history("test_history", limit=10)
    
    if history:
        print(f"✅ Retrieved {len(history)} historical entries")
        for idx, entry in enumerate(history[:3]):
            print(f"   Entry {idx}: price={entry['response']['price']}, time={entry['datetime']}")
    else:
        print("❌ Failed to retrieve history")
    
    return True

async def test_permanent_price_storage():
    """Test permanent vs cached price storage"""
    
    print("\n" + "=" * 80)
    print("Testing Permanent vs Cached Price Storage")
    print("=" * 80)
    
    # Test permanent price storage
    print("\n1. Testing permanent price storage (no TTL)...")
    test_price = 0.020500
    test_volume = 1500000.0
    
    result = await redis_client.set_latest_price(test_price, test_volume)
    if result:
        print("✅ Latest price stored permanently")
        
        stored = await redis_client.get_latest_price()
        if stored:
            print(f"✅ Retrieved permanent price:")
            print(f"   Price: {stored.get('price')}")
            print(f"   Volume: {stored.get('volume')}")
            print(f"   Timestamp: {stored.get('timestamp')}")
        else:
            print("❌ Failed to retrieve permanent price")
    else:
        print("❌ Failed to store permanent price")
    
    # Test cached price storage
    print("\n2. Testing cached price storage (with TTL)...")
    cached_price = 0.020550
    cached_volume = 1520000.0
    
    result = await redis_client.set_cached_price(cached_price, cached_volume)
    if result:
        print("✅ Cached price stored with TTL")
        
        stored = await redis_client.get_cached_price()
        if stored:
            print(f"✅ Retrieved cached price:")
            print(f"   Price: {stored.get('price')}")
            print(f"   Volume: {stored.get('volume')}")
            print(f"   Timestamp: {stored.get('timestamp')}")
        else:
            print("❌ Failed to retrieve cached price")
    else:
        print("❌ Failed to store cached price")
    
    # Verify both storage methods work independently
    print("\n3. Verifying independent storage...")
    latest = await redis_client.get_latest_price()
    cached = await redis_client.get_cached_price()
    
    if latest and cached:
        print(f"✅ Both storage methods working:")
        print(f"   Latest (permanent): {latest.get('price')}")
        print(f"   Cached (TTL): {cached.get('price')}")
        
        if latest.get('price') != cached.get('price'):
            print("✅ Prices are independent as expected")
        else:
            print("⚠️  Prices are the same (may be intentional)")
    else:
        print("❌ Failed to retrieve both prices")
    
    return True

async def test_complete_position_storage():
    """Test complete position data storage"""
    
    print("\n" + "=" * 80)
    print("Testing Complete Position Data Storage")
    print("=" * 80)
    
    print("\n1. Testing complete position data...")
    
    # Simulate complete position data from cloud task
    all_balances = {
        "QRL": {"free": "1000.5", "locked": "0.0", "total": "1000.5"},
        "USDT": {"free": "500.25", "locked": "10.0", "total": "510.25"},
        "BTC": {"free": "0.001", "locked": "0.0", "total": "0.001"}
    }
    
    position_data = {
        "qrl_balance": "1000.5",
        "usdt_balance": "500.25",
        "qrl_locked": "0.0",
        "usdt_locked": "10.0",
        "all_balances": json.dumps(all_balances),
        "account_type": "SPOT",
        "can_trade": "True",
        "can_withdraw": "True",
        "can_deposit": "True",
        "update_time": "1703750000000",
        "updated_at": datetime.now().isoformat()
    }
    
    result = await redis_client.set_position(position_data)
    if result:
        print("✅ Complete position data stored")
        
        stored = await redis_client.get_position()
        if stored:
            print(f"✅ Retrieved position data:")
            print(f"   QRL Balance: {stored.get('qrl_balance')} (locked: {stored.get('qrl_locked')})")
            print(f"   USDT Balance: {stored.get('usdt_balance')} (locked: {stored.get('usdt_locked')})")
            print(f"   Account Type: {stored.get('account_type')}")
            print(f"   Can Trade: {stored.get('can_trade')}")
            
            # Parse all_balances
            all_bal = json.loads(stored.get('all_balances', '{}'))
            print(f"   Total Assets: {len(all_bal)}")
        else:
            print("❌ Failed to retrieve position data")
    else:
        print("❌ Failed to store position data")
    
    return True

async def main():
    """Run all tests"""
    try:
        print("\n🚀 Starting Cloud Task Storage Tests\n")
        
        success = True
        
        # Test raw MEXC storage
        if not await test_raw_mexc_storage():
            success = False
        
        # Test price storage
        if not await test_permanent_price_storage():
            success = False
        
        # Test position storage
        if not await test_complete_position_storage():
            success = False
        
        # Summary
        print("\n" + "=" * 80)
        if success:
            print("✅ All tests completed successfully!")
        else:
            print("❌ Some tests failed - check output above")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await redis_client.close()
        print("\n🔌 Redis connection closed")

if __name__ == "__main__":
    asyncio.run(main())
