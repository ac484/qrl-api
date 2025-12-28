# Cloud Scheduler and Dashboard Logic Fixes

## Overview

This document summarizes the fixes applied to resolve critical logic issues in the QRL Trading API related to Google Cloud Scheduler authentication and dashboard data display.

## Issues Fixed

### 1. Cloud Scheduler Authentication Header Issue ✅

**Problem:**
- Cloud Scheduler endpoints only checked for `X-CloudScheduler` header
- Google Cloud Scheduler with OIDC authentication sends `Authorization: Bearer <token>` header instead
- All OIDC-authenticated requests were being rejected with 401 Unauthorized

**Root Cause:**
- According to [Google Cloud Scheduler documentation](https://cloud.google.com/scheduler/docs/http-target-auth):
  - OIDC authentication uses `Authorization` header with Bearer token
  - `X-CloudScheduler` header is NOT guaranteed to be present
  - The header check was too restrictive

**Solution:**
- Updated all three Cloud Scheduler endpoints (`/tasks/sync-balance`, `/tasks/update-price`, `/tasks/update-cost`)
- Now accepts BOTH authentication methods:
  - `X-CloudScheduler` header (legacy/backward compatibility)
  - `Authorization` header (OIDC/recommended)
- Added logging to track which authentication method is used
- Maintains full backward compatibility

**Files Changed:**
- `cloud_tasks.py` - All three task endpoints updated

**Code Changes:**
```python
# Before:
if not x_cloudscheduler:
    raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")

# After:
if not x_cloudscheduler and not authorization:
    raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")

auth_method = "OIDC" if authorization else "X-CloudScheduler"
logger.info(f"[Cloud Task] sync-balance authenticated via {auth_method}")
```

---

### 2. Dashboard Data Source Logic Issue ✅

**Problem:**
- Dashboard used Redis position data as fallback when API balance failed
- Redis position data is updated by Cloud Scheduler every 3 minutes
- Fallback to 3-minute-old data defeats the purpose of real-time API
- Created data inconsistency when mixing real-time and cached data

**Root Cause:**
```javascript
// WRONG: Fallback to stale Redis data
if (balances && price) {
    calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
}
else if (position && price && (position.qrl_balance || position.usdt_balance)) {
    // Using 3-minute-old Redis data as fallback
    const qrlBal = parseFloat(position.qrl_balance || 0);
    const usdtBal = parseFloat(position.usdt_balance || 0);
    calculateTotalValue(qrlBal, usdtBal, price);
}
```

**Solution:**
- Removed fallback to Redis position data for balance display
- Redis position data is now ONLY used for bot-specific analytics:
  - `avg_cost` - Average cost basis
  - `unrealized_pnl` - Unrealized profit/loss
  - `position_layers` - Core/swing/active position breakdown
- Display `'N/A (API Error)'` when real-time API fails instead of using stale data
- Prevents data inconsistency from mixing data sources

**Files Changed:**
- `templates/dashboard.html` - `refreshData()` function

**Code Changes:**
```javascript
// After:
if (balances && price) {
    calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
} else {
    // Show error instead of using stale Redis data
    console.error('Failed to load real-time balance from API');
    document.getElementById('total-value').textContent = 'N/A (API Error)';
}
```

---

### 3. Data Inconsistency Time Window ✅

**Problem:**
- Total value calculation could mix data from different time points:
  - API balance: Real-time (current)
  - Redis position: Every 3 minutes (potentially stale)
  - Price: Every 30 seconds
- This created inconsistent calculations

**Solution:**
- By removing the Redis fallback, we ensure consistency:
  - Total value = real-time API balance × current price
  - OR display error if API fails
  - Never mix real-time and cached data sources

---

### 4. Redis TTL Verification ✅

**Investigation:**
- Checked `redis_client.py` `set_position()` implementation
- Confirmed position data is stored permanently without TTL
- Uses `hset()` without expiration parameter
- No risk of data loss between Cloud Scheduler runs

**Code Verified:**
```python
async def set_position(self, position_data: Dict[str, Any]) -> bool:
    try:
        key = f"bot:{config.TRADING_SYMBOL}:position"
        position_data["updated_at"] = datetime.now().isoformat()
        await self.client.hset(key, mapping=position_data)  # No TTL
        return True
```

## Data Flow Architecture

### Before (Problematic):
```
Cloud Scheduler (every 3 min) → Redis position data
                                       ↓
                                  Dashboard ← (fallback when API fails)
                                       ↑
Real-time API balance ──────────────────┘
```

### After (Fixed):
```
Cloud Scheduler (every 3 min) → Redis position data → Bot Analytics Only
                                                       (avg_cost, PnL, layers)

Real-time API balance ────────→ Dashboard Balance Display
                                (no fallback, show error if fails)
```

## Testing

### Authentication Tests
- ✅ X-CloudScheduler header authentication
- ✅ OIDC Authorization header authentication
- ✅ Both headers present (OIDC takes precedence)
- ✅ Neither header (correctly rejected)

### Dashboard Logic Tests
- ✅ API balance and price available (normal case)
- ✅ API balance fails (show error, no Redis fallback)
- ✅ Price fails (show error)
- ✅ Both fail (show error)
- ✅ Redis data only used for analytics, not balance

## Benefits

1. **Reliability**: Cloud Scheduler works with both OIDC and legacy authentication
2. **Data Accuracy**: Dashboard always shows real-time data or error, never stale data
3. **Transparency**: Clear error messages when APIs fail
4. **Consistency**: No more mixing of real-time and cached data
5. **Maintainability**: Clear separation of data sources and their purposes
6. **Backward Compatibility**: Existing deployments continue to work

## Deployment Notes

- No configuration changes required
- Works with both existing (X-CloudScheduler) and new (OIDC) deployments
- No database migrations needed
- No breaking changes to APIs

## Monitoring Recommendations

After deployment, monitor logs for:
1. Authentication method used (`OIDC` vs `X-CloudScheduler`)
2. API failures that trigger `'N/A (API Error)'` display
3. Cloud Scheduler task success/failure rates

## References

- [Google Cloud Scheduler HTTP Target Authentication](https://cloud.google.com/scheduler/docs/http-target-auth)
- [OIDC Token Authentication](https://cloud.google.com/scheduler/docs/http-target-auth#using-oidc-auth)
- Issue #24: Original issue identifying these problems
