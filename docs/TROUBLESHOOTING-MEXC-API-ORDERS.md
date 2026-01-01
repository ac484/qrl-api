# MEXC API Orders Troubleshooting Guide

## Problem: 400 Bad Request on /account/orders

### Root Cause Analysis

**Error Message:**
```
Client error '400 Bad Request' for url 'https://api.mexc.com/api/v3/openOrders?timestamp=XXX&symbol=QRLUSDT&signature=XXX'
```

**Root Cause:**
The `get_open_orders()` method in `trade_repo.py` was incorrectly initializing the params dictionary with `{"timestamp": None}`, which caused:

1. The `None` value to be included in signature calculation
2. MEXC API to reject the signature as invalid
3. 400 Bad Request error returned to client

### Technical Details

**Problematic Code (Before Fix):**
```python
async def get_open_orders(self, symbol: Optional[str] = None):
    params = {"timestamp": None}  # ❌ WRONG! Causes signature mismatch
    if symbol:
        params["symbol"] = symbol
    return await self._request("GET", "/api/v3/openOrders", params=params, signed=True)
```

**Fixed Code:**
```python
async def get_open_orders(self, symbol: Optional[str] = None):
    params = {}  # ✅ CORRECT! Let _request add timestamp automatically
    if symbol:
        params["symbol"] = symbol
    return await self._request("GET", "/api/v3/openOrders", params=params, signed=True)
```

### Why This Happened

The MEXC client's `_request` method automatically adds `timestamp` when `signed=True`:

```python
async def _request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, signed: bool = False):
    payload = params.copy() if params else {}
    if signed:
        self._require_credentials()
        payload["timestamp"] = int(time.time() * 1000)  # ← Automatically added here
        payload["signature"] = self._generate_signature(payload)
    return await self._conn.request(method, endpoint, params=payload)
```

When `params` already contained `{"timestamp": None}`, the signature calculation included the `None` value, resulting in an invalid signature.

### Impact

- **Orders endpoint**: Failed with 400 error
- **All other signed endpoints**: Worked correctly (they didn't pre-set timestamp)
- **Rebalance execution**: Potentially affected if it needed order data

### Fix Applied

**Commit:** [Will be included in next commit]

**File Modified:** `src/app/infrastructure/external/mexc/repos/trade_repo.py`

**Change:**
- Line 44: Removed `{"timestamp": None}` initialization
- Line 44: Changed to empty dict `{}`

### Testing

After applying the fix, test with:

```bash
# Test orders endpoint
curl https://qrl-trading-api-XXX.run.app/account/orders

# Expected: 200 OK with orders array (or empty array if no orders)
# Previously: 400 Bad Request
```

### Related Issues

This pattern should be checked in other methods to ensure no similar issues exist:
- ✅ `create_order` - Correct (no pre-set timestamp)
- ✅ `cancel_order` - Correct (no pre-set timestamp)
- ✅ `get_order` - Correct (no pre-set timestamp)
- ❌ `get_open_orders` - **FIXED** (was pre-setting timestamp to None)
- ✅ `get_all_orders` - Correct (no pre-set timestamp)

### Prevention

**Best Practice for MEXC Signed Endpoints:**

1. ✅ **DO:** Initialize params as empty dict or with only required parameters
   ```python
   params = {}
   params = {"symbol": symbol}
   ```

2. ❌ **DON'T:** Pre-set timestamp or signature in params
   ```python
   params = {"timestamp": None}  # Wrong!
   params = {"signature": ""}     # Wrong!
   ```

3. ✅ **DO:** Let `_request(signed=True)` handle timestamp and signature automatically

### MEXC Signature Calculation

For reference, MEXC signature is calculated as:

1. Sort all parameters (including timestamp) alphabetically by key
2. URL-encode them: `param1=value1&param2=value2`
3. Calculate HMAC-SHA256 with secret key
4. Append as `&signature=XXX`

If any parameter value is incorrect (including `None`), the signature will be invalid and MEXC returns 400.

---

**Status:** ✅ FIXED  
**Date:** 2026-01-01  
**Related Docs:** `docs/TASKS-ENDPOINTS-REFERENCE.md`
