# MEXC API Data Storage in Redis

## Overview

All data received from MEXC API is now **permanently stored in Redis** for debugging and analysis purposes. This ensures complete visibility into API responses and helps diagnose issues without guessing.

## Implementation Details

### Data Storage Strategy

All MEXC API data is stored **permanently** (no expiration/TTL) in Redis with the following keys:

| Redis Key | Description | Data Type |
|-----------|-------------|-----------|
| `mexc:raw_response:account_info` | Complete MEXC account info API response | JSON |
| `mexc:account_balance` | Processed balance data for QRL and USDT | JSON |
| `mexc:qrl_price` | Current QRL price in USDT | JSON |
| `mexc:total_value` | Total account value calculation | JSON |

### Data Structure

#### 1. Raw Response (`mexc:raw_response:account_info`)

Stores the complete MEXC API response without modification:

```json
{
  "endpoint": "account_info",
  "data": {
    "balances": [
      {"asset": "QRL", "free": "1000.0", "locked": "0.0"},
      {"asset": "USDT", "free": "500.0", "locked": "0.0"},
      ...
    ],
    "updateTime": 1640000000000
  },
  "timestamp": "2024-12-27T23:00:00.000000",
  "stored_at": 1640000000000
}
```

#### 2. Account Balance (`mexc:account_balance`)

Processed balance data for QRL and USDT:

```json
{
  "balances": {
    "QRL": {
      "free": "1000.0",
      "locked": "0.0",
      "total": "1000.0"
    },
    "USDT": {
      "free": "500.0",
      "locked": "0.0",
      "total": "500.0"
    },
    "all_assets_count": 25
  },
  "timestamp": "2024-12-27T23:00:00.000000",
  "stored_at": 1640000000000
}
```

#### 3. QRL Price (`mexc:qrl_price`)

Current QRL price data:

```json
{
  "price": "0.0025",
  "price_float": 0.0025,
  "raw_data": {
    "symbol": "QRLUSDT",
    "price": "0.0025"
  },
  "timestamp": "2024-12-27T23:00:00.000000",
  "stored_at": 1640000000000
}
```

#### 4. Total Value (`mexc:total_value`)

Total account value calculation in USDT:

```json
{
  "total_value_usdt": "502.5",
  "total_value_float": 502.5,
  "breakdown": {
    "qrl_quantity": 1000.0,
    "qrl_price_usdt": 0.0025,
    "qrl_value_usdt": 2.5,
    "usdt_balance": 500.0,
    "total_value_usdt": 502.5
  },
  "timestamp": "2024-12-27T23:00:00.000000",
  "stored_at": 1640000000000
}
```

## API Endpoints

### 1. Fetch and Store Balance Data

```bash
GET /account/balance
```

**What it does:**
1. Fetches account info from MEXC API
2. Stores raw response in Redis (`mexc:raw_response:account_info`)
3. Fetches QRL price from MEXC API
4. Stores QRL price in Redis (`mexc:qrl_price`)
5. Calculates total account value
6. Stores total value in Redis (`mexc:total_value`)
7. Stores processed balance data in Redis (`mexc:account_balance`)

**Response:**
```json
{
  "success": true,
  "balances": {
    "QRL": {"free": "1000.0", "locked": "0.0", "total": "1000.0"},
    "USDT": {"free": "500.0", "locked": "0.0", "total": "500.0"}
  },
  "qrl_price": 0.0025,
  "total_value": {
    "usdt": 502.5,
    "breakdown": {
      "qrl_quantity": 1000.0,
      "qrl_price_usdt": 0.0025,
      "qrl_value_usdt": 2.5,
      "usdt_balance": 500.0,
      "total_value_usdt": 502.5
    }
  },
  "timestamp": "2024-12-27T23:00:00.000000",
  "redis_storage": {
    "raw_response": "mexc:raw_response:account_info",
    "account_balance": "mexc:account_balance",
    "qrl_price": "mexc:qrl_price",
    "total_value": "mexc:total_value"
  }
}
```

### 2. View Stored Redis Data

```bash
GET /account/balance/redis
```

**What it does:**
- Retrieves all stored MEXC data from Redis
- Shows which data is available
- Useful for debugging and verification

**Response:**
```json
{
  "success": true,
  "data_available": {
    "raw_response": true,
    "account_balance": true,
    "qrl_price": true,
    "total_value": true
  },
  "raw_response": {...},
  "account_balance": {...},
  "qrl_price": {...},
  "total_value": {...},
  "retrieved_at": "2024-12-27T23:00:00.000000"
}
```

## Logging

The implementation includes comprehensive logging at each step:

```
================================================================================
FETCHING ACCOUNT BALANCE FROM MEXC API
================================================================================
Step 1: Fetching account info from MEXC API...
Received account info with 25 assets
Step 2: Storing raw MEXC API response in Redis...
✓ Raw response stored in Redis: mexc:raw_response:account_info
Step 3: Processing balance data...
  QRL: free=1000.0, locked=0.0, total=1000.0
  USDT: free=500.0, locked=0.0, total=500.0
Account has 25 total assets
Step 4: Fetching QRL price from MEXC API...
✓ QRL Price: 0.0025 USDT
✓ QRL price stored in Redis: mexc:qrl_price
Step 5: Calculating total account value in USDT...
  QRL Quantity: 1000.0
  QRL Price: 0.0025 USDT
  QRL Value: 2.5 USDT
  USDT Balance: 500.0 USDT
  TOTAL VALUE: 502.5 USDT
✓ Total value stored in Redis: mexc:total_value
Step 6: Storing processed balance data in Redis...
✓ Balance data stored in Redis: mexc:account_balance
================================================================================
ALL MEXC DATA SUCCESSFULLY STORED IN REDIS (PERMANENT)
Redis Keys Created:
  - mexc:raw_response:account_info
  - mexc:account_balance
  - mexc:qrl_price
  - mexc:total_value
================================================================================
```

## Debugging

### Check Redis Directly

Using Redis CLI:

```bash
# Check if keys exist
redis-cli KEYS "mexc:*"

# View raw response
redis-cli GET "mexc:raw_response:account_info"

# View account balance
redis-cli GET "mexc:account_balance"

# View QRL price
redis-cli GET "mexc:qrl_price"

# View total value
redis-cli GET "mexc:total_value"
```

### Test Script

Run the test script to verify Redis storage:

```bash
python test_mexc_redis_storage.py
```

This will:
1. Connect to Redis
2. Store test data in all 4 Redis keys
3. Retrieve and verify the data
4. Display results

## Data Persistence

**IMPORTANT:** All MEXC data is stored **permanently** without expiration.

- Data will persist until explicitly deleted
- Data survives Redis restarts (if persistence is configured)
- No automatic cleanup or TTL

### Manual Data Cleanup (if needed)

To clear stored data:

```bash
# Delete all MEXC data
redis-cli DEL "mexc:raw_response:account_info"
redis-cli DEL "mexc:account_balance"
redis-cli DEL "mexc:qrl_price"
redis-cli DEL "mexc:total_value"

# Or delete all keys matching pattern
redis-cli KEYS "mexc:*" | xargs redis-cli DEL
```

## Benefits

1. **Complete Visibility**: See exactly what MEXC API returns
2. **Easy Debugging**: Inspect Redis data to diagnose issues
3. **No Guessing**: All data is preserved for analysis
4. **Historical Record**: Permanent storage allows tracking changes over time
5. **Fast Access**: Redis provides instant access to latest data

## Implementation References

- Redis storage methods: `redis_client.py`
- API endpoint implementation: `main.py` (`/account/balance`)
- Test script: `test_mexc_redis_storage.py`
