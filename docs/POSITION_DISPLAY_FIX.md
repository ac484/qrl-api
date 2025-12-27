# Position Display Fix

## Issue (問題)
分析持倉不顯示原因 - The position analysis data was not being displayed in the dashboard.

## Root Cause (根本原因)

### Problem Analysis
1. **Position data was never initialized**: The `set_position()` method existed in Redis client but was never called by the bot
2. **Cost data was stored separately**: Cost tracking data (`avg_cost`, `unrealized_pnl`, `realized_pnl`) was stored in a different Redis key (`cost`) than position data (`position`)
3. **Dashboard expected merged data**: The dashboard tried to display `avg_cost` and `unrealized_pnl` from the position object returned by `/status` endpoint, but these fields were missing

### Code Flow Before Fix
```
/status endpoint
    ├─> get_position() → Empty dict (never set)
    ├─> get_cost_data() → Has data but not used
    └─> Returns position without cost data
```

## Solution (解決方案)

### Changes Made

#### 1. Updated `/status` endpoint (main.py)
- Fetch both `position` data and `cost_data` from Redis
- Merge cost data into position data before returning
- This ensures the dashboard receives all necessary fields

```python
# Before
position = await redis_client.get_position()
return StatusResponse(position=position, ...)

# After
position = await redis_client.get_position()
cost_data = await redis_client.get_cost_data()
merged_position = dict(position)
if cost_data:
    merged_position.update(cost_data)
return StatusResponse(position=merged_position, ...)
```

#### 2. Updated bot Phase 2 - Data Collection (bot.py)
- Store position data (QRL and USDT balances) in Redis after fetching from MEXC
- Calculate and store cost data (avg_cost, total_invested, unrealized_pnl)
- This initializes the position tracking system

```python
# Store position data
position_data = {
    "qrl_balance": str(qrl_balance),
    "usdt_balance": str(usdt_balance),
}
await self.redis.set_position(position_data)

# Calculate and store cost data
await self.redis.set_cost_data(
    avg_cost=avg_cost,
    total_invested=total_invested,
    unrealized_pnl=unrealized_pnl
)
```

#### 3. Updated BUY execution (bot.py)
- After BUY order, recalculate weighted average cost
- Update total invested amount
- Reset unrealized PnL (since we just bought at current price)

```python
# Calculate new weighted average cost
new_total_invested = old_total_invested + usdt_to_use
new_qrl_balance = qrl_balance + qrl_quantity
new_avg_cost = new_total_invested / new_qrl_balance

await self.redis.set_cost_data(
    avg_cost=new_avg_cost,
    total_invested=new_total_invested,
    unrealized_pnl=0
)
```

#### 4. Updated SELL execution (bot.py)
- After SELL order, calculate realized PnL from the trade
- Update unrealized PnL for remaining position
- Track cumulative realized PnL

```python
# Calculate realized PnL from this trade
realized_pnl_from_trade = (price - avg_cost) * qrl_to_sell
new_realized_pnl = old_realized_pnl + realized_pnl_from_trade

# Update unrealized PnL for remaining position
new_qrl_balance = qrl_balance - qrl_to_sell
unrealized_pnl = (price - avg_cost) * new_qrl_balance

await self.redis.set_cost_data(
    avg_cost=avg_cost,
    total_invested=avg_cost * new_qrl_balance,
    unrealized_pnl=unrealized_pnl,
    realized_pnl=new_realized_pnl
)
```

### Code Flow After Fix
```
Bot Phase 2 (Data Collection)
    ├─> Fetch balances from MEXC
    ├─> set_position(qrl_balance, usdt_balance)
    └─> set_cost_data(avg_cost, total_invested, unrealized_pnl)

/status endpoint
    ├─> get_position() → {qrl_balance, usdt_balance}
    ├─> get_cost_data() → {avg_cost, total_invested, unrealized_pnl, realized_pnl}
    ├─> Merge both datasets
    └─> Returns complete position data

Dashboard
    └─> Displays all fields: balances, avg_cost, unrealized_pnl, realized_pnl
```

## Testing (測試)

### Manual Testing
Run the position display test:
```bash
python test_position_display.py
```

This test verifies:
1. Position data can be stored and retrieved
2. Cost data can be stored and retrieved
3. Both datasets merge correctly
4. All expected fields are present

### Integration Testing
1. Start Redis: `redis-server`
2. Start the API: `python main.py`
3. Execute a trading cycle: `POST /execute`
4. Check status: `GET /status`
5. View dashboard: Open `http://localhost:8000/dashboard`

### Expected Results
The dashboard should now display:
- ✅ QRL Balance (QRL 餘額)
- ✅ USDT Balance (USDT 餘額)
- ✅ Average Cost (平均成本)
- ✅ Unrealized PnL (未實現盈虧)
- ✅ Total Asset Value (總資產價值)

## Files Modified (修改的文件)

1. **main.py**: Updated `/status` endpoint to merge position and cost data
2. **bot.py**: 
   - Phase 2: Added position and cost data initialization
   - Phase 5: Added cost tracking for BUY and SELL executions
3. **test_position_display.py**: New test file for verifying the fix

## Impact (影響)

### Benefits
- Dashboard now displays complete position information
- Users can see their average cost and unrealized PnL
- Position tracking is maintained across bot executions
- Better visibility into trading performance

### No Breaking Changes
- Existing functionality remains unchanged
- Backward compatible with existing Redis data
- No API signature changes

## Future Enhancements (未來改進)

1. Add position history tracking
2. Display realized PnL on dashboard
3. Add position layer visualization (core/swing/active)
4. Implement position rebalancing alerts
