# 策略設計快速參考指南

> **Quick Reference**: 策略公式與計算的速查表

## 📊 核心公式速查

### 移動平均線 (MA)

```
MA(n) = Σ(P_i) / n

示例: MA(7) = (0.048 + 0.049 + ... + 0.051) / 7
```

### 信號強度

```
Signal_Strength = [(MA_short - MA_long) / MA_long] × 100%

示例: (0.0505 - 0.0495) / 0.0495 × 100% = 2.02%
```

### 買入條件

```
BUY = (MA_short > MA_long) AND (Price ≤ Avg_Cost × 1.00)

檢查項:
✓ 短期 MA 高於長期 MA (金叉)
✓ 當前價格不高於平均成本
```

### 賣出條件

```
SELL = (MA_short < MA_long) AND (Price ≥ Avg_Cost × 1.03)

檢查項:
✓ 短期 MA 低於長期 MA (死叉)
✓ 當前價格至少高於成本 3%
```

### 平均成本

```
Average_Cost = Σ(Price_i × Amount_i) / Σ(Amount_i)

示例:
買入 1: 5,000 @ 0.0520 = 260 USDT
買入 2: 3,000 @ 0.0480 = 144 USDT
平均成本 = (260 + 144) / (5,000 + 3,000) = 0.0505
```

### 倉位分層

```
Total_QRL = Core_QRL + Swing_QRL + Active_QRL

標準配置:
Core (70%):   不交易，長期持有
Swing (20%):  波段交易
Active (10%): 機動交易

可交易量 = Swing + Active = 30%
```

---

## 🛡️ 風險控制速查

### 每日交易限制

```
Allowed = (Daily_Trades < MAX_DAILY_TRADES)

預設: MAX_DAILY_TRADES = 5
```

### 交易間隔

```
Elapsed = Current_Time - Last_Trade_Time
Allowed = (Elapsed ≥ MIN_TRADE_INTERVAL)

預設: MIN_TRADE_INTERVAL = 300 秒 (5 分鐘)
```

### 核心倉位保護

```
Core_QRL = Total_QRL × 0.70
Tradeable_QRL = Total_QRL - Core_QRL

賣出限制: 最多賣出 Tradeable_QRL
```

### USDT 儲備

```
Min_Reserve = Total_Value × 0.20
Available_USDT = USDT_Balance - Min_Reserve

買入限制: 最多使用 Available_USDT
```

---

## 💡 實用計算範例

### 範例 1: 快速判斷買入信號

```
給定:
MA_7 = 0.0505
MA_25 = 0.0495
Price = 0.0490
Avg_Cost = 0.0500

步驟:
1. MA 條件: 0.0505 > 0.0495 ✓
2. 價格條件: 0.0490 ≤ 0.0500 ✓
3. 結論: BUY ✓
```

### 範例 2: 快速判斷賣出信號

```
給定:
MA_7 = 0.0495
MA_25 = 0.0505
Price = 0.0520
Avg_Cost = 0.0500

步驟:
1. MA 條件: 0.0495 < 0.0505 ✓
2. 利潤條件: 0.0520 ≥ (0.0500 × 1.03 = 0.0515) ✓
3. 實際利潤: (0.0520 - 0.0500) / 0.0500 = 4.0% ✓
4. 結論: SELL ✓
```

### 範例 3: 計算可賣出數量

```
給定:
Total_QRL = 10,000
Core_Position_PCT = 0.70

計算:
Core_QRL = 10,000 × 0.70 = 7,000
Max_Sell = 10,000 - 7,000 = 3,000 QRL
```

### 範例 4: 計算買入後成本

```
當前:
Holdings = 10,000 QRL @ 0.0500 = 500 USDT

新買入:
Buy = 2,000 QRL @ 0.0475 = 95 USDT

計算新成本:
New_Total_Cost = 500 + 95 = 595 USDT
New_Total_QRL = 10,000 + 2,000 = 12,000
New_Avg_Cost = 595 / 12,000 = 0.04958
```

---

## 🎯 決策流程圖

### 買入決策流程

```
1. 收集數據
   ├─ 計算 MA_7 和 MA_25
   ├─ 獲取當前價格
   └─ 查詢平均成本

2. 檢查信號條件
   ├─ MA_7 > MA_25? → 否 → HOLD
   └─ 是 ↓
       └─ Price ≤ Avg_Cost? → 否 → HOLD
           └─ 是 ↓

3. 檢查風險控制
   ├─ Daily_Trades < 5? → 否 → REJECT
   ├─ Elapsed ≥ 300s? → 否 → REJECT
   └─ USDT_Balance > 0? → 否 → REJECT
       └─ 全部是 ↓

4. 計算買入數量
   ├─ 計算可用 USDT
   ├─ 限制單筆金額
   └─ 執行買入

5. 更新狀態
   ├─ 更新平均成本
   ├─ 增加交易計數
   └─ 記錄交易時間
```

### 賣出決策流程

```
1. 收集數據
   ├─ 計算 MA_7 和 MA_25
   ├─ 獲取當前價格
   └─ 查詢平均成本

2. 檢查信號條件
   ├─ MA_7 < MA_25? → 否 → HOLD
   └─ 是 ↓
       └─ Price ≥ Avg_Cost × 1.03? → 否 → HOLD
           └─ 是 ↓

3. 檢查風險控制
   ├─ Daily_Trades < 5? → 否 → REJECT
   ├─ Elapsed ≥ 300s? → 否 → REJECT
   └─ Tradeable_QRL > 0? → 否 → REJECT
       └─ 全部是 ↓

4. 計算賣出數量
   ├─ 計算可交易量
   ├─ 限制單筆數量
   └─ 執行賣出

5. 更新狀態
   ├─ 成本保持不變
   ├─ 增加交易計數
   ├─ 記錄已實現利潤
   └─ 記錄交易時間
```

---

## 📋 檢查清單

### 交易前檢查

- [ ] MA 數據足夠 (至少 25 個價格點)
- [ ] 信號條件明確 (BUY 或 SELL)
- [ ] 每日交易次數未達上限
- [ ] 距離上次交易 ≥ 5 分鐘
- [ ] 買入: USDT 餘額充足
- [ ] 賣出: 可交易 QRL 充足

### 交易後驗證

- [ ] 成本更新正確 (只有買入時更新)
- [ ] 數量變化正確
- [ ] 交易計數增加
- [ ] 交易時間記錄
- [ ] 已實現利潤記錄 (賣出時)

---

## 🔢 常用數值

| 參數 | 預設值 | 說明 |
|------|--------|------|
| MA_SHORT_PERIOD | 7 | 短期 MA 週期 |
| MA_LONG_PERIOD | 25 | 長期 MA 週期 |
| BUY_THRESHOLD | 1.00 | 買入價格閾值 (≤ 成本) |
| SELL_THRESHOLD | 1.03 | 賣出價格閾值 (≥ 成本×1.03) |
| MAX_DAILY_TRADES | 5 | 每日最大交易次數 |
| MIN_TRADE_INTERVAL | 300s | 最小交易間隔 (5 分鐘) |
| CORE_POSITION_PCT | 0.70 | 核心倉位比例 (70%) |
| SWING_POSITION_PCT | 0.20 | 波段倉位比例 (20%) |
| ACTIVE_POSITION_PCT | 0.10 | 機動倉位比例 (10%) |
| MAX_TRADE_PCT | 0.30 | 單筆最大交易比例 (30%) |
| USDT_RESERVE_PCT | 0.20 | USDT 儲備比例 (20%) |

---

## 🔗 相關文檔

- **完整公式文檔**: [STRATEGY_DESIGN_FORMULAS.md](./STRATEGY_DESIGN_FORMULAS.md)
- **計算實例**: [STRATEGY_CALCULATION_EXAMPLES.md](./STRATEGY_CALCULATION_EXAMPLES.md)
- **策略概述**: [1-qrl-accumulation-strategy.md](./1-qrl-accumulation-strategy.md)

---

## 💻 代碼參考

### 策略實現

```python
from src.app.domain.strategies.trading_strategy import TradingStrategy

# 初始化策略
strategy = TradingStrategy(ma_short_period=7, ma_long_period=25)

# 計算 MA
ma_7 = strategy.calculate_moving_average(short_prices)
ma_25 = strategy.calculate_moving_average(long_prices)

# 生成信號
signal = strategy.generate_signal(
    price=current_price,
    short_prices=short_prices,
    long_prices=long_prices,
    avg_cost=average_cost
)

# 計算信號強度
strength = strategy.calculate_signal_strength(ma_7, ma_25)
```

### 風險檢查

```python
from src.app.domain.risk.limits import RiskManager

# 初始化風險管理器
risk_mgr = RiskManager(
    max_daily_trades=5,
    min_trade_interval=300,
    core_position_pct=0.70
)

# 檢查所有風險
result = risk_mgr.check_all_risks(
    signal="BUY",
    daily_trades=3,
    last_trade_time=last_trade_timestamp,
    position_layers=position_data,
    usdt_balance=usdt_amount
)

if result["allowed"]:
    # 執行交易
    execute_trade()
else:
    # 記錄拒絕原因
    log_rejection(result["reason"])
```

---

**版本**: 1.0.0  
**最後更新**: 2025-12-27  
**用途**: 快速查閱策略公式與計算方法
