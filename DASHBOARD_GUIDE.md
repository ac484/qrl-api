# Dashboard 使用指南

## 新功能

### 1. Web Dashboard (網頁儀表板)

訪問 `/dashboard` 可以查看視覺化的交易儀表板。

**功能特色**:
- 📊 實時顯示 QRL 和 USDT 餘額
- 💹 顯示 QRL/USDT 當前價格和 24h 變化
- 👥 支持子帳戶切換
- 🔄 自動每 30 秒刷新數據
- 📱 響應式設計，支持手機瀏覽

**訪問方式**:
```
http://localhost:8080/dashboard
```

### 2. 子帳戶支持

新增 API 端點支持查詢和管理子帳戶。

**API 端點**:
- `GET /account/sub-accounts` - 獲取子帳戶列表

**使用範例**:
```bash
curl http://localhost:8080/account/sub-accounts
```

**返回格式**:
```json
{
  "sub_accounts": [
    {
      "id": "sub-account-1",
      "email": "sub1@example.com"
    }
  ],
  "count": 1,
  "timestamp": "2024-12-27T12:00:00"
}
```

### 3. Redis 依賴更新

已移除 `aioredis` 依賴，因為它已被整合進 `redis-py` 5.0+。

**變更**:
- ❌ 移除: `aioredis==2.0.1`
- ✅ 保留: `redis==5.0.1` (已包含異步支持)

**使用方式保持不變**:
```python
import redis.asyncio as redis

# 創建異步 Redis 客戶端
client = redis.Redis(host='localhost', port=6379)
await client.ping()
```

## Dashboard 功能詳解

### 主要顯示區域

1. **帳戶選擇器**
   - 主帳戶 (Main Account)
   - 子帳戶下拉選單（動態載入）

2. **餘額卡片**
   - QRL 總餘額 + 可用/凍結明細
   - USDT 總餘額 + 可用/凍結明細
   - QRL/USDT 當前價格 + 24h 變化百分比

3. **價格趨勢**
   - 預留區域用於顯示價格歷史圖表

4. **詳細資訊**
   - 總資產價值 (USDT)
   - 平均成本
   - 未實現盈虧
   - 今日交易次數
   - 機器人狀態

### 自動刷新

Dashboard 會自動每 30 秒刷新一次數據，也可以手動點擊「重新整理」按鈕。

### 響應式設計

Dashboard 使用響應式設計，在不同螢幕尺寸下都能正常顯示：
- 桌面: 3 列網格佈局
- 平板: 2 列網格佈局  
- 手機: 1 列堆疊佈局

## 技術細節

### 前端技術
- 純 HTML + CSS + JavaScript
- 無需額外前端框架
- 使用 Fetch API 進行數據請求
- 實時數據更新

### 後端集成
- FastAPI Jinja2Templates 渲染
- 異步 API 端點
- MEXC API 整合
- Redis 狀態緩存

## 安全注意事項

⚠️ Dashboard 顯示敏感財務信息，建議：
1. 不要在公共網絡部署未經身份驗證的 Dashboard
2. 使用反向代理 (Nginx) 添加基本認證
3. 啟用 HTTPS
4. 限制訪問 IP 範圍

## 故障排除

### Dashboard 無法載入
1. 檢查 FastAPI 是否正常運行
2. 確認 `templates/dashboard.html` 文件存在
3. 查看瀏覽器控制台錯誤信息

### 子帳戶不顯示
1. 確認 MEXC API 密鑰有子帳戶查詢權限
2. 檢查 API 端點返回結果: `curl http://localhost:8080/account/sub-accounts`
3. MEXC 可能需要特殊權限才能訪問子帳戶 API

### 餘額顯示為 "--"
1. 確認已配置 MEXC_API_KEY 和 MEXC_SECRET_KEY
2. 檢查 API 密鑰權限
3. 查看後端日誌錯誤信息
