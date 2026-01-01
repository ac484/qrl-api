# Tasks Endpoints Reference

完整的 `/tasks` 端點參考指南，包含所有 Cloud Scheduler 任務接口。

---

## 📋 端點總覽

| 端點 | 方法 | 用途 | 認證 | 狀態 |
|-----|------|------|------|------|
| `/tasks/15-min-job` | POST | 成本/損益更新 + 再平衡整合 | Cloud Scheduler | ✅ 主要 |
| `/tasks/rebalance/symmetric` | POST | 獨立的對稱再平衡計劃 | Cloud Scheduler | ✅ 活躍 |
| `/tasks/01-min-job` | POST | 帳戶餘額同步（MEXC） | Cloud Scheduler | ✅ 活躍 |
| `/tasks/05-min-job` | POST | 市場價格同步（MEXC） | Cloud Scheduler | ✅ 活躍 |
| `/tasks/sync-trades` | POST | 交易成本更新（MEXC） | Cloud Scheduler | ✅ 活躍 |

**路徑衝突已解決：** MEXC 交易成本同步端點已重命名為 `/tasks/sync-trades`

---

## 🎯 主要整合端點

### POST `/tasks/15-min-job`

**新的整合端點**（本次任務實施）

#### 功能
15 分鐘定時任務，執行：
1. **成本/損益更新**（預留實施）
2. **對稱再平衡計劃生成**（50/50 價值比例）

#### 認證
```http
X-CloudScheduler: true
```
或
```http
Authorization: Bearer <OIDC_TOKEN>
```

#### 請求範例
```bash
curl -X POST https://qrl-api-xxx.run.app/tasks/15-min-job \
  -H "X-CloudScheduler: true"
```

#### 回應範例
```json
{
  "status": "success",
  "task": "15-min-job",
  "auth": "OIDC",
  "timestamp": "2026-01-01T13:00:00.000Z",
  "duration_ms": 234,
  "cost_update": {
    "status": "not_implemented",
    "message": "Cost/PnL update pending implementation"
  },
  "rebalance": {
    "action": "SELL",
    "quantity": 12.5,
    "notional_usdt": 25.0,
    "reason": "QRL above target",
    "timestamp": "2026-01-01T13:00:00.000Z",
    "price": 2.0,
    "qrl_balance": 100.0,
    "usdt_balance": 100.0,
    "target_ratio": 0.5,
    "current_ratio": 0.57,
    "threshold_pct": 0.01
  }
}
```

#### 執行流程
```
1. 認證（X-CloudScheduler 或 OIDC）
   ↓
2. 確保 Redis 連接
   ↓
3. 成本/損益更新（預留）
   ↓
4. 生成再平衡計劃
   ↓
5. 儲存到 Redis
   ↓
6. 返回結果
```

#### 實施檔案
- **路由定義：** `src/app/interfaces/tasks/15-min-job.py`
- **共享工具：** `src/app/interfaces/tasks/shared/task_utils.py`
- **再平衡服務：** `src/app/application/trading/services/trading/rebalance_service.py`

#### Cloud Scheduler 配置
```bash
gcloud scheduler jobs create http 15-min-job \
  --location=asia-southeast1 \
  --schedule="*/15 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/15-min-job" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://qrl-api-xxx.run.app" \
  --attempt-deadline=60s
```

---

## 🔄 再平衡端點

### POST `/tasks/rebalance/symmetric`

**獨立的再平衡端點**（可單獨使用或手動觸發）

#### 功能
生成對稱（50/50 價值）再平衡計劃，維持 QRL 和 USDT 的價值比例。

#### 認證
```http
X-CloudScheduler: true
```
或
```http
Authorization: Bearer <OIDC_TOKEN>
```

#### 請求範例
```bash
curl -X POST https://qrl-api-xxx.run.app/tasks/rebalance/symmetric \
  -H "X-CloudScheduler: true"
```

#### 回應範例
```json
{
  "status": "success",
  "task": "rebalance-symmetric",
  "auth": "X-CloudScheduler",
  "plan": {
    "action": "BUY",
    "quantity": 5.0,
    "notional_usdt": 10.0,
    "reason": "QRL below target",
    "timestamp": "2026-01-01T14:00:00.000Z",
    "price": 2.0,
    "qrl_balance": 45.0,
    "usdt_balance": 110.0,
    "target_ratio": 0.5,
    "current_ratio": 0.45,
    "threshold_pct": 0.01
  }
}
```

#### 再平衡邏輯

**目標：** 維持 QRL 和 USDT 的**價值**比例為 50:50

**核心算法：**
```python
total_value = qrl_balance × price + usdt_balance
target_value = total_value × 0.5
delta = (qrl_balance × price) - target_value

if abs(delta) < min_notional or abs(delta)/total_value < threshold:
    return "HOLD"
elif delta > 0:
    return "SELL", quantity  # QRL 價值過高
else:
    return "BUY", quantity   # QRL 價值過低
```

**決策閾值：**
- `min_notional`: 5 USDT（最小交易金額）
- `threshold_pct`: 1%（最小偏差百分比）

**真實案例：**

```
場景 1：價格上漲，需要賣出 QRL（止盈）
═════════════════════════════════════════
初始狀態：
  QRL: 100 @ 1.0 USDT = 100 USDT
  USDT: 100 USDT
  總價值: 200 USDT
  比例: 50:50 ✅

價格上漲：
  QRL: 100 @ 2.0 USDT = 200 USDT
  USDT: 100 USDT
  總價值: 300 USDT
  比例: 67:33 ❌（QRL 過多）

再平衡計劃：
  動作: SELL
  數量: 25 QRL
  金額: 50 USDT

執行後：
  QRL: 75 @ 2.0 USDT = 150 USDT
  USDT: 150 USDT
  總價值: 300 USDT
  比例: 50:50 ✅
  收益: 鎖定 50 USDT 利潤


場景 2：價格下跌，需要買入 QRL（逢低買入）
═════════════════════════════════════════
初始狀態：
  QRL: 100 @ 1.0 USDT = 100 USDT
  USDT: 100 USDT
  總價值: 200 USDT
  比例: 50:50 ✅

價格下跌：
  QRL: 100 @ 0.5 USDT = 50 USDT
  USDT: 100 USDT
  總價值: 150 USDT
  比例: 33:67 ❌（USDT 過多）

再平衡計劃：
  動作: BUY
  數量: 50 QRL
  金額: 25 USDT

執行後：
  QRL: 150 @ 0.5 USDT = 75 USDT
  USDT: 75 USDT
  總價值: 150 USDT
  比例: 50:50 ✅
  策略: 低價增持 QRL


場景 3：偏差過小，不需要交易（HOLD）
═════════════════════════════════════════
當前狀態：
  QRL: 100 @ 1.02 USDT = 102 USDT
  USDT: 100 USDT
  總價值: 202 USDT
  比例: 50.5:49.5（偏差 < 1%）

再平衡計劃：
  動作: HOLD
  原因: 偏差過小（< 1% 閾值）
  節省: 避免不必要的交易費用
```

#### 實施檔案
- **路由定義：** `src/app/interfaces/tasks/rebalance.py`
- **再平衡服務：** `src/app/application/trading/services/trading/rebalance_service.py`
- **餘額服務：** `src/app/application/account/balance_service.py`

#### 用途

1. **作為獨立任務** - 可單獨配置 Cloud Scheduler
2. **手動觸發** - 測試或緊急再平衡
3. **備用端點** - 如果 15-min-job 失效

---

## 📊 MEXC 同步端點

### POST `/tasks/01-min-job`

**帳戶餘額同步**

#### 功能
從 MEXC 交易所同步帳戶餘額到 Redis 快取。

#### 認證
Cloud Scheduler 或內部調用

#### 實施檔案
- **路由定義：** `src/app/interfaces/tasks/mexc/sync_account.py`
- **業務邏輯：** `src/app/application/account/sync_balance.py`

#### Cloud Scheduler 配置
```bash
gcloud scheduler jobs create http sync-account-balance \
  --location=asia-southeast1 \
  --schedule="* * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/01-min-job" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com
```

---

### POST `/tasks/05-min-job`

**市場價格同步**

#### 功能
從 MEXC 交易所同步 QRL/USDT 價格到 Redis 快取。

#### 認證
Cloud Scheduler 或內部調用

#### 實施檔案
- **路由定義：** `src/app/interfaces/tasks/mexc/sync_market.py`
- **業務邏輯：** `src/app/application/market/sync_price.py`

#### Cloud Scheduler 配置
```bash
gcloud scheduler jobs create http sync-market-price \
  --location=asia-southeast1 \
  --schedule="*/5 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/05-min-job" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com
```

---

### POST `/tasks/sync-trades` (MEXC Sync)

**✅ 路徑已更新：從 `/tasks/15-min-job` 重命名為 `/tasks/sync-trades`**

#### 功能
更新交易成本資料（MEXC 同步）

#### 實施檔案
- **路由定義：** `src/app/interfaces/tasks/mexc/sync_trades.py`
- **處理函數：** `src/app/application/market/sync_cost.py` 中的 `task_update_cost`

#### Cloud Scheduler 配置

如果您已配置此端點的 Cloud Scheduler 任務，請更新 URI：

```bash
# 更新現有 Scheduler 任務
gcloud scheduler jobs update http trades-sync-job \
  --location=asia-southeast1 \
  --uri="https://qrl-api-xxx.run.app/tasks/sync-trades"
```

或創建新任務：

```bash
gcloud scheduler jobs create http trades-sync-job \
  --location=asia-southeast1 \
  --schedule="*/15 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/sync-trades" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com
```
router = APIRouter(prefix="/tasks/mexc", tags=["MEXC Sync"])
router.add_api_route("/trades", task_update_cost, methods=["POST"])
# 結果路徑: /tasks/mexc/trades
```

#### 實施檔案
- **路由定義：** `src/app/interfaces/tasks/mexc/sync_trades.py`
- **業務邏輯：** `src/app/application/market/sync_cost.py`

---

## 🔐 認證機制

所有 `/tasks` 端點使用統一的 Cloud Scheduler 認證：

### 認證方式

**方式 1：X-CloudScheduler 標頭**
```http
POST /tasks/15-min-job
X-CloudScheduler: true
```

**方式 2：OIDC 令牌（推薦）**
```http
POST /tasks/15-min-job
Authorization: Bearer <OIDC_TOKEN>
```

### 認證優先級
1. **OIDC Authorization** - 優先使用（更安全）
2. **X-CloudScheduler** - 備用方案

### 共享認證邏輯
所有端點使用 `require_scheduler_auth()` 函數：

```python
from src.app.interfaces.tasks.shared import require_scheduler_auth

auth_method = require_scheduler_auth(x_cloudscheduler, authorization)
# 返回: "OIDC" 或 "X-CloudScheduler"
```

**實施檔案：** `src/app/interfaces/tasks/shared/task_utils.py`

---

## 🏗️ 架構概覽

### 路由器結構

```
src/app/interfaces/tasks/
├── router.py                  # 主路由聚合器
├── 15-min-job.py              # 主要整合端點
├── rebalance.py               # 獨立再平衡端點
├── shared/                    # 共享工具
│   ├── __init__.py
│   └── task_utils.py          # 認證、Redis 連接
└── mexc/                      # MEXC 同步端點
    ├── sync_account.py        # 01-min-job
    ├── sync_market.py         # 05-min-job
    └── sync_trades.py         # 15-min-job (衝突!)
```

### 共享工具模組

**`src/app/interfaces/tasks/shared/task_utils.py`**

提供兩個核心函數：

#### 1. require_scheduler_auth()
```python
def require_scheduler_auth(
    x_cloudscheduler: Optional[str],
    authorization: Optional[str]
) -> str:
    """
    驗證 Cloud Scheduler 認證。
    
    Returns:
        str: "OIDC" 或 "X-CloudScheduler"
    
    Raises:
        HTTPException(401): 認證失敗
    """
```

#### 2. ensure_redis_connected()
```python
async def ensure_redis_connected(redis_client) -> None:
    """
    確保 Redis 已連接，失敗時嘗試重新連接。
    
    Raises:
        HTTPException(500): 連接失敗
    """
```

---

## 📈 使用建議

### 推薦配置

**主要定時任務：**
```bash
# 每 15 分鐘：成本更新 + 再平衡
gcloud scheduler jobs create http main-15-min-job \
  --schedule="*/15 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/15-min-job"

# 每分鐘：帳戶餘額同步
gcloud scheduler jobs create http sync-account \
  --schedule="* * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/01-min-job"

# 每 5 分鐘：市場價格同步
gcloud scheduler jobs create http sync-market \
  --schedule="*/5 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/05-min-job"
```

**備用任務（手動觸發）：**
```bash
# 獨立再平衡（暫停，僅手動觸發）
gcloud scheduler jobs create http rebalance-manual \
  --schedule="0 0 * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/rebalance/symmetric" \
  --paused
```

### 成本優化

設置 Cloud Run 為零實例擴展：
```bash
gcloud run services update qrl-api \
  --min-instances=0 \
  --max-instances=5 \
  --memory=512Mi
```

**效益：**
- 僅在任務執行時計費
- 年度節省 ~$1,134 USD（99.5%）
- 詳見：`docs/CLOUD-RUN-COST-OPTIMIZATION.md`

---

## 🔧 故障排查

### 常見問題

**Q: 端點返回 401 Unauthorized**
- 檢查 Cloud Scheduler 是否配置了 OIDC 認證
- 驗證服務帳戶權限
- 檢查 `X-CloudScheduler` 標頭是否正確

**Q: 端點返回 500 Internal Server Error**
- 檢查 Redis 連接狀態
- 查看 Cloud Run 日誌
- 驗證 MEXC API 金鑰配置

**Q: 再平衡計劃總是返回 HOLD**
- 檢查市場價格是否正確同步
- 驗證帳戶餘額數據
- 確認閾值設置（`min_notional`, `threshold_pct`）

**Q: 訂單載入失敗**
- 檢查 MEXC API 金鑰是否正確配置
- 驗證帳戶權限（需要交易權限）
- 查看瀏覽器控制台錯誤日誌
- 確認 `/account/orders` 端點運作正常

### 查看日誌

```bash
# Cloud Run 日誌
gcloud logging read \
  "resource.type=cloud_run_revision AND textPayload:\"15-min-job\"" \
  --limit 50 \
  --format json

# Cloud Scheduler 日誌
gcloud logging read \
  "resource.type=cloud_scheduler_job" \
  --limit 50
```

---

## 📚 相關文檔

### 架構決策記錄（ADR）
- `docs/ADR-001-README.md` - ADR 索引
- `docs/ADR-001-Quick-Reference.md` - 快速參考
- `docs/ADR-001-Rebalance-Integration-15min-Job.md` - 整合 ADR
- `docs/ADR-001-Architecture-Diagrams.md` - 架構圖
- `docs/ADR-001-Rebalance-Logic-Deep-Dive.md` - 再平衡邏輯深度解析

### 實施文檔
- `docs/IMPLEMENTATION-COMPLETE.md` - 實施完成指南
- `docs/MIGRATION-REMOVED-ENDPOINTS.md` - 遷移指南
- `docs/CLOUD-RUN-COST-OPTIMIZATION.md` - 成本優化指南

### 測試
- `tests/test_shared_task_utils.py` - 共享工具單元測試

---

## ⚠️ 待解決問題

### 1. 成本更新實施

**狀態：** 在 15-min-job 端點中為預留位置
```python
cost_update_result = {
    "status": "not_implemented",
    "message": "Cost/PnL update pending implementation"
}
```

**待辦：** 實施 CostService 和損益計算邏輯

---

**最後更新：** 2026-01-01  
**文檔版本：** 1.0  
**維護者：** QRL API 開發團隊
