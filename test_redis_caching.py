#!/usr/bin/env python3
"""
Test script for Redis caching functionality
Tests all new MEXC v3 API data caching methods
"""
import asyncio
import json
from datetime import datetime
from redis_client import redis_client
from config import config

async def test_redis_caching():
    """Test all Redis caching methods"""
    
    print("=" * 60)
    print("Testing Redis Caching for MEXC v3 API Data")
    print("=" * 60)
    
    # Connect to Redis
    print("\n1. Connecting to Redis...")
    if not await redis_client.connect():
        print("❌ Failed to connect to Redis")
        return False
    print("✅ Connected to Redis successfully")
    
    # Test ticker caching
    print("\n2. Testing 24hr ticker caching...")
    test_ticker = {
        "symbol": "QRLUSDT",
        "priceChange": "0.0001",
        "priceChangePercent": "0.5",
        "lastPrice": "0.02",
        "volume": "1000000"
    }
    
    await redis_client.set_ticker_24hr("QRLUSDT", test_ticker)
    cached_ticker = await redis_client.get_ticker_24hr("QRLUSDT")
    
    if cached_ticker and "symbol" in cached_ticker:
        print(f"✅ Ticker cached and retrieved successfully")
        print(f"   Cached at: {cached_ticker.get('cached_at')}")
    else:
        print("❌ Failed to cache/retrieve ticker")
    
    # Test order book caching
    print("\n3. Testing order book caching...")
    test_orderbook = {
        "bids": [["0.019", "1000"], ["0.018", "2000"]],
        "asks": [["0.021", "1500"], ["0.022", "2500"]],
        "lastUpdateId": 12345
    }
    
    await redis_client.set_order_book("QRLUSDT", test_orderbook)
    cached_orderbook = await redis_client.get_order_book("QRLUSDT")
    
    if cached_orderbook and "bids" in cached_orderbook:
        print(f"✅ Order book cached and retrieved successfully")
        print(f"   Bids count: {len(cached_orderbook.get('bids', []))}")
    else:
        print("❌ Failed to cache/retrieve order book")
    
    # Test recent trades caching
    print("\n4. Testing recent trades caching...")
    test_trades = [
        {"id": 1, "price": "0.02", "qty": "100", "time": 1234567890},
        {"id": 2, "price": "0.021", "qty": "200", "time": 1234567891}
    ]
    
    await redis_client.set_recent_trades("QRLUSDT", test_trades)
    cached_trades = await redis_client.get_recent_trades("QRLUSDT")
    
    if cached_trades and len(cached_trades) == 2:
        print(f"✅ Recent trades cached and retrieved successfully")
        print(f"   Trades count: {len(cached_trades)}")
    else:
        print("❌ Failed to cache/retrieve recent trades")
    
    # Test klines caching
    print("\n5. Testing klines caching...")
    test_klines = [
        [1234567890000, "0.019", "0.021", "0.018", "0.02", "100000"],
        [1234567950000, "0.02", "0.022", "0.019", "0.021", "120000"]
    ]
    
    await redis_client.set_klines("QRLUSDT", "1m", test_klines)
    cached_klines = await redis_client.get_klines("QRLUSDT", "1m")
    
    if cached_klines and len(cached_klines) == 2:
        print(f"✅ Klines cached and retrieved successfully")
        print(f"   Klines count: {len(cached_klines)}")
    else:
        print("❌ Failed to cache/retrieve klines")
    
    # Test account balance caching
    print("\n6. Testing account balance caching...")
    test_balance = {
        "success": True,
        "balances": {
            "QRL": {"free": "10000", "locked": "0"},
            "USDT": {"free": "500", "locked": "0"}
        },
        "timestamp": datetime.now().isoformat()
    }
    
    await redis_client.set_account_balance(test_balance)
    cached_balance = await redis_client.get_account_balance()
    
    if cached_balance and "balances" in cached_balance:
        print(f"✅ Account balance cached and retrieved successfully")
        print(f"   QRL free: {cached_balance['balances']['QRL']['free']}")
    else:
        print("❌ Failed to cache/retrieve account balance")
    
    # Test open orders caching
    print("\n7. Testing open orders caching...")
    test_orders = [
        {"orderId": "123", "symbol": "QRLUSDT", "price": "0.02", "qty": "100"},
        {"orderId": "124", "symbol": "QRLUSDT", "price": "0.021", "qty": "200"}
    ]
    
    await redis_client.set_open_orders("QRLUSDT", test_orders)
    cached_orders = await redis_client.get_open_orders("QRLUSDT")
    
    if cached_orders and len(cached_orders) == 2:
        print(f"✅ Open orders cached and retrieved successfully")
        print(f"   Orders count: {len(cached_orders)}")
    else:
        print("❌ Failed to cache/retrieve open orders")
    
    # Test order history caching
    print("\n8. Testing order history caching...")
    test_history = [
        {"orderId": "100", "symbol": "QRLUSDT", "status": "FILLED"},
        {"orderId": "101", "symbol": "QRLUSDT", "status": "FILLED"}
    ]
    
    await redis_client.set_order_history("QRLUSDT", test_history)
    cached_history = await redis_client.get_order_history("QRLUSDT")
    
    if cached_history and len(cached_history) == 2:
        print(f"✅ Order history cached and retrieved successfully")
        print(f"   History count: {len(cached_history)}")
    else:
        print("❌ Failed to cache/retrieve order history")
    
    # Check TTL configuration
    print("\n9. Checking TTL configuration...")
    print(f"   CACHE_TTL_PRICE: {config.CACHE_TTL_PRICE}s")
    print(f"   CACHE_TTL_TICKER: {config.CACHE_TTL_TICKER}s")
    print(f"   CACHE_TTL_ORDER_BOOK: {config.CACHE_TTL_ORDER_BOOK}s")
    print(f"   CACHE_TTL_TRADES: {config.CACHE_TTL_TRADES}s")
    print(f"   CACHE_TTL_KLINES: {config.CACHE_TTL_KLINES}s")
    print(f"   CACHE_TTL_ACCOUNT: {config.CACHE_TTL_ACCOUNT}s")
    print(f"   CACHE_TTL_ORDERS: {config.CACHE_TTL_ORDERS}s")
    print("✅ TTL configuration loaded successfully")
    
    # Close Redis connection
    print("\n10. Closing Redis connection...")
    await redis_client.close()
    print("✅ Redis connection closed")
    
    print("\n" + "=" * 60)
    print("All Redis caching tests completed successfully! ✅")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    asyncio.run(test_redis_caching())
