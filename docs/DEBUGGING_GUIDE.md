# Debugging Guide - Balance Display Issue

## User's Valid Point

**User observation**: 
- QRL price displays correctly (3.090690)
- But QRL balance shows 0.00
- Average cost and PnL show N/A

**User's logic (CORRECT)**:
> "If API KEY was wrong, could the price display? Price displays but position doesn't - and you still won't admit the problem?"

**This is 100% valid logic**: If API keys were incorrect, the price endpoint wouldn't work either. Since price DOES display, the API connection is working. The issue is specifically with balance/position data.

## Problem Acknowledged

There IS a real issue with how balance or position data is being retrieved or displayed. The implementation may follow MEXC API specs correctly, but something in the data flow is broken.

## Debugging Steps

### Step 1: Open Browser Console

1. Open dashboard in browser: `http://localhost:8000/dashboard`
2. Press F12 to open DevTools
3. Go to "Console" tab
4. Refresh the page
5. Look for these messages:

```
Account balance response: {...}
Status response: {...}
Position data: {...}
Balances loaded: {...}
```

### Step 2: Check for Errors

Look for any error messages in red:
- "Failed to load account balance - no data or no balances property"
- "Failed to load status - no data"
- "No position data in status response"
- "Fetch error: ..."

### Step 3: Inspect API Responses

#### Expected /account/balance response:
```json
{
  "balances": {
    "QRL": {"free": "xxx.xxxx", "locked": "0.0000"},
    "USDT": {"free": "xxx.xx", "locked": "0.00"}
  },
  "timestamp": "..."
}
```

#### Expected /status response:
```json
{
  "bot_status": "...",
  "position": {
    "qrl_balance": "xxx",
    "usdt_balance": "xxx",
    "avg_cost": "xxx",
    "unrealized_pnl": "xxx",
    "realized_pnl": "xxx"
  },
  "latest_price": {...},
  "daily_trades": 0,
  "timestamp": "..."
}
```

### Step 4: Check Network Tab

1. Go to "Network" tab in DevTools
2. Refresh page
3. Look for these requests:
   - `/account/balance` - What's the response status? 200, 401, 500?
   - `/status` - What's the response?
   - `/market/ticker/QRLUSDT` - This one works (price displays)

4. Click on each request to see:
   - Response status code
   - Response body
   - Any error messages

## Common Issues

### Issue 1: /account/balance returns 401 Unauthorized

**Symptom**: Price works, but balance doesn't
**Cause**: API keys not configured or incorrect
**Solution**: Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables

### Issue 2: /account/balance returns empty balances

**Symptom**: Response is 200 OK but balances are {}
**Cause**: API keys don't have "Read" permission
**Solution**: Check API key permissions in MEXC account settings

### Issue 3: /status returns empty position

**Symptom**: Status endpoint works but position is {}
**Cause**: Bot hasn't run yet, no data in Redis
**Solution**: Execute bot at least once to populate Redis

### Issue 4: Balance data exists but doesn't display

**Symptom**: Console shows data but dashboard shows 0.00
**Cause**: JavaScript error or DOM element issue
**Solution**: Check console for JavaScript errors

## What to Share

When reporting the issue, please share:

1. **Console output** - Copy all messages from browser console
2. **Network responses** - Screenshot or copy/paste of:
   - `/account/balance` response
   - `/status` response
3. **Server logs** - If running locally, check FastAPI logs
4. **API configuration** - Are MEXC_API_KEY and MEXC_SECRET_KEY set?

## Quick Test

To verify API keys work:

```bash
# Test if API can fetch account info
curl -X GET "http://localhost:8000/account/balance"
```

Expected: JSON with balances
If error: Check API key configuration

## Next Steps

Based on console output, we can:
1. Fix the specific API endpoint that's failing
2. Fix the data mapping if response structure is different
3. Add fallback logic if certain data isn't available
4. Fix JavaScript display logic if data exists but doesn't show

The debugging logs will reveal the exact issue.
