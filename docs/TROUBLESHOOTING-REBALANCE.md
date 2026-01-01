# Rebalance Execution Troubleshooting Guide

## Problem: Rebalance Action Always HOLD

### Symptoms

- Cloud Scheduler successfully triggers `/tasks/15-min-job`
- Logs show: `Rebalance action: HOLD, quantity: 0.0000, reason: Insufficient price or balance`
- No actual rebalancing occurs despite having QRL and USDT balances

### Root Cause Analysis

The rebalance service may return `HOLD` for several reasons:

1. **Missing or invalid price data**
2. **Zero or missing balances**
3. **MEXC API connection issues**
4. **Redis cache serving stale/incomplete data**

### Diagnostic Steps

#### Step 1: Check Logs for Balance Snapshot

After the fix, logs will show detailed balance snapshot:

```
[15-min-job] Balance snapshot - QRL: 100.0, USDT: 100.0, Price: 1.5, Source: api
```

**What to look for:**
- `QRL`: Should show actual QRL balance (not 0)
- `USDT`: Should show actual USDT balance (not 0)
- `Price`: Should show current QRL/USDT price (not 0 or 'N/A')
- `Source`: Should be `api` (live data) or `cache` (cached data)

**Common Issues:**

| Symptom | Cause | Solution |
|---------|-------|----------|
| `QRL: 0, USDT: 0` | No balances or API connection failed | Check MEXC API credentials |
| `Price: 0` or `Price: N/A` | Failed to fetch ticker price | Check MEXC market endpoint |
| `Source: cache` | Using cached data (API failed) | Check MEXC API connection |
| All values present but HOLD | Within threshold (< 1% deviation) | This is normal, no rebalance needed |

#### Step 2: Check MEXC API Credentials

```bash
# Verify credentials are set
gcloud run services describe qrl-api \
  --region=asia-southeast1 \
  --format="value(spec.template.spec.containers[0].env)" | grep MEXC

# Should show:
# MEXC_API_KEY=XXX
# MEXC_API_SECRET=XXX
```

**If missing:**
```bash
gcloud run services update qrl-api \
  --region=asia-southeast1 \
  --set-env-vars="MEXC_API_KEY=your_key,MEXC_API_SECRET=your_secret"
```

#### Step 3: Test MEXC API Connection

```bash
# Test account endpoint
curl https://qrl-trading-api-XXX.run.app/account/balance

# Expected: 200 OK with QRL and USDT balances
# Error: 503 or 400 indicates API connection issue
```

#### Step 4: Check Rebalance Logic

The rebalance service uses this logic:

```python
# Calculate values
total_value = qrl_balance × price + usdt_balance
target_value = total_value × 0.5  # 50% target
qrl_value = qrl_balance × price
delta = qrl_value - target_value

# Decision logic
if price <= 0 or total_value <= 0:
    → HOLD (Insufficient price or balance)
    
elif abs(delta) < 5 USDT:
    → HOLD (Below minimum notional)
    
elif abs(delta)/total_value < 1%:
    → HOLD (Within threshold)
    
elif delta > 0:
    → SELL (QRL value above 50% target)
    
else:
    → BUY (QRL value below 50% target)
```

**Example Scenarios:**

**Scenario 1: Normal HOLD (Within Threshold)**
```
QRL: 100 @ 1.0 = 100 USDT
USDT: 102
Total: 202 USDT
Target: 101 USDT (50%)
Delta: -1 USDT
Deviation: 0.5% < 1%
→ HOLD (Within threshold) ✅ This is correct behavior
```

**Scenario 2: Should Rebalance**
```
QRL: 100 @ 2.0 = 200 USDT
USDT: 50
Total: 250 USDT
Target: 125 USDT (50%)
Delta: 75 USDT
Deviation: 30% > 1%
→ SELL 37.5 QRL ✅ Should execute
```

**Scenario 3: Missing Data**
```
QRL: 0 @ 0 = 0 USDT
USDT: 0
Total: 0 USDT
→ HOLD (Insufficient price or balance) ❌ API connection issue
```

#### Step 5: Check Redis Connection

```bash
# View Redis-related logs
gcloud logging read \
  "resource.type=cloud_run_revision AND textPayload:\"redis\"" \
  --limit 20

# Should see successful Redis connections
# If errors, check Redis Cloud connection string and password
```

### Enhanced Logging (After Fix)

The updated code now logs detailed balance information before computing the rebalance plan:

```python
logger.info(
    f"[15-min-job] Balance snapshot - "
    f"QRL: {snapshot.get('balances', {}).get('QRL', {}).get('total', 0)}, "
    f"USDT: {snapshot.get('balances', {}).get('USDT', {}).get('total', 0)}, "
    f"Price: {snapshot.get('prices', {}).get('QRLUSDT', 'N/A')}, "
    f"Source: {snapshot.get('source', 'unknown')}"
)
```

This helps diagnose why rebalance returns HOLD by showing the exact input data.

### Common Fixes

#### Fix 1: MEXC API Credentials Not Set

**Symptom:** Logs show cache source, balances are 0 or stale

**Solution:**
```bash
gcloud run services update qrl-api \
  --region=asia-southeast1 \
  --set-env-vars="MEXC_API_KEY=your_key,MEXC_API_SECRET=your_secret"
```

#### Fix 2: Redis Connection Issues

**Symptom:** Logs show Redis connection errors

**Solution:**
```bash
# Check Redis environment variables
gcloud run services describe qrl-api \
  --region=asia-southeast1 \
  --format="value(spec.template.spec.containers[0].env)" | grep REDIS

# Update if needed
gcloud run services update qrl-api \
  --region=asia-southeast1 \
  --set-env-vars="REDIS_URL=redis://...,REDIS_PASSWORD=..."
```

#### Fix 3: Within Threshold (Normal Behavior)

**Symptom:** Logs show valid balances and price, but action is HOLD with "Within threshold"

**This is correct behavior** - Rebalance only executes when:
- Deviation > 1% of total value, AND
- Notional value > 5 USDT

**Example of normal HOLD:**
```
Total value: 200 USDT
QRL value: 102 USDT (51%)
Deviation: 2 USDT (1%)
→ HOLD (Within threshold) ✅ This prevents excessive trading
```

To force rebalance even for small deviations (not recommended), adjust thresholds in rebalance service initialization (requires code change).

### Testing Rebalance Execution

#### Manual Test

```bash
# Trigger manually
curl -X POST https://qrl-trading-api-XXX.run.app/tasks/15-min-job \
  -H "X-CloudScheduler: true"

# Check logs for balance snapshot
gcloud logging read \
  "resource.type=cloud_run_revision AND textPayload:\"Balance snapshot\"" \
  --limit 5
```

#### Check Stored Rebalance Plan

```bash
# If Redis is accessible, check stored plan
# (Requires Redis CLI access or admin endpoint)

# Alternative: Check via logs
gcloud logging read \
  "resource.type=cloud_run_revision AND textPayload:\"Rebalance action\"" \
  --limit 5 \
  --format json
```

### Expected Behavior After Fix

1. **Orders endpoint** works correctly (400 error fixed)
2. **Balance snapshot** shows actual QRL/USDT balances and price
3. **Rebalance action** determined based on actual data:
   - `HOLD` if within 1% threshold (normal)
   - `BUY` if QRL value < 50% target
   - `SELL` if QRL value > 50% target

### Related Files

- **Rebalance Service:** `src/app/application/trading/services/trading/rebalance_service.py`
- **Balance Service:** `src/app/application/account/balance_service.py`
- **15-min Job:** `src/app/interfaces/tasks/15-min-job.py`
- **MEXC Client:** `src/app/infrastructure/external/mexc/client.py`

---

**Status:** ✅ Enhanced with diagnostic logging  
**Date:** 2026-01-01  
**Related Docs:** `docs/TASKS-ENDPOINTS-REFERENCE.md`, `docs/TROUBLESHOOTING-MEXC-API-ORDERS.md`
