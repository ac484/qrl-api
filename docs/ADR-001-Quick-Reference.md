# 快速參考：Rebalance 決策流程

## 一頁速覽：何時買入、賣出或持有

### 輸入數據
```
├─ QRL 餘額：qrl_balance
├─ USDT 餘額：usdt_balance
└─ 當前價格：price
```

### 計算步驟
```
1. total_value = qrl_balance × price + usdt_balance
2. target_value = total_value × 50%
3. qrl_value = qrl_balance × price
4. delta = qrl_value - target_value
5. notional = |delta|
```

### 決策流程圖

```
開始
  │
  ▼
╔═══════════════════════╗
║ 價格有效？            ║
║ price > 0?            ║
╚═══════════════════════╝
  │          │
  否         是
  │          │
  ▼          ▼
[HOLD]   ╔═══════════════════════╗
價格無效  ║ 總價值有效？          ║
         ║ total_value > 0?      ║
         ╚═══════════════════════╝
           │          │
           否         是
           │          │
           ▼          ▼
        [HOLD]   ╔═══════════════════════╗
        無資產    ║ 偏差 ≥ 5 USDT？      ║
                 ║ notional ≥ 5.0?      ║
                 ╚═══════════════════════╝
                   │          │
                   否         是
                   │          │
                   ▼          ▼
                [HOLD]   ╔═══════════════════════╗
                太小     ║ 偏差 ≥ 1%？          ║
                        ║ notional/total ≥ 1%? ║
                        ╚═══════════════════════╝
                          │          │
                          否         是
                          │          │
                          ▼          ▼
                       [HOLD]   ╔═══════════════════════╗
                       在閾值內  ║ QRL 過多？            ║
                                ║ delta > 0?            ║
                                ╚═══════════════════════╝
                                  │          │
                                  是         否
                                  │          │
                                  ▼          ▼
                           ╔═══════════╗  ╔═══════════╗
                           ║ 賣出 QRL  ║  ║ 買入 QRL  ║
                           ╚═══════════╝  ╚═══════════╝
                                 │              │
                                 ▼              ▼
                     ╔══════════════════╗  ╔══════════════════╗
                     ║ quantity =       ║  ║ quantity =       ║
                     ║ min(需要,        ║  ║ min(需要,        ║
                     ║     qrl_balance) ║  ║     usdt/price)  ║
                     ╚══════════════════╝  ╚══════════════════╝
                              │                   │
                              ▼                   ▼
                      ╔═════════════╗     ╔═════════════╗
                      ║ action:     ║     ║ USDT 足夠？ ║
                      ║ SELL        ║     ║ qty > 0?    ║
                      ╚═════════════╝     ╚═════════════╝
                                            │        │
                                            否       是
                                            │        │
                                            ▼        ▼
                                        [HOLD]  ╔═════════════╗
                                        USDT    ║ action:     ║
                                        不足    ║ BUY         ║
                                               ╚═════════════╝
```

## 快速判斷表

| 條件 | 動作 | 原因 |
|-----|-----|------|
| price ≤ 0 | **HOLD** | 價格無效 |
| total_value ≤ 0 | **HOLD** | 無資產可平衡 |
| notional < 5 USDT | **HOLD** | 交易額太小 |
| notional/total < 1% | **HOLD** | 偏差在容忍範圍 |
| delta > 0 且通過閾值 | **SELL** | QRL 價值過高 |
| delta < 0 且通過閾值 | **BUY** | QRL 價值過低 |
| delta ≈ 0 | **HOLD** | 已平衡 |

## 真實案例速查

### 案例 1：價格上漲 → 賣出
```
前：100 QRL @ 1 USDT + 100 USDT
  QRL: 100 USDT (50%)
  USDT: 100 USDT (50%)
  ✅ 平衡

漲：100 QRL @ 2 USDT + 100 USDT
  QRL: 200 USDT (67%)
  USDT: 100 USDT (33%)
  ❌ 失衡

計算：
  target = 300 × 50% = 150 USDT
  delta = 200 - 150 = +50 USDT
  quantity = 50 / 2 = 25 QRL

動作：SELL 25 QRL

後：75 QRL @ 2 USDT + 150 USDT
  QRL: 150 USDT (50%)
  USDT: 150 USDT (50%)
  ✅ 恢復平衡
```

### 案例 2：價格下跌 → 買入
```
前：100 QRL @ 1 USDT + 100 USDT
  ✅ 平衡 (50:50)

跌：100 QRL @ 0.5 USDT + 100 USDT
  QRL: 50 USDT (33%)
  USDT: 100 USDT (67%)
  ❌ 失衡

計算：
  target = 150 × 50% = 75 USDT
  delta = 50 - 75 = -25 USDT
  quantity = 25 / 0.5 = 50 QRL

動作：BUY 50 QRL

後：150 QRL @ 0.5 USDT + 75 USDT
  QRL: 75 USDT (50%)
  USDT: 75 USDT (50%)
  ✅ 恢復平衡
```

### 案例 3：微小偏差 → 持有
```
當前：100 QRL @ 2 USDT + 202 USDT
  QRL: 200 USDT
  USDT: 202 USDT
  Total: 402 USDT

計算：
  target = 402 × 50% = 201 USDT
  delta = 200 - 201 = -1 USDT
  notional = 1 USDT

判斷：
  1 < 5 USDT ✗ (低於最小交易額)
  
動作：HOLD (Within threshold)
```

## 參數速查

| 參數 | 默認值 | 說明 | 何時調整 |
|-----|-------|------|---------|
| `target_ratio` | 0.5 | 50% QRL | 改變風險偏好時 |
| `min_notional_usdt` | 5.0 | 最小交易 5U | 根據賬戶大小 |
| `threshold_pct` | 0.01 | 1% 偏差閾值 | 平衡頻率 vs 手續費 |

### 賬戶大小建議

| 總資產 (USDT) | min_notional | threshold_pct |
|--------------|--------------|---------------|
| < 500 | 5 | 2% |
| 500 - 2000 | 5 | 1.5% |
| 2000 - 10000 | 10 | 1% |
| > 10000 | 20-50 | 1% |

## 常見問題

### Q1: 為什麼不是 50% 數量而是 50% 價值？
**A:** 因為價格會變動。如果維持數量平衡，價格變動時價值會失衡。

**例子：**
```
錯誤方法（數量 50:50）：
  初始：100 QRL + 100 USDT
  價格漲至 10 USDT/QRL
  結果：1000 USDT QRL + 100 USDT → 91:9（極度失衡）

正確方法（價值 50:50）：
  初始：100 QRL @ 1 + 100 USDT
  價格漲至 10 USDT/QRL
  賣出 45 QRL
  結果：55 QRL @ 10 + 550 USDT → 550:550（保持平衡）
```

### Q2: 為什麼設置閾值？
**A:** 避免頻繁交易浪費手續費。

**例子：**
```
無閾值（每次都交易）：
  微小波動 0.1% → 交易手續費 0.1%
  一天波動 10 次 → 手續費 1%
  一個月 → 手續費 ~30%（吃掉大部分收益）

有閾值（1% 才交易）：
  微小波動 < 1% → 不交易
  一天可能 1-2 次
  一個月 → 手續費 ~3%（可接受）
```

### Q3: 資金不足時怎麼辦？
**A:** 盡力而為，部分平衡。

**例子：**
```
需要買入 100 QRL (200 USDT)
但只有 50 USDT
→ 買入 50/2 = 25 QRL
→ 部分接近目標，總比不做好
```

### Q4: 極端行情怎麼辦？
**A:** 建議添加熔斷機制。

**建議：**
```python
# 價格變化超過 20% → 暫停
if abs(price_change) > 0.2:
    return "HOLD", "Abnormal price movement"

# 閃崩檢測 → 暫停 1 小時
if is_flash_crash(price_history):
    halt_trading(duration=3600)
```

## 監控指標

### 關鍵指標
- `rebalance_frequency`: 每天再平衡次數（目標：1-3 次）
- `avg_deviation`: 平均偏差百分比（目標：< 2%）
- `total_fees`: 累積手續費（目標：< 月收益 10%）
- `balance_ratio`: 當前比例（目標：45-55%）

### 警報條件
- 🔴 連續 3 次再平衡失敗
- 🟡 偏差 > 10%（極度失衡）
- 🟡 每日交易 > 10 次（過度交易）
- 🔴 USDT 或 QRL 餘額為 0

## 進階技巧

### 1. 動態閾值
```python
# 高波動時提高閾值，減少交易
if market_volatility > 0.05:
    threshold_pct = 0.03  # 從 1% 提高到 3%
```

### 2. 冷卻期
```python
# 1 小時內不重複交易
if time_since_last_trade < 3600:
    return "HOLD", "In cooldown"
```

### 3. 趨勢調整
```python
# 上升趨勢：延遲賣出
if price > ma_7 > ma_25:
    threshold_pct *= 1.5  # 提高賣出閾值
```

## 總結

✅ **使用此頁面：**
- 快速理解決策邏輯
- 查詢常見案例
- 調整參數參考
- 故障排查

📚 **深入學習：**
- 詳細算法 → `ADR-001-Rebalance-Logic-Deep-Dive.md`
- 架構設計 → `ADR-001-Architecture-Diagrams.md`
- 實施計劃 → `ADR-001-Rebalance-Integration-15min-Job.md`

---
**最後更新：** 2026-01-01  
**版本：** 1.0  
**用途：** 快速參考和決策指南
