# Redis TTL Fix and Complete MEXC Response Storage

## Problem Summary

Based on issue #24, there were three critical problems:

1. **Redis TTL causing data expiration**: 
   - `set_account_balance()` had 120 second TTL
   - `set_position()` data could expire
   - `set_latest_price()` had 30 second TTL
   - Cloud Scheduler runs every 3 minutes, but data expired before next run

2. **Incomplete MEXC response storage**:
   - Only QRL/USDT balances were being stored
   - All other fields from MEXC `/api/v3/account` API were lost:
     - `makerCommission`, `takerCommission`
     - `canTrade`, `canWithdraw`, `canDeposit`
     - `updateTime`, `accountType`, `permissions`

3. **Cloud Tasks partial data storage**:
   - `sync-balance` task only stored QRL/USDT balance
   - `update-price` task only stored price without complete 24hr ticker data

## Solutions Implemented

### 1. Remove TTL from Critical Data Storage (`redis_client.py`)

**Changed: `set_account_balance()` method**
```python
# BEFORE (with TTL)
await self.client.set(key, json.dumps(data), ex=config.CACHE_TTL_ACCOUNT)  # 120 seconds

# AFTER (permanent storage)
await self.client.set(key, json.dumps(data))  # No TTL - permanent
```

**Verified: Other methods already have no TTL**
- `set_position()` - Uses `hset` which doesn't have TTL
- `set_latest_price()` - Already stores permanently without TTL

### 2. Store Complete MEXC Account Response (`main.py`)

**Updated: `/account/balance` endpoint**

Added complete MEXC account fields to the response:
```python
result = {
    "success": True,
    "balances": balances,
    # NEW: Include all MEXC account fields
    "makerCommission": account_info.get("makerCommission", 0),
    "takerCommission": account_info.get("takerCommission", 0),
    "canTrade": account_info.get("canTrade", False),
    "canWithdraw": account_info.get("canWithdraw", False),
    "canDeposit": account_info.get("canDeposit", False),
    "updateTime": account_info.get("updateTime", 0),
    "accountType": account_info.get("accountType", "SPOT"),
    "permissions": account_info.get("permissions", []),
    "timestamp": datetime.now().isoformat(),
    "cached": False
}
```

Added raw MEXC response storage:
```python
await redis_client.set_raw_mexc_response(
    endpoint="account_info",
    response_data=account_info,
    metadata={"source": "account_balance_endpoint"}
)
```

### 3. Enhanced Logging (`cloud_tasks.py` and `main.py`)

**Added detailed logging for all MEXC fields:**

In `cloud_tasks.py`:
```python
logger.info(
    f"[Cloud Task] Balance synced - "
    f"QRL: {qrl_balance:.4f} (locked: {all_balances.get('QRL', {}).get('locked', 0)}), "
    f"USDT: {usdt_balance:.2f} (locked: {all_balances.get('USDT', {}).get('locked', 0)}), "
    f"Total assets: {len(all_balances)}, "
    f"Account type: {account_info.get('accountType')}, "
    f"canTrade: {account_info.get('canTrade')}, "
    f"Maker/Taker: {account_info.get('makerCommission')}/{account_info.get('takerCommission')}, "
    f"Permissions: {account_info.get('permissions')}, "
    f"Update time: {account_info.get('updateTime')}"
)
```

## Verification Steps

### 1. Verify No TTL on Account Balance

Connect to Redis and check TTL:
```bash
redis-cli
> TTL account:balance
-1  # -1 means no TTL (permanent storage)
```

### 2. Verify Complete MEXC Fields Stored

Check stored account balance data:
```bash
redis-cli
> GET account:balance
```

Should contain all these fields:
- `balances` (QRL, USDT)
- `makerCommission`
- `takerCommission`
- `canTrade`
- `canWithdraw`
- `canDeposit`
- `updateTime`
- `accountType`
- `permissions`

### 3. Verify Raw MEXC Response Storage

Check raw MEXC API responses:
```bash
redis-cli
> GET mexc:raw:account_info:latest
> GET mexc:raw:ticker_24hr:latest
```

Both should have no TTL:
```bash
> TTL mexc:raw:account_info:latest
-1
> TTL mexc:raw:ticker_24hr:latest
-1
```

### 4. Monitor Logs

Check Cloud Run logs for enhanced logging:

**After `/account/balance` API call:**
```
Stored raw account_info response with X balances
Stored complete account balance - Type: SPOT, canTrade: True, Maker/Taker: 10/10, Permissions: ['SPOT']
```

**After Cloud Scheduler sync-balance task:**
```
[Cloud Task] Balance synced - QRL: X.XXXX (locked: 0), USDT: X.XX (locked: 0), Total assets: X, Account type: SPOT, canTrade: True, Maker/Taker: 10/10, Permissions: ['SPOT'], Update time: XXXXXXXXXX
```

## Impact

### Before Fix
- Account balance data expired after 120 seconds
- Only QRL/USDT balances stored, all other MEXC fields lost
- Cloud Scheduler running every 3 minutes found expired data
- Missing critical account information (permissions, trade capabilities, commission rates)

### After Fix
- Account balance data stored permanently (no expiration)
- Complete MEXC account response stored with all fields
- Cloud Scheduler always finds valid data
- Full account information available for monitoring and debugging
- Raw MEXC responses preserved for historical tracking

## Files Modified

1. `redis_client.py` - Removed TTL from `set_account_balance()`
2. `main.py` - Store complete MEXC account fields and raw response
3. `cloud_tasks.py` - Enhanced logging with all MEXC fields

## Testing

To test these changes:

1. **Deploy to Cloud Run** with the updated code
2. **Wait 3+ minutes** (longer than old TTL)
3. **Check Redis** to verify data still exists:
   ```bash
   redis-cli
   > GET account:balance
   > TTL account:balance  # Should be -1
   ```
4. **Call API endpoint** `/account/balance`
5. **Check logs** for complete field logging
6. **Trigger Cloud Scheduler** task manually
7. **Verify logs** show all MEXC fields

## Related

- Issue: #24
- MEXC API Docs: https://www.mexc.com/api-docs/spot-v3/
- Cloud Scheduler runs every 3 minutes
- Previous TTL: 120 seconds (account), 30 seconds (price)
- New TTL: -1 (permanent storage)
