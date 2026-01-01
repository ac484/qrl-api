# ADR-001: 整合 Rebalance 功能至 15-min-job

## 狀態
提議中 (Proposed)

## 日期
2026-01-01

## 背景 (Context)

目前系統有兩個獨立的 Cloud Scheduler 任務端點：

1. **15-min-job** (`/tasks/runtime`)
   - 目前：簡單的 keepalive 端點
   - 預期用途：每 15 分鐘更新成本和未實現損益
   - 位置：`src/app/interfaces/tasks/15-min-job.py`

2. **Rebalance** (`/tasks/rebalance/symmetric`)
   - 功能：執行對稱再平衡（50/50 QRL/USDT）
   - 包含完整的認證、Redis 連接、計劃生成
   - 位置：`src/app/interfaces/tasks/rebalance.py`

### 需求
需要實現：當 Cloud Scheduler 觸發 15-min-job 時，一併觸發 rebalance 功能。

## Rebalance 邏輯詳細說明

### 核心邏輯 (RebalanceService)

**目標**：維持投資組合價值的對稱分配（QRL 價值 50%，USDT 價值 50%）

#### 輸入參數
```python
def __init__(
    self,
    balance_service,      # 餘額服務
    redis_client=None,    # Redis 客戶端（儲存計劃）
    target_ratio: float = 0.5,          # 目標比率 (50%)
    min_notional_usdt: float = 5.0,     # 最小交易額度 (5 USDT)
    threshold_pct: float = 0.01,        # 偏差閾值 (1%)
)
```

#### 計算流程

**第一階段：數據獲取**
```python
# 從快照中提取數據
qrl_data = snapshot["balances"]["QRL"]
usdt_data = snapshot["balances"]["USDT"]
price = snapshot["prices"]["QRLUSDT"]  # QRL 當前價格

qrl_total = qrl_data["total"]   # QRL 總餘額
usdt_total = usdt_data["total"] # USDT 總餘額
```

**第二階段：價值計算**
```python
# 計算總價值（以 USDT 計）
total_value = qrl_total * price + usdt_total

# 計算目標價值（50% 的總價值）
target_value = total_value * 0.5

# 計算當前 QRL 的價值
qrl_value = qrl_total * price

# 計算偏差
delta = qrl_value - target_value

# 計算需要調整的名義金額和數量
notional = abs(delta)
quantity = notional / price  # 需要交易的 QRL 數量
```

**第三階段：決策邏輯**

```python
# 條件 1：價格或總價值無效
if price <= 0 or total_value <= 0:
    return {"action": "HOLD", "reason": "Insufficient price or balance"}

# 條件 2：偏差太小（小於最小交易額度或閾值百分比）
if notional < min_notional_usdt:
    return {"action": "HOLD", "reason": "Within threshold"}
    
if (notional / total_value) < threshold_pct:
    return {"action": "HOLD", "reason": "Within threshold"}

# 條件 3：QRL 價值過高 → 賣出 QRL
if delta > 0:
    sell_qty = min(quantity, qrl_total)  # 不能賣超過持有量
    return {
        "action": "SELL",
        "reason": "QRL above target",
        "quantity": sell_qty,
        "notional_usdt": sell_qty * price
    }

# 條件 4：QRL 價值過低 → 買入 QRL
if delta < 0:
    buy_qty = min(quantity, usdt_total / price)  # 不能買超過 USDT 額度
    if buy_qty <= 0:
        return {"action": "HOLD", "reason": "Insufficient USDT"}
    return {
        "action": "BUY",
        "reason": "QRL below target",
        "quantity": buy_qty,
        "notional_usdt": buy_qty * price
    }
```

#### 輸出結果

計劃物件包含：
```python
{
    "timestamp": "2026-01-01T12:00:00",
    "price": 2.5,                    # QRL 價格
    "qrl_balance": 100.0,            # QRL 餘額
    "usdt_balance": 150.0,           # USDT 餘額
    "qrl_value_usdt": 250.0,         # QRL 價值（USDT）
    "usdt_value_usdt": 150.0,        # USDT 價值
    "total_value_usdt": 400.0,       # 總價值
    "target_value_usdt": 200.0,      # 目標價值（50%）
    "target_ratio": 0.5,             # 目標比率
    "quantity": 20.0,                # 交易數量（QRL）
    "notional_usdt": 50.0,           # 名義金額（USDT）
    "action": "SELL",                # 操作：HOLD/BUY/SELL
    "reason": "QRL above target"     # 原因
}
```

### 實際案例分析

**案例 1：需要買入 QRL**
- 持有：10 QRL，80 USDT
- 價格：2 USDT/QRL
- QRL 價值：10 * 2 = 20 USDT
- USDT 價值：80 USDT
- 總價值：100 USDT
- 目標 QRL 價值：50 USDT
- 偏差：20 - 50 = -30 USDT（QRL 不足）
- **動作：BUY 15 QRL**（30 USDT / 2）

**案例 2：需要賣出 QRL**
- 持有：50 QRL，20 USDT
- 價格：2 USDT/QRL
- QRL 價值：50 * 2 = 100 USDT
- USDT 價值：20 USDT
- 總價值：120 USDT
- 目標 QRL 價值：60 USDT
- 偏差：100 - 60 = 40 USDT（QRL 過多）
- **動作：SELL 20 QRL**（40 USDT / 2）

**案例 3：保持不動**
- 持有：25 QRL，50 USDT
- 價格：2 USDT/QRL
- QRL 價值：50 USDT
- USDT 價值：50 USDT
- 總價值：100 USDT
- 目標 QRL 價值：50 USDT
- 偏差：0 USDT
- **動作：HOLD**（完美平衡）

## 決策

### 方案比較

#### 方案 A：HTTP 內部調用
```python
# 15-min-job.py 內部使用 httpx 調用 /tasks/rebalance/symmetric
async def runtime_keepalive():
    # 執行 15 分鐘任務邏輯
    await update_cost_and_pnl()
    
    # 調用 rebalance 端點
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8080/tasks/rebalance/symmetric",
            headers=headers
        )
    
    return {"success": True, "rebalance": response.json()}
```

**優點：**
- ✅ 完全重用現有的 rebalance.py 邏輯
- ✅ 保持端點獨立性
- ✅ 無需修改 RebalanceService

**缺點：**
- ❌ HTTP 調用開銷
- ❌ 需要處理內部請求的認證
- ❌ 錯誤處理更複雜
- ❌ 增加網路延遲

---

#### 方案 B：直接引入 RebalanceService
```python
# 15-min-job.py 直接使用服務
from src.app.application.trading.services.trading.rebalance_service import (
    RebalanceService,
)
from src.app.application.account.balance_service import BalanceService

async def runtime_keepalive():
    # 執行 15 分鐘任務邏輯
    await update_cost_and_pnl()
    
    # 直接調用 rebalance 服務
    balance_service = BalanceService(mexc_client, redis_client)
    rebalance_service = RebalanceService(balance_service, redis_client)
    plan = await rebalance_service.generate_plan()
    
    return {"success": True, "rebalance_plan": plan}
```

**優點：**
- ✅ 直接高效，無 HTTP 開銷
- ✅ 更好的錯誤處理
- ✅ 統一的 Redis 連接管理
- ✅ 更容易測試

**缺點：**
- ❌ 認證邏輯需要提取共用
- ❌ 增加 15-min-job 的複雜度
- ❌ 需要管理額外的依賴

---

#### 方案 C：共享模組化方法（推薦）
```python
# 新建 src/app/interfaces/tasks/shared/task_utils.py
async def require_scheduler_auth(headers):
    """共享的 Cloud Scheduler 認證邏輯"""
    pass

async def ensure_redis_connected(redis_client):
    """確保 Redis 已連接"""
    if not redis_client.connected:
        await redis_client.connect()

# 15-min-job.py
async def runtime_keepalive(
    x_cloudscheduler: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None),
):
    # 認證
    auth_method = await require_scheduler_auth(
        {"x_cloudscheduler": x_cloudscheduler, "authorization": authorization}
    )
    
    # 確保 Redis 連接
    await ensure_redis_connected(redis_client)
    
    try:
        # 1. 執行 15 分鐘任務（更新成本/損益）
        cost_result = await update_cost_and_pnl()
        
        # 2. 執行再平衡
        balance_service = BalanceService(mexc_client, redis_client)
        rebalance_service = RebalanceService(balance_service, redis_client)
        rebalance_plan = await rebalance_service.generate_plan()
        
        return {
            "status": "success",
            "task": "15-min-job",
            "auth": auth_method,
            "cost_update": cost_result,
            "rebalance": rebalance_plan,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
```

**優點：**
- ✅ 模組化、可重用的認證和連接邏輯
- ✅ 直接調用，無 HTTP 開銷
- ✅ 清晰的錯誤處理
- ✅ 保持端點職責清晰
- ✅ 易於測試和維護

**缺點：**
- ❌ 需要額外創建共享模組
- ❌ 稍微增加初期開發工作量

## 推薦方案：方案 C（共享模組化方法）

### 理由
1. **最佳實踐**：符合 DRY（Don't Repeat Yourself）原則
2. **效率**：避免 HTTP 調用開銷
3. **可維護性**：認證邏輯集中管理
4. **可測試性**：各部分可獨立測試
5. **擴展性**：未來其他任務也可使用共享模組

## 實施計劃

### 階段 1：創建共享模組
- [ ] 創建 `src/app/interfaces/tasks/shared/task_utils.py`
- [ ] 提取認證邏輯到 `require_scheduler_auth()`
- [ ] 提取 Redis 連接邏輯到 `ensure_redis_connected()`
- [ ] 添加單元測試

### 階段 2：更新 15-min-job
- [ ] 引入必要依賴（RebalanceService, BalanceService）
- [ ] 實現認證邏輯
- [ ] 添加成本/損益更新邏輯（如果還未實現）
- [ ] 整合 rebalance 調用
- [ ] 添加詳細日誌記錄

### 階段 3：重構 rebalance.py（可選）
- [ ] 使用共享的認證和連接邏輯
- [ ] 保持向後兼容性
- [ ] 更新測試

### 階段 4：測試
- [ ] 單元測試：15-min-job 的各個部分
- [ ] 整合測試：完整的 Cloud Scheduler 流程
- [ ] 認證測試：X-CloudScheduler 和 OIDC
- [ ] 錯誤處理測試

### 階段 5：文檔和部署
- [ ] 更新 `docs/04-Operations-and-Tasks.md`
- [ ] 添加新的監控指標
- [ ] 更新 Cloud Scheduler 配置文檔
- [ ] 部署到測試環境驗證

## 風險與緩解

### 風險 1：Redis 連接失敗
**緩解**：
- 添加重試邏輯
- 優雅降級（記錄錯誤但不中斷整個流程）
- 完整的錯誤日誌

### 風險 2：Rebalance 失敗影響整個任務
**緩解**：
- 使用 try-except 隔離 rebalance 邏輯
- 即使 rebalance 失敗，15-min 任務的其他部分仍可完成
- 記錄詳細的失敗原因

### 風險 3：執行時間超過 Cloud Scheduler 超時
**緩解**：
- 監控執行時間
- 設置合理的超時限制
- 考慮異步執行非關鍵部分

## 監控與日誌

### 新增指標
- `15min_job_execution_time` - 總執行時間
- `15min_job_rebalance_action` - 再平衡動作類型（HOLD/BUY/SELL）
- `15min_job_rebalance_notional` - 再平衡金額
- `15min_job_failures` - 失敗計數

### 日誌格式
```json
{
  "timestamp": "2026-01-01T12:00:00",
  "task": "15-min-job",
  "auth": "X-CloudScheduler",
  "cost_update": {"status": "success", "duration_ms": 120},
  "rebalance": {
    "action": "SELL",
    "quantity": 20.0,
    "notional_usdt": 40.0,
    "reason": "QRL above target"
  },
  "total_duration_ms": 500
}
```

## 參考文獻
- [Cloud Scheduler 文檔](https://cloud.google.com/scheduler/docs)
- [MEXC API v3 文檔](https://www.mexc.com/api-docs/spot-v3/introduction)
- 現有代碼：`rebalance.py`, `rebalance_service.py`

## 附錄：Cloud Scheduler 配置範例

```bash
# 創建或更新 15-min-job 的 Cloud Scheduler
gcloud scheduler jobs create http 15-min-job \
  --location=asia-southeast1 \
  --schedule="*/15 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/runtime" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://qrl-api-xxx.run.app"

# 可選：保留獨立的 rebalance job 作為備用
gcloud scheduler jobs create http rebalance-symmetric \
  --location=asia-southeast1 \
  --schedule="0 */4 * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/rebalance/symmetric" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://qrl-api-xxx.run.app"
```

## 決定
等待團隊審查和批准。

## 後果
- 15-min-job 將同時執行成本更新和再平衡
- 需要創建共享工具模組
- 提高代碼重用性和可維護性
- 需要更新監控和文檔
