# Issue #12 Fix - Dashboard Data Source Priority

## Problem Summary

The dashboard was incorrectly prioritizing stale Redis position data over real-time API balance data. This caused the dashboard to display outdated balances when:
1. User deposited/withdrew funds outside the bot
2. User made manual trades not tracked by the bot
3. Bot hadn't run recently, causing Redis data to be stale

## Root Cause

**Wrong Priority:**
```javascript
// WRONG: Prioritize Redis data (stale)
if (position && price && (position.qrl_balance || position.usdt_balance)) {
    // Use Redis data (only updates when bot runs)
}
else if (balances && price) {
    // Fallback to API (real-time)
}
```

Additionally, `loadStatus()` was overwriting the real-time API balance displays with potentially stale Redis data.

## Solution

### Data Source Strategy

| Data Type | Primary Source | Why |
|-----------|---------------|-----|
| **QRL/USDT Balance** | MEXC API (`/account/balance`) | Real-time, reflects all activities |
| **Average Cost** | Redis (`cost_data`) | Bot-calculated based on its trades |
| **Unrealized PnL** | Redis (`cost_data`) | Bot-calculated based on avg_cost |
| **Total Value** | Calculated from API balance + current price | Most accurate |

### Changes Made

#### 1. Updated `loadStatus()` Function
**Before:** Updated balance displays with Redis data (causing stale data to be shown)

**After:** Only updates analytics fields (avg_cost, unrealized_pnl)
```javascript
// NOTE: Do NOT update balance from Redis position data
// Balance should come from real-time API (/account/balance)
// Redis position data may be stale (only updates when bot runs)

// Update average cost (bot-specific analysis)
// Update unrealized PnL (bot-specific analysis)
```

#### 2. Fixed `refreshData()` Priority
**Before:** Redis position data was primary source

**After:** API balance is primary, Redis is fallback
```javascript
// PRIMARY: Use real-time API balance (most accurate and up-to-date)
// API balance reflects all activities (bot trades + manual deposits/withdrawals)
if (balances && price) {
    calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
}
// FALLBACK: Only use Redis position data if API fails
// Redis data may be stale (only updates when bot runs)
else if (position && price && (position.qrl_balance || position.usdt_balance)) {
    const qrlBal = parseFloat(position.qrl_balance || 0);
    const usdtBal = parseFloat(position.usdt_balance || 0);
    calculateTotalValue(qrlBal, usdtBal, price);
}
```

## Testing the Fix

### Manual Testing Steps

1. **Start the API server:**
   ```bash
   python main.py
   ```

2. **Open the dashboard:**
   Navigate to `http://localhost:8000/dashboard`

3. **Verify real-time balance display:**
   - Check that QRL and USDT balances match the MEXC API
   - Open browser DevTools Console
   - Look for log message: `Account balance response:`
   - Verify the displayed balances match the API response

4. **Verify analytics display:**
   - Check that "平均成本" (Average Cost) shows the bot's calculated cost
   - Check that "未實現盈虧" (Unrealized PnL) shows the bot's PnL calculation
   - These values come from Redis and should reflect the bot's trading history

5. **Test with stale Redis data:**
   - If bot hasn't run recently, Redis data will be stale
   - Dashboard should still show current balance from API ✅
   - Analytics (avg_cost, PnL) will show last bot calculation (expected behavior)

### Expected Behavior

✅ **Balance displays (QRL, USDT):** Always shows real-time data from MEXC API
✅ **Average cost:** Shows bot-calculated cost from Redis (or N/A if no trades)
✅ **Unrealized PnL:** Shows bot-calculated PnL from Redis (or N/A if no trades)
✅ **Total value:** Calculated from real-time API balance × current price

### What Was Fixed

| Scenario | Before (Wrong) | After (Correct) |
|----------|---------------|-----------------|
| User deposits 1000 QRL, bot hasn't run | Shows 0 QRL (stale Redis) ❌ | Shows 1000 QRL (real-time API) ✅ |
| User withdraws 500 USDT manually | Shows old balance (Redis) ❌ | Shows updated balance (API) ✅ |
| Bot bought 500 QRL at $0.055 | Shows only bot's 500 QRL ❌ | Shows total balance from API ✅ |
| API fails but Redis has data | No balance shown ❌ | Shows Redis balance (fallback) ✅ |

## Files Changed

- **templates/dashboard.html**
  - Modified `loadStatus()`: Removed balance update logic, kept only analytics updates
  - Modified `refreshData()`: Reversed priority (API first, Redis fallback)
  - Added explanatory comments for future developers

## References

- Issue: #12
- Related PR: #13 (balance display issue)
- Documentation: `docs/DATA_SOURCE_STRATEGY.md`
- Documentation: `docs/FINAL_FIX_SUMMARY.md`

## Summary

The fix ensures that the dashboard always displays the user's real-time balance from the MEXC API, while bot-specific analytics (average cost, PnL) continue to come from Redis. This provides the most accurate and up-to-date information to users.

**Key Principle:**
- **Balance = Reality (from API)** ← Real-time source of truth
- **Analytics = Bot's perspective (from Redis)** ← Bot trading performance

These are two different things and should never be confused.
