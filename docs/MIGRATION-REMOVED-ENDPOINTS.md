# Migration Notice: Removed Redundant Endpoints

## 已移除的端點

根據「不考慮向後兼容，從根本實施並處理冗餘」的要求，以下端點已被移除：

### `/tasks/runtime` (POST)

**移除原因：**
- 功能過於簡單，僅返回固定訊息
- 已整合到新的 `/tasks/15-min-job` 端點
- 消除代碼重複

**遷移方案：**

更新 Cloud Scheduler 任務指向新端點：

```bash
# 舊配置
--uri="https://qrl-api-xxx.run.app/tasks/runtime"

# 新配置
--uri="https://qrl-api-xxx.run.app/tasks/15-min-job"
```

**功能對比：**

| 特性 | `/tasks/runtime` (舊) | `/tasks/15-min-job` (新) |
|-----|---------------------|----------------------|
| 認證 | ❌ 無 | ✅ Cloud Scheduler |
| Redis 連接 | ❌ 無 | ✅ 自動管理 |
| 成本更新 | ❌ 無 | ✅ 預留實施 |
| 再平衡 | ❌ 無 | ✅ 完整整合 |
| 錯誤處理 | ❌ 基本 | ✅ 完整 |
| 日誌記錄 | ❌ 無 | ✅ 詳細追蹤 |
| 性能監控 | ❌ 無 | ✅ 執行時間 |

**回應格式對比：**

```json
// 舊端點回應
{
  "success": true,
  "message": "15-min-job"
}

// 新端點回應
{
  "status": "success",
  "task": "15-min-job",
  "auth": "OIDC",
  "timestamp": "2026-01-01T13:00:00",
  "duration_ms": 234,
  "cost_update": { ... },
  "rebalance": { ... }
}
```

## 其他移除的檔案

### `src/app/interfaces/tasks/runtime.py`

**移除原因：**
- 僅包含簡單的 keepalive 函數
- 功能已完全整合到 `15-min-job.py`
- 消除冗餘代碼

**影響範圍：**
- 該檔案的路由已從 `router.py` 中移除
- 任何直接導入此模組的代碼需要更新

**遷移方案：**

如果有代碼直接使用此模組：

```python
# 舊導入（已失效）
from src.app.interfaces.tasks.runtime import runtime_keepalive

# 新導入
from src.app.interfaces.tasks import task_15_min_job
```

## 潛在影響分析

### Cloud Scheduler 任務

**需要更新的任務：**

1. 任何使用 `/tasks/runtime` 端點的排程任務
2. 任何手動腳本或自動化工具

**更新步驟：**

```bash
# 列出所有 Cloud Scheduler 任務
gcloud scheduler jobs list --location=asia-southeast1

# 檢查任務詳情
gcloud scheduler jobs describe JOB_NAME --location=asia-southeast1

# 更新任務 URI
gcloud scheduler jobs update http JOB_NAME \
  --location=asia-southeast1 \
  --uri="https://qrl-api-xxx.run.app/tasks/15-min-job"
```

### 監控和告警

**需要更新的項目：**

1. **日誌查詢**
   ```bash
   # 舊查詢
   gcloud logging read "textPayload:\"runtime\""
   
   # 新查詢
   gcloud logging read "textPayload:\"15-min-job\""
   ```

2. **告警規則**
   - 更新任何基於 `/tasks/runtime` 的告警
   - 更新錯誤監控過濾器

3. **儀表板**
   - 更新 Grafana/Cloud Monitoring 儀表板
   - 更新指標查詢

### API 文檔

**需要更新的文檔：**

1. OpenAPI/Swagger 規範
2. README.md 中的 API 端點列表
3. 使用者指南
4. 操作手冊

## 驗證清單

部署後請驗證：

- [ ] Cloud Scheduler 任務已更新
- [ ] 新端點正常回應
- [ ] 認證機制正常工作
- [ ] 再平衡邏輯正常執行
- [ ] 日誌正確記錄
- [ ] 監控指標正常收集
- [ ] 告警規則正常觸發
- [ ] 文檔已更新

## 支援

如果在遷移過程中遇到問題：

1. 查看 `docs/IMPLEMENTATION-COMPLETE.md` 完整文檔
2. 檢查日誌：`gcloud logging read "textPayload:\"15-min-job\""`
3. 手動測試新端點：
   ```bash
   curl -X POST https://qrl-api-xxx.run.app/tasks/15-min-job \
     -H "X-CloudScheduler: true"
   ```

## 回滾方案

如果需要緊急回滾：

```bash
# 回滾到之前的提交
git checkout 176302d  # 實施前的最後一個提交

# 或使用 Git revert
git revert 19affd6  # 實施提交的哈希

# 重新部署
gcloud run deploy qrl-api --source .
```

---

**移除日期：** 2026-01-01  
**影響評估：** 低（僅需更新 Cloud Scheduler 配置）  
**遷移截止：** 建議 7 天內完成  
**文檔更新：** ✅ 完成
