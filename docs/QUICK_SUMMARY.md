# 快速摘要：Cloud Task 數據儲存修復

## 🎯 問題
Google Cloud Scheduler 定時任務更新的數據會在 30 秒後消失

## ✅ 解決方案
實施雙存儲策略：永久存儲 + 快取存儲

## 📝 主要更改

### 1. 新增功能 (redis_client.py)

**原始 MEXC API 響應儲存**：
```python
await redis_client.set_raw_mexc_response(
    endpoint="account_info",
    response_data=mexc_response,
    metadata={"task": "sync-balance"}
)
```

**雙價格存儲**：
- `set_latest_price()` - 永久存儲（無 TTL）
- `set_cached_price()` - 快取存儲（30秒 TTL）

### 2. 增強 Cloud Tasks (cloud_tasks.py)

**task_sync_balance**：
- ✅ 儲存原始 MEXC 響應
- ✅ 儲存所有資產餘額（包括鎖定金額）
- ✅ 儲存帳戶權限
- ✅ 增強日誌記錄

**task_update_price**：
- ✅ 儲存原始 ticker 響應
- ✅ 儲存完整價格數據（漲跌、高低價、成交量）
- ✅ 同時更新永久和快取存儲
- ✅ 增強日誌記錄

**task_update_cost**：
- ✅ 計算更多指標（ROI%, 總損益）
- ✅ 增強日誌記錄

## 🔍 驗證

```bash
# 運行驗證腳本（不需要 Redis）
python validate_cloud_task_fixes.py
```

結果：✅ All validations passed!

## 📊 數據結構

### Before
```
bot:QRLUSDT:price:latest  (30秒 TTL) ❌ 會過期
```

### After
```
mexc:raw:account_info:latest     (永久) ✅ 原始響應
mexc:raw:ticker_24hr:latest      (永久) ✅ 原始響應
bot:QRLUSDT:price:latest         (永久) ✅ 不會過期
bot:QRLUSDT:price:cached         (30秒) ✅ 快取用
```

## 🚀 部署

```bash
# 部署到 Cloud Run
gcloud builds submit --config cloudbuild.yaml
```

## 📈 監控要點

1. **Cloud Scheduler 日誌**：
   - 查找 `[Cloud Task] Stored raw` 訊息
   - 確認詳細指標被記錄

2. **Redis 數據**：
   ```bash
   redis-cli keys "mexc:raw:*"
   redis-cli get "bot:QRLUSDT:price:latest"
   redis-cli ttl "bot:QRLUSDT:price:latest"  # 應該返回 -1 (無 TTL)
   ```

3. **API 測試**：
   ```bash
   curl https://your-cloud-run-url/tasks/sync-balance \
     -H "X-CloudScheduler: true"
   ```

## 🔧 向後兼容性

✅ **完全兼容** - 所有現有代碼無需修改
- `set_latest_price()` 和 `get_latest_price()` 方法簽名未變
- 只是移除了 TTL，數據現在會永久保存

## 📚 完整文檔

詳見 `CLOUD_TASK_STORAGE_FIX.md` 獲取完整技術文檔

## ✨ 效益

- ✅ 數據永久保存，不再過期
- ✅ 完整的 MEXC API 響應歷史
- ✅ 更詳細的日誌和指標
- ✅ 更好的調試能力
- ✅ 支持歷史數據分析
