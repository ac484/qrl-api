# Implementation Complete: 15-min-job + Rebalance Integration

## 實施完成概要

根據 ADR-001 的推薦方案（共享模組化方法），已完成整合實施。

## 已實施的變更

### 1. 新建檔案

#### `src/app/interfaces/tasks/shared/` 模組
- **`task_utils.py`** - 共享工具函數
  - `require_scheduler_auth()` - 統一的 Cloud Scheduler 認證邏輯
  - `ensure_redis_connected()` - Redis 連接管理
  - 完整的錯誤處理和日誌記錄

- **`__init__.py`** - 模組導出介面

#### 測試檔案
- **`tests/test_shared_task_utils.py`** - 共享工具的單元測試
  - 認證邏輯測試（X-CloudScheduler 和 OIDC）
  - Redis 連接管理測試
  - 錯誤處理測試

### 2. 更新檔案

#### `src/app/interfaces/tasks/15-min-job.py`
**之前：** 簡單的 keepalive 端點
```python
@router.post("/runtime")
async def runtime_keepalive():
    return {"success": True, "message": "15-min-job"}
```

**現在：** 完整的整合端點
- ✅ Cloud Scheduler 認證（使用共享模組）
- ✅ Redis 連接管理（使用共享模組）
- ✅ 成本/損益更新（預留實施位置）
- ✅ 再平衡執行（調用 RebalanceService）
- ✅ 完整的錯誤處理和日誌
- ✅ 性能監控（執行時間追蹤）

**新端點：** `/tasks/15-min-job` (POST)

#### `src/app/interfaces/tasks/rebalance.py`
**更新：** 使用共享模組，簡化代碼
- ✅ 使用 `require_scheduler_auth()` 替代內聯邏輯
- ✅ 使用 `ensure_redis_connected()` 統一管理連接
- ✅ 改進的日誌記錄
- ✅ 保持向後兼容（端點路徑不變）

**保留端點：** `/tasks/rebalance/symmetric` (POST)

#### `src/app/interfaces/tasks/router.py`
**更新：** 整合新的 15-min-job 路由
- ✅ 動態導入 15-min-job 模組（處理檔名中的連字符）
- ✅ 註冊所有任務路由
- ✅ 優雅降級（導入失敗不中斷其他路由）

### 3. 移除檔案

#### `src/app/interfaces/tasks/runtime.py`
**原因：** 功能已整合到 15-min-job.py
- 舊的 `/tasks/runtime` 端點已被 `/tasks/15-min-job` 取代
- 消除冗餘代碼

## 架構改進

### 代碼重用
```
之前：
├── rebalance.py (包含認證邏輯)
└── runtime.py (簡單 keepalive)

現在：
├── shared/task_utils.py (共享認證和連接邏輯)
├── 15-min-job.py (使用共享模組 + 整合再平衡)
└── rebalance.py (使用共享模組，保持獨立端點)
```

### 呼叫流程

**15-min-job 執行流程：**
```
Cloud Scheduler (每 15 分鐘)
    │
    ▼
POST /tasks/15-min-job
    │
    ├─→ require_scheduler_auth() (共享模組)
    │       └─→ 驗證 X-CloudScheduler 或 OIDC
    │
    ├─→ ensure_redis_connected() (共享模組)
    │       └─→ 確保 Redis 已連接
    │
    ├─→ 成本/損益更新 (預留)
    │       └─→ 未來實施
    │
    └─→ RebalanceService.generate_plan()
            ├─→ BalanceService.get_account_balance()
            │       └─→ MEXC API
            ├─→ 計算再平衡計劃
            └─→ redis_client.set_rebalance_plan()
```

**rebalance 獨立執行流程：**
```
Cloud Scheduler (手動/定時)
    │
    ▼
POST /tasks/rebalance/symmetric
    │
    ├─→ require_scheduler_auth() (共享模組)
    ├─→ ensure_redis_connected() (共享模組)
    └─→ RebalanceService.generate_plan()
```

## 安全性考量

### ✅ 已實施的安全措施

1. **集中化認證**
   - 所有任務端點統一使用 `require_scheduler_auth()`
   - 防止未授權訪問
   - 支援 X-CloudScheduler 和 OIDC 雙重認證

2. **連接管理**
   - Redis 連接統一管理，防止洩漏
   - 連接失敗優雅處理（HTTP 503）
   - 完整的錯誤日誌追蹤

3. **錯誤處理**
   - 敏感資訊不會洩漏到錯誤訊息
   - 所有異常都有適當的 HTTP 狀態碼
   - 詳細日誌記錄便於排障

4. **直接調用**
   - 避免內部 HTTP 調用攻擊面
   - 減少網路層面的安全風險

### 🔒 安全優勢對比

| 項目 | 之前 | 現在 |
|-----|------|------|
| 認證邏輯 | 分散在各檔案 | 集中管理 |
| 連接管理 | 內聯重複代碼 | 統一處理 |
| 錯誤處理 | 不一致 | 標準化 |
| 日誌追蹤 | 部分缺失 | 完整覆蓋 |

## API 變更

### 新增端點

**`POST /tasks/15-min-job`**
- **用途：** 15 分鐘定時任務（成本更新 + 再平衡）
- **認證：** X-CloudScheduler 或 OIDC
- **回應：**
  ```json
  {
    "status": "success",
    "task": "15-min-job",
    "auth": "OIDC",
    "timestamp": "2026-01-01T13:00:00",
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
      ...
    }
  }
  ```

### 保留端點

**`POST /tasks/rebalance/symmetric`**
- **用途：** 獨立的再平衡端點（手動觸發/舊排程器）
- **認證：** X-CloudScheduler 或 OIDC
- **回應：** （與之前相同）

### 移除端點

**`POST /tasks/runtime`**
- **原因：** 已整合到 `/tasks/15-min-job`
- **遷移：** 更新 Cloud Scheduler 任務指向新端點

## Cloud Scheduler 配置

### 建議配置

**主要任務（推薦）：**
```bash
gcloud scheduler jobs create http 15-min-job \
  --location=asia-southeast1 \
  --schedule="*/15 * * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/15-min-job" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://qrl-api-xxx.run.app" \
  --attempt-deadline=300s
```

**獨立再平衡（可選，作為備用）：**
```bash
gcloud scheduler jobs create http rebalance-manual \
  --location=asia-southeast1 \
  --schedule="0 0 * * *" \
  --uri="https://qrl-api-xxx.run.app/tasks/rebalance/symmetric" \
  --http-method=POST \
  --oidc-service-account-email=scheduler@project.iam.gserviceaccount.com \
  --oidc-token-audience="https://qrl-api-xxx.run.app" \
  --paused
```

## 測試

### 單元測試

新增測試檔案：`tests/test_shared_task_utils.py`

**測試覆蓋：**
- ✅ Cloud Scheduler 認證（X-CloudScheduler）
- ✅ OIDC 認證
- ✅ 優先級（OIDC > X-CloudScheduler）
- ✅ 認證失敗處理
- ✅ Redis 連接管理
- ✅ Redis 連接失敗處理

### 整合測試建議

```python
# 測試 15-min-job 完整流程
async def test_15min_job_integration():
    response = await client.post(
        "/tasks/15-min-job",
        headers={"X-CloudScheduler": "true"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "rebalance" in data
    assert "cost_update" in data
```

## 後續工作

### 階段 2：成本/損益更新實施

在 `15-min-job.py` 的 Step 3 位置實施：

```python
# Step 3: Cost/PnL update
cost_service = CostService(redis_client)
cost_update_result = await cost_service.update_cost_and_pnl()
```

**需要：**
- 創建 CostService
- 實施成本計算邏輯
- 實施損益計算邏輯
- 更新 Redis 儲存

### 階段 3：監控和告警

**建議監控指標：**
- `15min_job_execution_time` - 執行時間
- `15min_job_success_rate` - 成功率
- `15min_job_rebalance_action` - 再平衡動作分布
- `shared_auth_failures` - 認證失敗次數

## 遷移指南

### 從舊端點遷移

1. **更新 Cloud Scheduler 任務**
   ```bash
   # 更新現有任務
   gcloud scheduler jobs update http OLD_JOB_NAME \
     --uri="https://qrl-api-xxx.run.app/tasks/15-min-job"
   
   # 或創建新任務並刪除舊任務
   ```

2. **驗證新端點**
   ```bash
   # 手動測試
   curl -X POST https://qrl-api-xxx.run.app/tasks/15-min-job \
     -H "X-CloudScheduler: true"
   ```

3. **監控日誌**
   ```bash
   # 檢查日誌確保正常運作
   gcloud logging read "resource.type=cloud_run_revision AND 15-min-job" --limit 50
   ```

## 總結

✅ **完成項目：**
- 創建共享工具模組（認證、連接管理）
- 完全重構 15-min-job 整合再平衡
- 更新 rebalance.py 使用共享模組
- 移除冗餘代碼（runtime.py）
- 添加單元測試
- 更新路由註冊

✅ **安全性：**
- 無新增安全風險
- 改進認證集中管理
- 優化連接管理
- 增強錯誤處理

✅ **不考慮向後兼容：**
- 移除 `/tasks/runtime` 端點
- 需要更新 Cloud Scheduler 配置
- 端點路徑變更為 `/tasks/15-min-job`

🚀 **下一步：**
- 實施成本/損益更新邏輯
- 配置監控和告警
- 部署到測試環境驗證
- 更新生產環境 Cloud Scheduler

---

**實施日期：** 2026-01-01  
**狀態：** ✅ 核心功能完成，等待部署  
**負責人：** @copilot  
**審查人：** @7Spade
