# Dashboard Display Fix

## Issue Reported
User reported that the dashboard shows:
- QRL 持倉: 0.00 (should show actual balance)
- USDT 餘額: 500.00 (correct)
- 平均成本 (Average Cost): N/A (should show calculated value)
- 盈虧 (PnL): N/A (should show unrealized PnL)

The user confirmed there IS QRL and USDT in the account, but the dashboard is not displaying them correctly.

## Root Cause

### Problem 1: Incomplete JavaScript Function
The `loadStatus()` function in `dashboard.html` was incomplete:
- ✅ Updated `avg-cost` field
- ❌ **Did NOT update `unrealized-pnl` field**
- ❌ **Did NOT use position data as fallback for balance display**

### Problem 2: No Fallback for Balance Display
The dashboard loads balance from `/account/balance` endpoint which:
- Requires MEXC API keys to be configured
- Returns empty/zero data when API keys are missing
- Has no fallback to position data from bot execution

The position data from `/status` endpoint DOES contain balance information (qrl_balance, usdt_balance) but was not being used to populate the balance cards.

## Solution

### Fix 1: Complete loadStatus() Function

**Before:**
```javascript
async function loadStatus() {
    const data = await fetchData('/status');
    if (data && data.position) {
        const avgCost = data.position.avg_cost;
        if (avgCost) {
            document.getElementById('avg-cost').textContent = parseFloat(avgCost).toFixed(6);
        }
    }
}
```

**After:**
```javascript
async function loadStatus() {
    const data = await fetchData('/status');
    if (data && data.position) {
        // Update average cost
        const avgCost = data.position.avg_cost;
        if (avgCost && avgCost !== '0') {
            document.getElementById('avg-cost').textContent = parseFloat(avgCost).toFixed(6);
        } else {
            document.getElementById('avg-cost').textContent = 'N/A';
        }
        
        // ✅ NEW: Update unrealized PnL with color coding
        const unrealizedPnl = data.position.unrealized_pnl;
        if (unrealizedPnl !== undefined && unrealizedPnl !== null) {
            const pnlValue = parseFloat(unrealizedPnl);
            const pnlElement = document.getElementById('unrealized-pnl');
            pnlElement.textContent = pnlValue.toFixed(2) + ' USDT';
            pnlElement.style.color = pnlValue >= 0 ? '#26de81' : '#fc5c65';
        } else {
            document.getElementById('unrealized-pnl').textContent = 'N/A';
        }
        
        // ✅ NEW: Use position data as fallback for balances
        if (data.position.qrl_balance) {
            const qrlBalance = parseFloat(data.position.qrl_balance);
            const currentQrlDisplay = document.getElementById('qrl-balance').textContent;
            if (currentQrlDisplay === '--' || parseFloat(currentQrlDisplay) === 0) {
                document.getElementById('qrl-balance').textContent = qrlBalance.toFixed(4);
                document.getElementById('qrl-free').textContent = qrlBalance.toFixed(4);
            }
        }
        
        if (data.position.usdt_balance) {
            const usdtBalance = parseFloat(data.position.usdt_balance);
            const currentUsdtDisplay = document.getElementById('usdt-balance').textContent;
            if (currentUsdtDisplay === '--' || parseFloat(currentUsdtDisplay) === 0) {
                document.getElementById('usdt-balance').textContent = usdtBalance.toFixed(2);
                document.getElementById('usdt-free').textContent = usdtBalance.toFixed(2);
            }
        }
    }
    return data.position || {};
}
```

### Fix 2: Update refreshData() with Fallback

**Before:**
```javascript
async function refreshData() {
    const balances = await loadAccountBalance();
    const price = await loadPrice();
    await loadStatus();
    
    if (balances && price) {
        calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
    }
}
```

**After:**
```javascript
async function refreshData() {
    const balances = await loadAccountBalance();
    const price = await loadPrice();
    const position = await loadStatus();
    
    // Try account balance first
    if (balances && price) {
        calculateTotalValue(balances.qrlTotal, balances.usdtTotal, price);
    }
    // ✅ NEW: Fallback to position data
    else if (position && price && (position.qrl_balance || position.usdt_balance)) {
        const qrlBal = parseFloat(position.qrl_balance || 0);
        const usdtBal = parseFloat(position.usdt_balance || 0);
        calculateTotalValue(qrlBal, usdtBal, price);
    }
}
```

## What This Fixes

### Before Fix
```
Dashboard Display:
├─ QRL 持倉: 0.00           ← Wrong (not using position data)
├─ USDT 餘額: 500.00        ← May be wrong if from /account/balance
├─ 平均成本: N/A            ← Missing (field not updated)
├─ 未實現盈虧: N/A          ← Missing (field not updated)
└─ 總資產價值: --           ← Can't calculate without balances
```

### After Fix
```
Dashboard Display:
├─ QRL 持倉: 1000.0000      ✅ From position data
├─ USDT 餘額: 500.00        ✅ From position data
├─ 平均成本: 0.055000       ✅ From cost data
├─ 未實現盈虧: 5.50 USDT   ✅ From cost data (green if profit, red if loss)
└─ 總資產價值: 555.50 USDT  ✅ Calculated from position data
```

## How It Works

### Data Flow
```
Bot Execution
    └─> Phase 2: Fetch balances from MEXC
        └─> Store in Redis:
            ├─ position: {qrl_balance, usdt_balance}
            └─ cost: {avg_cost, unrealized_pnl}

/status Endpoint
    └─> Merge position + cost data
        └─> Return complete data

Dashboard
    ├─> Try /account/balance (requires API keys)
    ├─> Load /status (always works)
    └─> Use position data as fallback
        ├─> Display balances from position
        ├─> Display avg_cost
        ├─> Display unrealized_pnl with color
        └─> Calculate total value
```

### Fallback Logic
1. Dashboard tries to load balance from `/account/balance`
2. If that fails (no API keys or error), it uses position data from `/status`
3. Position data is updated by the bot during Phase 2 execution
4. This ensures the dashboard always shows the latest bot-tracked balances

## Benefits

1. **Dashboard works without API keys configured**
   - Uses position data from bot execution
   - Shows last known balances from Redis

2. **All fields properly populated**
   - Average cost displayed
   - Unrealized PnL displayed with color coding
   - Total asset value calculated

3. **Better user experience**
   - Green color for profit, red for loss
   - "N/A" shown when data is truly not available
   - Fallback ensures data is always shown when possible

## Testing

To test the fix:
1. Start the API without MEXC API keys configured
2. Run the bot at least once to populate position data
3. Open the dashboard: `http://localhost:8000/dashboard`
4. Verify all fields show correct values:
   - QRL balance from position data
   - USDT balance from position data
   - Average cost from cost data
   - Unrealized PnL with color coding
   - Total asset value calculated correctly

## Files Changed

- `templates/dashboard.html`: 49 additions, 2 deletions
  - Enhanced `loadStatus()` function
  - Updated `refreshData()` with fallback logic

## Commit

Fix dashboard to display position data and unrealized PnL properly (1e39f78)
