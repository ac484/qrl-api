# Rebalance 再平衡邏輯詳細討論

## 目錄
1. [核心概念](#核心概念)
2. [算法詳解](#算法詳解)
3. [決策樹分析](#決策樹分析)
4. [實際案例](#實際案例)
5. [參數調優](#參數調優)
6. [風險考量](#風險考量)
7. [優化建議](#優化建議)

## 核心概念

### 什麼是對稱再平衡？

對稱再平衡（Symmetric Rebalancing）是一種投資組合管理策略，目標是維持兩種資產的**價值**比例為 50:50。

**關鍵理解：**
- ⚠️ 不是維持 QRL 和 USDT 的**數量**相等
- ✅ 而是維持它們的**價值（以 USDT 計）**相等
- 📊 當市場波動導致比例失衡時，通過買賣調整

### 為什麼需要再平衡？

**問題場景：**
```
初始狀態（完美平衡）：
- 持有：100 QRL，價格 1 USDT/QRL
- QRL 價值：100 USDT
- USDT 持有：100 USDT
- 總價值：200 USDT
- 比例：50% QRL : 50% USDT ✅

QRL 價格上漲到 2 USDT/QRL：
- QRL 價值：100 * 2 = 200 USDT
- USDT 持有：100 USDT
- 總價值：300 USDT
- 比例：66.7% QRL : 33.3% USDT ❌ 失衡！

需要再平衡：
- 目標 QRL 價值：300 * 50% = 150 USDT
- 需要賣出：(200-150)/2 = 25 QRL
- 再平衡後：75 QRL (150 USDT) + 150 USDT = 50:50 ✅
```

**優勢：**
1. **風險管理**：避免過度集中於單一資產
2. **自動止盈**：價格上漲時賣出部分，鎖定利潤
3. **逢低買入**：價格下跌時買入更多，降低平均成本
4. **紀律性**：機械化執行，避免情緒化決策

## 算法詳解

### 完整代碼流程

```python
class RebalanceService:
    def __init__(
        self,
        balance_service,           # 餘額服務（獲取 QRL/USDT 餘額）
        redis_client=None,         # Redis 客戶端（儲存計劃）
        target_ratio: float = 0.5, # 目標比率（50%）
        min_notional_usdt: float = 5.0,  # 最小交易額度
        threshold_pct: float = 0.01,     # 偏差閾值（1%）
    ):
        self.balance_service = balance_service
        self.redis = redis_client
        self.target_ratio = target_ratio
        self.min_notional_usdt = min_notional_usdt
        self.threshold_pct = threshold_pct

    async def generate_plan(self, snapshot=None):
        """生成再平衡計劃"""
        # 1. 獲取餘額快照
        snapshot = snapshot or await self.balance_service.get_account_balance()
        
        # 2. 計算計劃（純函數，便於測試）
        plan = self.compute_plan(snapshot)
        
        # 3. 儲存計劃到 Redis
        await self._record_plan(plan)
        
        return plan
```

### 步驟 1：數據提取

```python
def compute_plan(self, snapshot):
    # 提取 QRL 數據
    qrl_data = snapshot.get("balances", {}).get("QRL", {})
    qrl_total = safe_float(qrl_data.get("total", 0))
    
    # 提取 USDT 數據
    usdt_data = snapshot.get("balances", {}).get("USDT", {})
    usdt_total = safe_float(usdt_data.get("total", 0))
    
    # 獲取價格（優先從 prices，fallback 到 QRL 數據）
    price_entry = snapshot.get("prices", {}).get("QRLUSDT")
    price = safe_float(price_entry or qrl_data.get("price"))
```

**數據來源：**
```json
{
  "balances": {
    "QRL": {
      "total": 100.0,      // QRL 總餘額
      "available": 95.0,   // 可用餘額（未鎖定）
      "locked": 5.0,       // 鎖定餘額（掛單中）
      "price": 2.5         // 備用價格
    },
    "USDT": {
      "total": 250.0,
      "available": 240.0,
      "locked": 10.0
    }
  },
  "prices": {
    "QRLUSDT": 2.5        // 主要價格來源
  }
}
```

### 步驟 2：價值計算

```python
# 計算總價值（以 USDT 計）
total_value = qrl_total * price + usdt_total

# 計算目標價值（50% 的總價值）
target_value = total_value * self.target_ratio  # 0.5 = 50%

# 計算當前 QRL 的價值
qrl_value = qrl_total * price

# 計算偏差（正值表示 QRL 過多，負值表示 QRL 不足）
delta = qrl_value - target_value

# 計算需要調整的金額
notional = abs(delta)  # 絕對值

# 計算需要交易的 QRL 數量
quantity = notional / price if price > 0 else 0
```

**數學範例：**
```
假設：
- qrl_total = 100 QRL
- usdt_total = 150 USDT
- price = 2 USDT/QRL

計算：
total_value = 100 * 2 + 150 = 350 USDT
target_value = 350 * 0.5 = 175 USDT
qrl_value = 100 * 2 = 200 USDT
delta = 200 - 175 = 25 USDT (QRL 過多)
notional = |25| = 25 USDT
quantity = 25 / 2 = 12.5 QRL

結論：需要賣出 12.5 QRL
```

### 步驟 3：構建基礎計劃

```python
plan = {
    "timestamp": datetime.now().isoformat(),
    "price": price,
    "qrl_balance": qrl_total,
    "usdt_balance": usdt_total,
    "qrl_value_usdt": qrl_value,
    "usdt_value_usdt": usdt_total,
    "total_value_usdt": total_value,
    "target_value_usdt": target_value,
    "target_ratio": self.target_ratio,
    "quantity": quantity,
    "notional_usdt": notional,
}
```

### 步驟 4：決策邏輯

#### 檢查點 1：價格或餘額無效

```python
if price <= 0 or total_value <= 0:
    plan.update({
        "action": "HOLD",
        "reason": "Insufficient price or balance"
    })
    return plan
```

**觸發條件：**
- 價格為 0 或負數（數據錯誤）
- 總價值為 0（沒有資產）

**示例：**
```
price = 0        → HOLD (無法計算)
total_value = 0  → HOLD (沒有資產可平衡)
```

#### 檢查點 2：偏差在閾值內

```python
if notional < self.min_notional_usdt:  # 默認 5 USDT
    plan.update({
        "action": "HOLD",
        "reason": "Within threshold"
    })
    return plan

if total_value > 0 and (notional / total_value) < self.threshold_pct:  # 默認 1%
    plan.update({
        "action": "HOLD",
        "reason": "Within threshold"
    })
    return plan
```

**兩個閾值：**

1. **絕對閾值**：`min_notional_usdt = 5 USDT`
   - 避免過小的交易（手續費可能超過收益）
   - 例：偏差只有 2 USDT → 不值得交易

2. **相對閾值**：`threshold_pct = 1%`
   - 避免微小波動頻繁交易
   - 例：總價值 1000 USDT，偏差 8 USDT (0.8%) → 在容忍範圍內

**示例：**
```
情況 1：小額偏差
- total_value = 1000 USDT
- notional = 3 USDT
- 3 < 5 → HOLD (絕對值太小)

情況 2：相對偏差小
- total_value = 1000 USDT
- notional = 8 USDT
- 8 / 1000 = 0.8% < 1% → HOLD (相對偏差小)

情況 3：需要行動
- total_value = 1000 USDT
- notional = 15 USDT
- 15 > 5 ✓
- 15 / 1000 = 1.5% > 1% ✓ → 進行交易
```

#### 檢查點 3：賣出 QRL

```python
if delta > 0:  # QRL 價值超過目標
    sell_qty = min(quantity, qrl_total)  # 不能賣超過持有量
    plan.update({
        "action": "SELL",
        "reason": "QRL above target",
        "quantity": sell_qty,
        "notional_usdt": sell_qty * price,
    })
    return plan
```

**邏輯：**
- `delta > 0` 表示 QRL 價值超過目標（比例過高）
- 需要賣出 QRL 換成 USDT
- **安全限制**：賣出數量不能超過實際持有量

**示例：**
```
計算需要賣出 50 QRL，但只持有 40 QRL
→ 實際賣出 min(50, 40) = 40 QRL
→ 盡力接近目標，但不會賣空
```

#### 檢查點 4：買入 QRL

```python
else:  # delta <= 0，QRL 價值低於目標
    buy_qty = min(quantity, usdt_total / price if price > 0 else 0)
    
    if buy_qty <= 0:
        plan.update({
            "action": "HOLD",
            "reason": "Insufficient USDT"
        })
        return plan
    
    plan.update({
        "action": "BUY",
        "reason": "QRL below target",
        "quantity": buy_qty,
        "notional_usdt": buy_qty * price,
    })
    return plan
```

**邏輯：**
- `delta <= 0` 表示 QRL 價值低於目標（比例過低）
- 需要用 USDT 買入 QRL
- **安全限制**：買入金額不能超過 USDT 餘額

**示例：**
```
計算需要買入 100 QRL (200 USDT)，但只有 150 USDT
→ 實際買入 min(100, 150/2) = min(100, 75) = 75 QRL
→ 用完所有 USDT，盡可能接近目標

如果 USDT 餘額為 0
→ buy_qty = 0 → HOLD ("Insufficient USDT")
```

### 步驟 5：儲存計劃

```python
async def _record_plan(self, plan):
    if not self.redis or not hasattr(self.redis, "set_rebalance_plan"):
        return  # Redis 不可用，跳過儲存
    
    try:
        await self.redis.set_rebalance_plan(plan)
    except Exception:
        # Best-effort：儲存失敗不影響計劃生成
        pass
```

**設計考量：**
- 儲存是「盡力而為」（best-effort）
- 即使 Redis 失敗，計劃仍然生成並返回
- 適合快速原型，生產環境可能需要更嚴格的錯誤處理

## 決策樹分析

```
開始
  │
  ├─ price <= 0 or total_value <= 0?
  │    YES → HOLD (Insufficient price or balance)
  │    NO ↓
  │
  ├─ notional < 5 USDT?
  │    YES → HOLD (Within threshold - 絕對值太小)
  │    NO ↓
  │
  ├─ notional/total < 1%?
  │    YES → HOLD (Within threshold - 相對偏差小)
  │    NO ↓
  │
  ├─ delta > 0? (QRL 過多)
  │    YES → SELL
  │    │     quantity = min(需要, qrl_balance)
  │    │     確保不賣空
  │    │
  │    NO ↓ (delta <= 0, QRL 不足)
  │
  └─ BUY
       quantity = min(需要, usdt_balance/price)
       │
       ├─ buy_qty <= 0?
       │    YES → HOLD (Insufficient USDT)
       │    NO → BUY (執行買入)
```

## 實際案例

### 案例 1：QRL 價格上漲，需要賣出

**初始狀態：**
```
QRL 餘額：100 QRL
USDT 餘額：100 USDT
價格：1 USDT/QRL
QRL 價值：100 USDT
總價值：200 USDT
比例：50% : 50% ✅ 平衡
```

**價格上漲至 2 USDT/QRL：**
```
QRL 餘額：100 QRL (不變)
USDT 餘額：100 USDT (不變)
價格：2 USDT/QRL
QRL 價值：200 USDT ⬆️
總價值：300 USDT
比例：66.7% : 33.3% ❌ 失衡

計算：
- target_value = 300 * 0.5 = 150 USDT
- delta = 200 - 150 = 50 USDT (QRL 過多)
- quantity = 50 / 2 = 25 QRL
- notional = 50 USDT > 5 USDT ✓
- 50/300 = 16.7% > 1% ✓

動作：SELL 25 QRL
```

**執行後：**
```
QRL 餘額：75 QRL
USDT 餘額：150 USDT (100 + 50)
價格：2 USDT/QRL
QRL 價值：150 USDT
總價值：300 USDT
比例：50% : 50% ✅ 恢復平衡

收益：鎖定 50 USDT 利潤！
```

### 案例 2：QRL 價格下跌，需要買入

**初始狀態：**
```
QRL 餘額：100 QRL
USDT 餘額：100 USDT
價格：1 USDT/QRL
總價值：200 USDT
比例：50% : 50% ✅
```

**價格下跌至 0.5 USDT/QRL：**
```
QRL 價值：50 USDT ⬇️
USDT 餘額：100 USDT
總價值：150 USDT
比例：33.3% : 66.7% ❌

計算：
- target_value = 150 * 0.5 = 75 USDT
- delta = 50 - 75 = -25 USDT (QRL 不足)
- quantity = 25 / 0.5 = 50 QRL
- buy_qty = min(50, 100/0.5) = min(50, 200) = 50 QRL

動作：BUY 50 QRL (花費 25 USDT)
```

**執行後：**
```
QRL 餘額：150 QRL (100 + 50)
USDT 餘額：75 USDT (100 - 25)
QRL 價值：75 USDT
總價值：150 USDT
比例：50% : 50% ✅

優勢：以低價買入更多 QRL，降低平均成本！
```

### 案例 3：資金不足，無法完全平衡

**初始狀態：**
```
QRL 餘額：10 QRL
USDT 餘額：10 USDT
價格：2 USDT/QRL
QRL 價值：20 USDT
總價值：30 USDT
比例：66.7% : 33.3% ❌
```

**計算：**
```
target_value = 30 * 0.5 = 15 USDT
delta = 20 - 15 = 5 USDT (QRL 過多)
quantity = 5 / 2 = 2.5 QRL
notional = 5 USDT (剛好等於閾值)
5/30 = 16.7% > 1% ✓

動作：SELL 2.5 QRL
```

**如果 USDT 不足的情況（買入）：**
```
QRL 餘額：5 QRL
USDT 餘額：5 USDT
價格：2 USDT/QRL
QRL 價值：10 USDT
總價值：15 USDT
比例：66.7% : 33.3%

target_value = 15 * 0.5 = 7.5 USDT
delta = 10 - 7.5 = 2.5 USDT
需要買入但...
計算需要：2.5 / 2 = 1.25 QRL
可用 USDT：5 USDT / 2 = 2.5 QRL ✓ 足夠

但如果只有 1 USDT：
buy_qty = min(1.25, 1/2) = min(1.25, 0.5) = 0.5 QRL
→ 只能部分平衡
```

### 案例 4：閾值保護，避免頻繁交易

**微小波動場景：**
```
QRL 餘額：100 QRL
USDT 餘額：202 USDT
價格：2 USDT/QRL
QRL 價值：200 USDT
總價值：402 USDT
比例：49.75% : 50.25%

計算：
target_value = 402 * 0.5 = 201 USDT
delta = 200 - 201 = -1 USDT
notional = 1 USDT
1 < 5 → HOLD ✅ (絕對值太小，避免交易)

即使 notional = 6 USDT：
6/402 = 1.49%，但...
6 > 5 ✓
1.49% > 1% ✓
→ 會觸發交易（剛好超過兩個閾值）

但如果 notional = 3 USDT：
3 < 5 → HOLD (絕對閾值優先)
```

## 參數調優

### target_ratio (目標比率)

**當前：** `0.5` (50%)

**可選值：**
- `0.3` - 保守（30% QRL, 70% USDT）適合熊市
- `0.5` - 中性（50% QRL, 50% USDT）平衡
- `0.7` - 激進（70% QRL, 30% USDT）適合牛市

**影響：**
```python
# 30/70 策略（保守）
target_ratio = 0.3
# 總價值 100 USDT
# → 目標 QRL 價值：30 USDT
# → 目標 USDT 持有：70 USDT
# 適合：預期價格下跌，保留更多穩定幣

# 70/30 策略（激進）
target_ratio = 0.7
# 總價值 100 USDT
# → 目標 QRL 價值：70 USDT
# → 目標 USDT 持有：30 USDT
# 適合：預期價格上漲，持有更多 QRL
```

### min_notional_usdt (最小交易額度)

**當前：** `5.0` USDT

**調優考量：**
```python
# 過小（如 1 USDT）
min_notional_usdt = 1.0
# 優點：更精確的平衡
# 缺點：頻繁交易，手續費累積

# 適中（推薦 5-10 USDT）
min_notional_usdt = 5.0
# 優點：平衡精確度和手續費
# 缺點：小賬戶可能無法交易

# 過大（如 50 USDT）
min_notional_usdt = 50.0
# 優點：減少交易次數
# 缺點：失衡容忍度高，可能偏離目標
```

**根據賬戶大小調整：**
```python
# 小賬戶（< 1000 USDT）
min_notional_usdt = 5.0  # 0.5% 最小交易

# 中型賬戶（1000-10000 USDT）
min_notional_usdt = 10.0  # 更合理的比例

# 大賬戶（> 10000 USDT）
min_notional_usdt = 50.0  # 減少交易摩擦
```

### threshold_pct (偏差閾值)

**當前：** `0.01` (1%)

**調優考量：**
```python
# 嚴格（0.5%）
threshold_pct = 0.005
# 總價值 1000 USDT
# 容忍偏差：5 USDT
# 適合：追求精確平衡，交易頻繁

# 寬鬆（2%）
threshold_pct = 0.02
# 總價值 1000 USDT
# 容忍偏差：20 USDT
# 適合：減少交易，容忍更大波動

# 超寬鬆（5%）
threshold_pct = 0.05
# 總價值 1000 USDT
# 容忍偏差：50 USDT
# 適合：長期持有，極少調整
```

**與手續費的權衡：**
```
假設手續費率：0.1% (MEXC 一般費率)

情況 1：threshold_pct = 0.5%
- 交易次數：頻繁（每天可能多次）
- 單次手續費：0.1%
- 累積成本：高

情況 2：threshold_pct = 2%
- 交易次數：適中（每週幾次）
- 單次手續費：0.1%
- 累積成本：中等 ✅ 推薦

情況 3：threshold_pct = 5%
- 交易次數：稀少（每月幾次）
- 單次手續費：0.1%
- 累積成本：低
- 但可能錯過再平衡機會
```

### 推薦配置矩陣

| 賬戶大小 | target_ratio | min_notional | threshold_pct | 說明 |
|---------|--------------|--------------|---------------|------|
| < 500   | 0.5          | 5            | 0.02          | 小賬戶，減少交易 |
| 500-2000| 0.5          | 5            | 0.015         | 中小，平衡頻率 |
| 2k-10k  | 0.5          | 10           | 0.01          | 中型，標準配置 |
| > 10k   | 0.5          | 20-50        | 0.01          | 大賬戶，降低摩擦 |

**動態策略（進階）：**
```python
# 根據市場波動調整閾值
if market_volatility < 0.01:  # 低波動
    threshold_pct = 0.005  # 更敏感
elif market_volatility > 0.05:  # 高波動
    threshold_pct = 0.03   # 更寬容

# 根據時間調整（避免頻繁交易）
if last_rebalance_time < 1_hour:
    threshold_pct *= 1.5  # 提高閾值，減少短期交易
```

## 風險考量

### 1. 滑點風險

**問題：**
```
計劃：SELL 100 QRL @ 2.0 USDT
實際成交：
- 50 QRL @ 2.0
- 30 QRL @ 1.98
- 20 QRL @ 1.95
平均價格：1.985 USDT (損失 0.75%)
```

**緩解措施：**
```python
# 添加滑點容忍度檢查
MAX_SLIPPAGE = 0.005  # 0.5%

def validate_execution_price(plan_price, actual_price):
    slippage = abs(actual_price - plan_price) / plan_price
    if slippage > MAX_SLIPPAGE:
        raise ExecutionError("Excessive slippage")
```

### 2. 市場深度不足

**問題：**
```
訂單簿深度：
BID: 2.0 (50 QRL)
BID: 1.98 (30 QRL)
BID: 1.95 (20 QRL)

計劃賣出 100 QRL 會吃穿多層深度
→ 平均成交價遠低於計劃價格
```

**緩解措施：**
```python
# 在執行前檢查市場深度
def check_market_depth(symbol, quantity, side):
    orderbook = get_orderbook(symbol)
    available = sum_depth(orderbook, side, levels=3)
    
    if quantity > available * 0.8:  # 不要吃掉超過 80% 的深度
        raise MarketDepthError("Insufficient liquidity")
```

### 3. 頻繁交易的手續費累積

**問題：**
```
交易次數：每天 10 次
手續費率：0.1%
月累積：~3%

假設資產 10000 USDT：
月手續費：300 USDT
年手續費：3600 USDT (36%)

即使策略本身盈利，手續費也可能吃掉大部分收益！
```

**緩解措施：**
```python
# 添加冷卻期
COOLDOWN_PERIOD = 3600  # 1 小時

def check_cooldown(last_trade_time):
    if time.now() - last_trade_time < COOLDOWN_PERIOD:
        return "HOLD", "In cooldown period"

# 提高閾值
threshold_pct = 0.02  # 2% 才觸發

# 累積偏差再交易
accumulated_deviation += current_deviation
if accumulated_deviation > threshold:
    execute_rebalance()
    accumulated_deviation = 0
```

### 4. 極端市場條件

**問題 A：快速崩盤**
```
初始：100 QRL @ 2 USDT + 100 USDT
價格暴跌：0.5 USDT → 買入信號
但價格繼續跌：0.2 USDT → 繼續買入
最終：0.05 USDT → 資金耗盡

結果：抄底失敗，深度套牢
```

**問題 B：閃崩/閃漲**
```
閃崩：2 USDT → 0.01 USDT（1 秒）→ 2 USDT
系統可能在 0.01 觸發大量買入
→ 滑點巨大，損失慘重
```

**緩解措施：**
```python
# 添加價格變化限制
MAX_PRICE_CHANGE = 0.2  # 20%

def validate_price_change(current_price, reference_price):
    change = abs(current_price - reference_price) / reference_price
    if change > MAX_PRICE_CHANGE:
        return "HOLD", "Abnormal price movement"

# 添加緊急熔斷
def circuit_breaker(price_history):
    if is_flash_crash(price_history):
        halt_trading(duration=3600)  # 暫停 1 小時
```

### 5. 部分成交風險

**問題：**
```
計劃：SELL 100 QRL
實際成交：45 QRL（部分成交）
→ 平衡未達成
→ 下次觸發可能重複賣出

如果沒有追蹤執行狀態：
- 重複計劃
- 重複下單
- 資金混亂
```

**緩解措施：**
```python
# 儲存執行狀態
class ExecutionTracker:
    def __init__(self):
        self.pending_orders = {}
    
    def track_order(self, plan_id, order_id, quantity):
        self.pending_orders[plan_id] = {
            "order_id": order_id,
            "planned": quantity,
            "filled": 0
        }
    
    def update_fill(self, plan_id, filled_quantity):
        self.pending_orders[plan_id]["filled"] += filled_quantity
    
    def is_complete(self, plan_id):
        order = self.pending_orders[plan_id]
        return order["filled"] >= order["planned"]
```

## 優化建議

### 1. 分層執行策略

**問題：** 大額訂單一次性執行風險高

**解決方案：** TWAP (Time-Weighted Average Price)
```python
def execute_large_order(quantity, duration_minutes=15):
    """將大訂單分散在時間段內執行"""
    chunks = quantity / (duration_minutes / 3)  # 每 3 分鐘執行一部分
    
    for chunk in range(int(duration_minutes / 3)):
        execute_chunk(chunks)
        wait(180)  # 等待 3 分鐘
```

### 2. 價格預測整合

**當前：** 只看當前價格

**優化：** 整合簡單移動平均
```python
def enhanced_decision(current_price, ma_7, ma_25):
    """結合移動平均線的決策"""
    delta = compute_delta(current_price)
    
    # 上升趨勢：延遲賣出（價格可能繼續漲）
    if current_price > ma_7 > ma_25 and delta > 0:
        threshold_pct *= 1.5  # 提高賣出閾值
    
    # 下降趨勢：延遲買入（價格可能繼續跌）
    if current_price < ma_7 < ma_25 and delta < 0:
        threshold_pct *= 1.5  # 提高買入閾值
    
    return make_decision(delta, threshold_pct)
```

### 3. 多級閾值系統

**當前：** 單一閾值

**優化：** 分級響應
```python
# 不同偏差程度的不同響應
THRESHOLDS = {
    "minor": 0.01,      # 1%  - 小額調整
    "moderate": 0.03,   # 3%  - 標準調整
    "major": 0.05,      # 5%  - 大額調整
    "critical": 0.10    # 10% - 緊急調整
}

def tiered_response(deviation_pct):
    if deviation_pct < THRESHOLDS["minor"]:
        return "HOLD"
    elif deviation_pct < THRESHOLDS["moderate"]:
        return "SMALL_REBALANCE", quantity * 0.5  # 只調整一半
    elif deviation_pct < THRESHOLDS["major"]:
        return "FULL_REBALANCE", quantity
    else:
        return "URGENT_REBALANCE", quantity, "high_priority"
```

### 4. 成本基礎追蹤

**當前：** 不考慮買入成本

**優化：** 避免虧損賣出
```python
def cost_aware_rebalance(current_price, avg_cost):
    """考慮成本基礎的再平衡"""
    plan = compute_plan(snapshot)
    
    if plan["action"] == "SELL":
        # 如果當前價格低於平均成本，考慮暫緩
        if current_price < avg_cost * 1.02:  # 低於成本 + 2% 緩衝
            return {
                "action": "HOLD",
                "reason": "Price below cost basis",
                "original_plan": plan
            }
    
    return plan
```

### 5. 回測系統

**目標：** 驗證參數效果

```python
def backtest_rebalance(historical_data, config):
    """回測再平衡策略"""
    portfolio = {"qrl": 100, "usdt": 100}
    trades = []
    
    for timestamp, price in historical_data:
        plan = compute_plan_with_config(portfolio, price, config)
        
        if plan["action"] in ["BUY", "SELL"]:
            # 模擬執行
            portfolio, trade_result = simulate_trade(portfolio, plan)
            trades.append(trade_result)
    
    # 計算績效
    final_value = portfolio["qrl"] * historical_data[-1]["price"] + portfolio["usdt"]
    initial_value = 200  # 初始 100 QRL @ 1 + 100 USDT
    
    return {
        "total_return": (final_value - initial_value) / initial_value,
        "num_trades": len(trades),
        "total_fees": sum(t["fee"] for t in trades),
        "sharpe_ratio": calculate_sharpe(trades)
    }

# 測試不同配置
results = {}
for threshold in [0.005, 0.01, 0.02, 0.05]:
    for min_notional in [5, 10, 20]:
        config = {"threshold_pct": threshold, "min_notional_usdt": min_notional}
        results[str(config)] = backtest_rebalance(data, config)

# 找出最佳配置
best_config = max(results.items(), key=lambda x: x[1]["total_return"])
```

## 總結

### 核心要點

1. **目標明確**：維持 50:50 價值比例
2. **邏輯簡單**：計算偏差 → 判斷閾值 → 執行動作
3. **風險控制**：多重檢查、安全限制
4. **參數可調**：適應不同賬戶和市場條件

### 適用場景

✅ **適合：**
- 長期持有兩種資產
- 相信資產長期價值
- 希望自動止盈/逢低買入
- 減少情緒化決策

❌ **不適合：**
- 單向看漲/看跌
- 極度波動的市場
- 流動性極差的交易對
- 超高頻交易需求

### 下一步行動

1. **驗證參數**：根據賬戶大小調整配置
2. **回測驗證**：使用歷史數據測試效果
3. **小額測試**：先用小額資金實盤驗證
4. **監控優化**：持續追蹤效果並調整參數

### 關鍵指標監控

```python
# 建議追蹤的指標
metrics = {
    "deviation_from_target": "當前偏差百分比",
    "rebalance_frequency": "再平衡頻率（次/天）",
    "avg_trade_size": "平均交易大小",
    "total_fees_paid": "累積手續費",
    "portfolio_return": "投資組合回報率",
    "vs_hold_strategy": "對比單純持有的表現"
}
```

這份文檔應該能幫助團隊充分理解再平衡邏輯，並為整合到 15-min-job 做好準備！
