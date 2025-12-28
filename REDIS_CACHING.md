# Redis Caching for MEXC v3 API Data

## Overview

This implementation adds comprehensive Redis caching for all MEXC v3 API data endpoints, improving performance and reducing API call frequency to MEXC servers.

## Features

### Market Data Caching

All market data from MEXC v3 API is now cached in Redis with appropriate TTL values:

1. **24hr Ticker Statistics** (`/market/ticker/{symbol}`)
   - Caches price changes, volume, and other 24hr stats
   - TTL: 60 seconds (configurable via `CACHE_TTL_TICKER`)
   - Redis Key: `market:{symbol}:ticker:24hr`

2. **Order Book Depth** (`/market/orderbook/{symbol}`)
   - Caches bids and asks with depth data
   - TTL: 10 seconds (configurable via `CACHE_TTL_ORDER_BOOK`)
   - Redis Key: `market:{symbol}:orderbook`

3. **Recent Trades** (`/market/trades/{symbol}`)
   - Caches list of recent trades
   - TTL: 60 seconds (configurable via `CACHE_TTL_TRADES`)
   - Redis Key: `market:{symbol}:trades:recent`

4. **Klines/Candlesticks** (`/market/klines/{symbol}`)
   - Caches candlestick data for specified intervals
   - TTL: 300 seconds (configurable via `CACHE_TTL_KLINES`)
   - Redis Key: `market:{symbol}:klines:{interval}`

5. **Current Price** (`/market/price/{symbol}`)
   - Already cached, now with configurable TTL
   - TTL: 30 seconds (configurable via `CACHE_TTL_PRICE`)
   - Redis Key: `bot:{symbol}:price:latest`

### Account Data Caching

Account-related data is also cached with longer TTL values:

1. **Account Balance** (`/account/balance`)
   - Caches asset balances (free and locked)
   - TTL: 120 seconds (configurable via `CACHE_TTL_ACCOUNT`)
   - Redis Key: `account:balance`

2. **Open Orders** (`/account/orders/open`)
   - Caches list of open orders
   - TTL: 30 seconds (configurable via `CACHE_TTL_ORDERS`)
   - Redis Key: `account:orders:open:{symbol}`

3. **Order History** (`/account/orders/history`)
   - Caches historical orders
   - TTL: 30 seconds (configurable via `CACHE_TTL_ORDERS`)
   - Redis Key: `account:orders:history:{symbol}:{start_time}-{end_time}`

## Configuration

### Environment Variables

Add these to your `.env` file to customize cache TTL values:

```bash
# Redis Cache TTL Configuration (in seconds)
CACHE_TTL_PRICE=30           # Price data TTL (default: 30s)
CACHE_TTL_TICKER=60          # 24hr ticker TTL (default: 60s)
CACHE_TTL_ORDER_BOOK=10      # Order book TTL (default: 10s)
CACHE_TTL_TRADES=60          # Recent trades TTL (default: 60s)
CACHE_TTL_KLINES=300         # Klines TTL (default: 300s)
CACHE_TTL_ACCOUNT=120        # Account data TTL (default: 120s)
CACHE_TTL_ORDERS=30          # Orders TTL (default: 30s)
```

### Redis Methods

All new Redis methods follow a consistent pattern:

**Setting Cache:**
```python
await redis_client.set_ticker_24hr(symbol, ticker_data)
await redis_client.set_order_book(symbol, orderbook_data)
await redis_client.set_recent_trades(symbol, trades_data)
await redis_client.set_klines(symbol, interval, klines_data)
await redis_client.set_account_balance(balance_data)
await redis_client.set_open_orders(symbol, orders_data)
await redis_client.set_order_history(symbol, orders_data, start_time, end_time)
```

**Getting Cache:**
```python
cached_ticker = await redis_client.get_ticker_24hr(symbol)
cached_orderbook = await redis_client.get_order_book(symbol)
cached_trades = await redis_client.get_recent_trades(symbol)
cached_klines = await redis_client.get_klines(symbol, interval)
cached_balance = await redis_client.get_account_balance()
cached_orders = await redis_client.get_open_orders(symbol)
cached_history = await redis_client.get_order_history(symbol, start_time, end_time)
```

## API Response Format

All cached endpoints now return a `cached` field indicating whether the data came from cache:

```json
{
  "symbol": "QRLUSDT",
  "data": { ... },
  "timestamp": "2024-01-01T12:00:00",
  "cached": true
}
```

- `cached: true` - Data retrieved from Redis cache
- `cached: false` - Data fetched fresh from MEXC API

## Benefits

1. **Reduced API Calls**: Significantly reduces calls to MEXC API, avoiding rate limits
2. **Improved Performance**: Faster response times by serving data from Redis
3. **Cost Efficiency**: Reduces bandwidth and API quota usage
4. **Reliability**: Cached data available even during temporary MEXC API issues
5. **Flexibility**: Configurable TTL values for different data types

## Cache Invalidation

Cache invalidation is handled automatically through TTL expiration:

- Market data has shorter TTL (10-60 seconds) for fresher data
- Account data has longer TTL (30-120 seconds) as it changes less frequently
- Klines have longest TTL (5 minutes) as they're more stable

## Testing

Run the Redis caching test suite:

```bash
python test_redis_caching.py
```

This will test:
- All caching methods (set/get)
- TTL configuration
- Data persistence and retrieval
- Redis connection handling

## New Endpoints

The following new endpoints were added:

1. `GET /market/orderbook/{symbol}` - Get order book depth with caching
2. `GET /market/trades/{symbol}` - Get recent trades with caching
3. `GET /market/klines/{symbol}` - Get klines/candlesticks with caching
4. `GET /account/orders/open` - Get open orders with caching
5. `GET /account/orders/history` - Get order history with caching

## Migration Notes

### Existing Code

No breaking changes. Existing endpoints maintain backward compatibility while adding caching support.

### Updated Endpoints

The following endpoints now support caching:

- `/market/ticker/{symbol}` - Added cache support
- `/market/price/{symbol}` - Updated to use configurable TTL
- `/account/balance` - Added cache support

## Performance Metrics

Expected improvements:

- **Response Time**: 50-90% faster for cached requests
- **API Calls**: 70-95% reduction in MEXC API calls
- **Rate Limit Usage**: Significantly lower, allowing higher throughput

## Troubleshooting

### Cache Not Working

1. Check Redis connection: `curl http://localhost:8080/health`
2. Verify Redis is running and accessible
3. Check Redis logs for connection errors
4. Verify environment variables are set correctly

### Stale Data

If you need fresher data, adjust TTL values in `.env`:

```bash
# For more frequent updates
CACHE_TTL_TICKER=30  # Reduced from 60s
CACHE_TTL_ACCOUNT=60  # Reduced from 120s
```

### Cache Miss

Cache misses are normal and expected:

- First request for a symbol/endpoint will always miss
- After TTL expiration, next request will miss
- Cache is transparent - fallback to API is automatic

## Future Enhancements

Potential improvements for future versions:

1. **Cache Warming**: Pre-populate cache on startup
2. **Manual Invalidation**: Add endpoint to clear specific cache keys
3. **Cache Statistics**: Track hit/miss ratios
4. **Smart TTL**: Adjust TTL based on data volatility
5. **Redis Cluster**: Support for Redis cluster deployments

## Related Files

- `redis_client.py` - Redis caching implementation
- `main.py` - API endpoints with caching integration
- `config.py` - Cache TTL configuration
- `test_redis_caching.py` - Test suite
