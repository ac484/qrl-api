# Cloud Task Storage Fix Documentation

## Problem Statement

根據 issue #24，Google Cloud Scheduler 定時任務無法正確儲存數據，導致數據刷新失敗。

### 原始問題

1. **Task 端點只儲存部分數據**
   - `task_sync_balance` 只儲存 QRL 和 USDT 餘額
   - 沒有儲存鎖定金額、帳戶權限等完整信息
   - 沒有儲存原始 MEXC API 響應

2. **數據有 TTL 過期**
   - `set_latest_price()` 使用 `CACHE_TTL_PRICE` (30秒)
   - 導致價格數據自動過期，scheduled task 更新的數據很快就消失

3. **缺少原始 MEXC 響應儲存**
   - 無法追蹤 API 響應歷史
   - 無法調試數據問題
   - 無法進行數據分析

## Root Cause Analysis

### Redis 儲存方式分析

| Method | Storage Type | TTL | Status | Issue |
|--------|--------------|-----|--------|-------|
| `set_position()` | Hash (hset) | None | ✅ OK | 永久儲存 |
| `set_latest_price()` | String (set) | 30s | ❌ FAIL | 30秒後過期 |
| `set_cost_data()` | Hash (hset) | None | ✅ OK | 永久儲存 |
| Raw MEXC Response | N/A | N/A | ❌ MISSING | 不存在 |

### 問題影響

- **短期影響**: 定時任務執行後，數據在30秒內消失
- **長期影響**: 無法建立歷史數據記錄，無法進行趨勢分析
- **調試影響**: 無法追蹤 API 響應，難以定位問題

## Solution Design

### 雙存儲策略 (Dual-Storage Strategy)

我們實施了雙存儲策略，分別處理不同的使用場景：

#### 1. 永久存儲 (Permanent Storage)
- **用途**: 歷史追蹤、數據分析、scheduled task 儲存
- **TTL**: 無 (永久保存)
- **數據類型**: 
  - 原始 MEXC API 響應
  - 最新價格和倉位數據
  - 成本和損益數據

#### 2. 快取存儲 (Cached Storage)
- **用途**: 高頻 API 查詢、性能優化
- **TTL**: 30秒 (可配置)
- **數據類型**: 
  - 快取價格數據
  - 快取市場數據

## Implementation Changes

### 1. redis_client.py 新增方法

#### 原始 MEXC 響應儲存

```python
async def set_raw_mexc_response(endpoint: str, response_data: Dict, metadata: Optional[Dict] = None) -> bool
```
- 永久儲存原始 MEXC API 響應
- 自動添加時間戳
- 儲存到 `mexc:raw:{endpoint}:latest`
- 同時添加到歷史記錄 (sorted set)

```python
async def get_raw_mexc_response(endpoint: str) -> Optional[Dict]
```
- 獲取最新的原始響應

```python
async def get_raw_mexc_response_history(endpoint: str, start_time: Optional[int], end_time: Optional[int], limit: int = 100) -> List[Dict]
```
- 獲取歷史響應記錄
- 支持時間範圍查詢
- 自動保留最近 1000 條記錄

#### 價格儲存重構

```python
async def set_latest_price(price: float, volume: Optional[float] = None) -> bool
```
- **變更**: 移除 TTL，改為永久儲存
- 用於 scheduled task 和 bot 執行時的價格儲存

```python
async def set_cached_price(price: float, volume: Optional[float] = None) -> bool
```
- **新增**: 帶 TTL 的快取價格儲存
- 用於高頻 API 查詢

```python
async def get_cached_price() -> Optional[Dict]
```
- **新增**: 獲取快取價格
- 如果快取過期，自動回退到永久儲存的價格

### 2. cloud_tasks.py 端點更新

#### task_sync_balance (同步餘額)

**新增功能**:
1. 儲存原始 `account_info` 響應
2. 儲存所有非零餘額資產
3. 儲存鎖定金額 (locked)
4. 儲存帳戶權限 (canTrade, canWithdraw, canDeposit)
5. 增強日誌記錄

**儲存的數據**:
```python
{
    "qrl_balance": "1000.5",
    "usdt_balance": "500.25",
    "qrl_locked": "0.0",
    "usdt_locked": "10.0",
    "all_balances": '{"QRL": {...}, "USDT": {...}, ...}',
    "account_type": "SPOT",
    "can_trade": "True",
    "can_withdraw": "True",
    "can_deposit": "True",
    "update_time": "1703750000000",
    "updated_at": "2024-12-28T04:00:00"
}
```

#### task_update_price (更新價格)

**新增功能**:
1. 儲存原始 `ticker_24hr` 響應
2. 儲存完整 ticker 數據 (價格變化、高低價、交易量)
3. 同時更新永久和快取價格
4. 儲存到價格歷史記錄
5. 增強日誌記錄

**儲存的數據**:
- 永久價格: `bot:QRLUSDT:price:latest` (無 TTL)
- 快取價格: `bot:QRLUSDT:price:cached` (30秒 TTL)
- 原始響應: `mexc:raw:ticker_24hr:latest` (無 TTL)
- 歷史記錄: `bot:QRLUSDT:price:history` (sorted set)

#### task_update_cost (更新成本)

**新增功能**:
1. 儲存原始 `ticker_price` 響應
2. 計算額外指標 (ROI%, 總損益)
3. 增強日誌記錄
4. 改進錯誤處理

## Data Flow

### Before (有問題的流程)

```
Google Cloud Scheduler
  ↓
task_sync_balance / task_update_price
  ↓
set_position() / set_latest_price(TTL=30s)
  ↓
Redis (部分數據, 30秒後過期) ❌
```

### After (修復後的流程)

```
Google Cloud Scheduler
  ↓
task_sync_balance / task_update_price
  ↓
1. set_raw_mexc_response() → 永久儲存原始響應 ✅
2. set_position() → 永久儲存完整倉位數據 ✅
3. set_latest_price() → 永久儲存最新價格 ✅
4. set_cached_price() → 快取價格 (30s TTL) ✅
5. add_price_to_history() → 價格歷史 ✅
  ↓
Redis (完整數據, 永久保存) ✅
```

## Redis Key Structure

### 原始 MEXC 響應
```
mexc:raw:{endpoint}:latest          - 最新響應 (String, 無 TTL)
mexc:raw:{endpoint}:history         - 歷史響應 (Sorted Set, 最多 1000 條)
```

### 價格數據
```
bot:QRLUSDT:price:latest            - 最新價格 (String, 無 TTL) - NEW!
bot:QRLUSDT:price:cached            - 快取價格 (String, 30s TTL) - NEW!
bot:QRLUSDT:price:history           - 價格歷史 (Sorted Set, 無 TTL)
```

### 倉位數據
```
bot:QRLUSDT:position                - 倉位數據 (Hash, 無 TTL)
bot:QRLUSDT:cost                    - 成本數據 (Hash, 無 TTL)
```

## Testing

### 測試腳本

#### test_cloud_tasks_storage.py
- 測試原始 MEXC 響應儲存和檢索
- 測試永久 vs 快取價格儲存
- 測試完整倉位數據儲存
- 測試歷史記錄功能

#### validate_cloud_task_fixes.py
- 驗證 redis_client.py 新方法存在
- 驗證 cloud_tasks.py 正確調用新方法
- 驗證方法簽名正確
- 驗證移除了 TTL

### 運行測試

```bash
# 代碼結構驗證 (不需要 Redis)
python validate_cloud_task_fixes.py

# 功能測試 (需要 Redis)
python test_cloud_tasks_storage.py
```

## Deployment

### 部署步驟

1. **代碼審查**: 確認所有更改正確
2. **本地測試**: 運行驗證腳本
3. **部署到 Cloud Run**: 
   ```bash
   gcloud builds submit --config cloudbuild.yaml
   ```
4. **監控**: 
   - 檢查 Cloud Scheduler 執行日誌
   - 驗證 Redis 數據持久化
   - 確認數據不再過期

### 監控重點

1. **Cloud Scheduler 日誌**:
   - 檢查 `[Cloud Task] Stored raw` 日誌
   - 確認所有數據欄位都被儲存
   - 驗證詳細的指標日誌

2. **Redis 數據**:
   - 檢查 `mexc:raw:*:latest` keys
   - 檢查 `bot:QRLUSDT:price:latest` (應該無 TTL)
   - 檢查 `bot:QRLUSDT:position` 包含所有欄位

3. **API 響應**:
   - 測試 `/tasks/sync-balance` 返回完整數據
   - 測試 `/tasks/update-price` 返回完整 ticker 數據
   - 確認 `/status` 能獲取持久化的數據

## Backward Compatibility

### API 兼容性

✅ **完全向後兼容**

- `set_latest_price()` 方法簽名未變更
- `get_latest_price()` 方法簽名未變更
- 所有現有代碼無需修改
- 只是移除了 TTL，從30秒過期改為永久保存

### 使用這些方法的代碼

- `bot.py`: 使用 `set_latest_price()` - 無需修改 ✅
- `main.py`: 使用 `set_latest_price()` 和 `get_latest_price()` - 無需修改 ✅
- `cloud_tasks.py`: 已更新使用新方法 ✅

## Benefits

### 短期收益

1. **數據持久化**: 定時任務更新的數據不再過期
2. **完整數據**: 儲存所有帳戶信息和市場數據
3. **可調試性**: 可以查看原始 MEXC 響應

### 長期收益

1. **歷史分析**: 可以分析價格和帳戶變化趨勢
2. **問題追蹤**: 可以追溯歷史 API 響應定位問題
3. **數據完整性**: 確保所有重要數據都被保存

### 性能優化

1. **雙存儲策略**: 永久存儲 + 快取存儲
2. **快取回退**: 快取過期時自動回退到永久存儲
3. **減少 API 調用**: 快取減少對 MEXC API 的調用

## Conclusion

此修復解決了 Google Cloud Scheduler 定時任務數據無法持久化的根本問題：

1. ✅ 移除價格數據的 TTL，改為永久儲存
2. ✅ 新增原始 MEXC API 響應的永久儲存
3. ✅ 儲存完整的帳戶和市場數據
4. ✅ 實施雙存儲策略，兼顧持久化和性能
5. ✅ 增強日誌記錄，便於監控和調試
6. ✅ 保持向後兼容，無需修改現有代碼

現在，scheduled tasks 更新的數據會永久保存在 Redis 中，不會再出現數據消失的問題。
