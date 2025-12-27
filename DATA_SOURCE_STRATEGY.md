# Data Source Strategy - Final Correct Implementation

## User Feedback History

### Issue 1: Position data not displaying
- User: Dashboard shows N/A for avg_cost and PnL
- Fix: Merged position + cost data in backend

### Issue 2: Balance showing 0 when should have value
- User: QRL shows 0.00 but I have QRL
- Wrong Fix: Made Redis position data override API balance
- User feedback: "Don't be silly - if env vars were wrong, nothing would display"

### Issue 3: ALL DATA WRONG
- User: "Everything should be real source, and USDT isn't even 500!"
- **ROOT CAUSE IDENTIFIED**: Redis position data is STALE
- Redis only updates when bot runs
- Dashboard was showing OLD Redis data instead of REAL-TIME API data

## The Correct Data Source Strategy

### Data Types and Their Sources

| Data Type | Primary Source | Fallback | Update Frequency | Reason |
|-----------|---------------|----------|------------------|--------|
| **QRL Balance** | `/account/balance` API | Redis position | Real-time | User's actual balance can change outside bot |
| **USDT Balance** | `/account/balance` API | Redis position | Real-time | User's actual balance can change outside bot |
| **Average Cost** | Redis cost_data | N/A | Bot execution | Calculated by bot based on trades |
| **Unrealized PnL** | Redis cost_data | N/A | Bot execution | Calculated by bot based on avg_cost |
| **Realized PnL** | Redis cost_data | N/A | Bot execution | Calculated by bot based on trades |
| **Total Value** | Calculated from API balance + current price | - | Real-time | Most accurate calculation |

### Why This is Correct

**Real-time API Balance (Primary for balances):**
- User may deposit/withdraw outside of bot
- Manual trades not tracked by bot
- API balance is ALWAYS the ground truth for actual holdings
- Updated every time dashboard refreshes

**Redis Position Data (Primary for analysis):**
- Bot tracks its own trades
- Calculates avg_cost based on bot's buy orders
- Calculates PnL based on bot's trading history
- Only relevant for bot's trading performance analysis

## Implementation

### Dashboard Data Flow

```
Page Load/Refresh
    ↓
loadAccountBalance()
    ├─> Fetch /account/balance (MEXC API)
    ├─> Display QRL balance (REAL-TIME) ✅
    └─> Display USDT balance (REAL-TIME) ✅
    ↓
loadPrice()
    └─> Fetch current QRL/USDT price
    ↓
loadStatus()
    ├─> Fetch /status (Redis data)
    ├─> Display avg_cost (bot-calculated) ✅
    ├─> Display unrealized_pnl (bot-calculated) ✅
    └─> Do NOT override balances with Redis data ❌
    ↓
calculateTotalValue()
    └─> Use API balance + current price (MOST ACCURATE) ✅
```

### Code Implementation

```javascript
async function refreshData() {
    // Get real-time data from API
    const balances = await loadAccountBalance();  // MEXC API - REAL-TIME
    const price = await loadPrice();               // Market price - REAL-TIME
    const position = await loadStatus();           // Redis - BOT DATA ONLY
    
    // PRIMARY: Use real-time API balance
    if (balances && price) {
        calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
    }
    // FALLBACK: Only if API fails
    else if (position && price && (position.qrl_balance || position.usdt_balance)) {
        const qrlBal = parseFloat(position.qrl_balance || 0);
        const usdtBal = parseFloat(position.usdt_balance || 0);
        calculateTotalValue(qrlBal, usdtBal, price);
    }
}
```

## What Was Wrong Before

### Attempt 1: Fallback when display is 0
```javascript
// WRONG - only updated when display showed 0
if (currentQrlDisplay === '--' || parseFloat(currentQrlDisplay) === 0) {
    document.getElementById('qrl-balance').textContent = qrlBalance.toFixed(4);
}
```
**Problem**: API might return 0 legitimately, then Redis would override with stale data

### Attempt 2: Always override with Redis
```javascript
// WRONG - always overrode with potentially stale data
if (data.position.qrl_balance) {
    const qrlBalance = parseFloat(data.position.qrl_balance);
    if (qrlBalance > 0) {
        document.getElementById('qrl-balance').textContent = qrlBalance.toFixed(4);
    }
}
```
**Problem**: Redis data only updates when bot runs. If bot hasn't run recently, shows OLD balance

### Correct Approach: Never override balance
```javascript
// CORRECT - let API balance display naturally, don't override
async function loadStatus() {
    // Only update analysis fields (avg_cost, unrealized_pnl)
    // Do NOT touch balance display
    if (data.position.avg_cost) {
        document.getElementById('avg-cost').textContent = ...;
    }
    if (data.position.unrealized_pnl) {
        document.getElementById('unrealized-pnl').textContent = ...;
    }
    // No balance override code
}
```

## User's Balance vs Bot's Position

### Scenario: User deposits 1000 QRL

**Before bot runs:**
- API balance: 1000 QRL (CORRECT - real balance)
- Redis position: 0 QRL (bot hasn't seen the deposit)
- Dashboard SHOULD show: 1000 QRL ✅

**With wrong logic (override with Redis):**
- Dashboard shows: 0 QRL ❌ (WRONG - using stale Redis data)

**With correct logic (use API):**
- Dashboard shows: 1000 QRL ✅ (CORRECT - real-time API)

### Scenario: Bot bought 500 QRL at $0.055

**After bot runs:**
- API balance: 1500 QRL (correct - includes deposit + bot purchase)
- Redis position: 500 QRL (bot only knows its own trades)
- Redis avg_cost: 0.055 (bot's purchase cost)
- Dashboard SHOULD show:
  - Balance: 1500 QRL (from API) ✅
  - Avg cost: 0.055 (from Redis) ✅
  - PnL: calculated from bot's 500 QRL ✅

## Summary

**The Fundamental Principle:**
- **Balance = Reality (from API)**
- **Analysis = Bot's perspective (from Redis)**

These are TWO DIFFERENT THINGS and should never be confused or mixed.

The user was right to be frustrated - the dashboard was showing stale cached data instead of their real balance.

## Commits

1-6: Backend fixes
7-8: Frontend fixes (initial)
9: Wrong - made Redis override API (commit fa5a42b)
10: **CORRECT** - API is primary source for balance (commit 2bf6753) ✅
