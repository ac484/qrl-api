# QRL Trading API

MEXC API 整合的 QRL/USDT 自動化交易機器人

## 技術架構

### 完全異步設計
- **Web 框架**: FastAPI + Uvicorn
- **HTTP 客戶端**: httpx (async)
- **Redis 客戶端**: redis.asyncio
- **WebSocket**: websockets (async)

### 核心特性
- ✅ MEXC API v3 完整整合
- ✅ 異步 REST API 調用
- ✅ Redis 狀態管理與智能快取
- ✅ 全面的 MEXC v3 API 數據快取（市場數據、帳戶數據、訂單數據）
- ✅ 可配置的快取 TTL（減少 API 調用、提升性能）
- ✅ 6 階段交易執行系統
- ✅ 移動平均線交叉策略
- ✅ 多層倉位管理
- ✅ 風險控制機制
- ✅ Docker 容器化支援

## 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 配置環境變數

```bash
cp .env.example .env
# 編輯 .env 文件，設置你的 MEXC API 密鑰
```

### 3. 啟動 Redis

**選項 1: 使用 Redis Cloud (推薦)**
```bash
# 在 .env 文件中設置 REDIS_URL
REDIS_URL=redis://default:your_password@your-redis-cloud.com:6379/0
```

詳細設定請參考 [REDIS_CLOUD_SETUP.md](REDIS_CLOUD_SETUP.md)

**選項 2: 本地 Redis**
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### 4. 運行應用

```bash
# 開發模式
uvicorn main:app --reload

# 生產模式
uvicorn main:app --host 0.0.0.0 --port 8080
```

### 5. 訪問 API 文檔

- Swagger UI: http://localhost:8080/docs
- ReDoc: http://localhost:8080/redoc

## API 端點

### 核心端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/` | GET | 服務信息 |
| `/health` | GET | 健康檢查 |
| `/status` | GET | 機器人狀態 |
| `/control` | POST | 控制機器人（start/pause/stop） |
| `/execute` | POST | 執行交易策略 |

### 市場數據端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/market/ticker/{symbol}` | GET | 獲取 24 小時行情（支援 Redis 快取） |
| `/market/price/{symbol}` | GET | 獲取當前價格（支援 Redis 快取） |
| `/market/orderbook/{symbol}` | GET | 獲取訂單簿深度（支援 Redis 快取） |
| `/market/trades/{symbol}` | GET | 獲取最近交易記錄（支援 Redis 快取） |
| `/market/klines/{symbol}` | GET | 獲取 K 線/蠟燭圖數據（支援 Redis 快取） |

### 帳戶端點

| 端點 | 方法 | 說明 |
|------|------|------|
| `/account/balance` | GET | 獲取帳戶餘額（支援 Redis 快取） |
| `/account/orders/open` | GET | 獲取未成交訂單（支援 Redis 快取） |
| `/account/orders/history` | GET | 獲取歷史訂單（支援 Redis 快取） |
| `/account/sub-accounts` | GET | 獲取子帳戶列表 |
| `/account/sub-account/balance` | GET | 獲取子帳戶餘額 |

## 使用範例

### 1. 檢查服務狀態

```bash
curl http://localhost:8080/health
```

### 2. 獲取機器人狀態

```bash
curl http://localhost:8080/status
```

### 3. 啟動機器人

```bash
curl -X POST http://localhost:8080/control \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'
```

### 4. 執行交易（Dry Run）

```bash
curl -X POST http://localhost:8080/execute \
  -H "Content-Type: application/json" \
  -d '{
    "pair": "QRL/USDT",
    "strategy": "ma-crossover",
    "dry_run": true
  }'
```

### 5. 獲取市場價格

```bash
curl http://localhost:8080/market/price/QRLUSDT
```

## Docker 部署

### 構建映像

```bash
docker build -t qrl-trading-api .
```

### 運行容器

```bash
docker run -d \
  -p 8080:8080 \
  -e REDIS_HOST=redis \
  -e MEXC_API_KEY=your_api_key \
  -e MEXC_SECRET_KEY=your_secret_key \
  --name qrl-trading-api \
  qrl-trading-api
```

### Docker Compose

```yaml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data

  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - REDIS_HOST=redis
      - MEXC_API_KEY=${MEXC_API_KEY}
      - MEXC_SECRET_KEY=${MEXC_SECRET_KEY}
    depends_on:
      - redis

volumes:
  redis-data:
```

## 交易策略

### 移動平均線交叉策略

**買入條件**:
- 短期 MA (7) 上穿長期 MA (25)
- 當前價格 <= 平均成本

**賣出條件**:
- 短期 MA (7) 下穿長期 MA (25)
- 當前價格 >= 平均成本 × 1.03 (3% 利潤)

### 倉位管理

- **核心倉位**: 70% (永不交易)
- **波段倉位**: 20% (週級別)
- **機動倉位**: 10% (日級別)

### 風險控制

- 每日最多交易 5 次
- 最小交易間隔 300 秒
- 單次交易不超過可用倉位的 30%
- 保留 20% USDT 儲備

## 開發指南

### 項目結構

```
qrl-api/
├── main.py              # FastAPI 主應用（異步）
├── bot.py               # 交易機器人邏輯（異步）
├── mexc_client.py       # MEXC API 客戶端（httpx）
├── redis_client.py      # Redis 客戶端（redis.asyncio）
├── config.py            # 配置管理
├── requirements.txt     # Python 依賴
├── Dockerfile           # Docker 配置
├── .env.example         # 環境變數範例
└── README.md            # 文檔
```

### 異步架構優勢

1. **高並發**: 處理多個 API 請求而不阻塞
2. **低延遲**: 非阻塞 I/O 操作
3. **資源效率**: 更好的內存和 CPU 利用率
4. **可擴展性**: 輕鬆處理更多並發連接

## MEXC API 參考

- [MEXC API 文檔](https://www.mexc.com/zh-MY/api-docs/spot-v3/introduction)
- [MEXC API SDK](https://github.com/mexcdevelop/mexc-api-sdk)
- [WebSocket 協議](https://github.com/mexcdevelop/websocket-proto)

## MEXC 數據持久化

所有從 MEXC API 獲取的數據都會**永久儲存在 Redis** 中，方便除錯和分析。查看 **[MEXC Redis 儲存指南](./docs/MEXC_REDIS_STORAGE.md)** 了解詳情：

- 📦 完整 API 響應儲存
- 💰 帳戶餘額數據
- 📈 QRL 價格數據
- 💵 總價值計算（USDT）
- 🔍 詳細日誌記錄
- 🛠️ 除錯工具和方法

**Redis 儲存的數據:**
- `mexc:raw_response:account_info` - 完整 MEXC API 響應
- `mexc:account_balance` - 處理後的餘額數據
- `mexc:qrl_price` - QRL 價格數據
- `mexc:total_value` - 總價值計算

**API 端點:**
- `GET /account/balance` - 獲取餘額並儲存到 Redis
- `GET /account/balance/redis` - 查看 Redis 中儲存的數據

## 疑難排解

遇到問題？查看我們的 **[疑難排解指南](./TROUBLESHOOTING.md)** 了解常見問題和解決方案：

- 🔴 餘額顯示錯誤或卡住
- 🔴 子帳戶無法載入
- 🔴 機器人無法交易
- 🔧 詳細除錯步驟
- 📋 部署前檢查清單

**常見問題快速連結:**
- [API 密鑰配置](./TROUBLESHOOTING.md#api-keys-not-configured-)
- [子帳戶權限](./TROUBLESHOOTING.md#not-a-broker-account-)
- [除錯步驟](./TROUBLESHOOTING.md#-debugging-steps)

## 安全注意事項

⚠️ **重要**:
- 永不將 API 密鑰提交到 Git
- 使用環境變數或 Secret Manager 管理密鑰
- 定期輪換 API 密鑰
- 設置 IP 白名單
- 限制 API 權限（只允許交易，禁止提幣）

## 授權

MIT License

## 支援

如有問題，請：
1. 查看 [疑難排解指南](./TROUBLESHOOTING.md)
2. 查看 [現有 Issues](https://github.com/7Spade/qrl-api/issues)
3. 提交新的 [GitHub Issue](https://github.com/7Spade/qrl-api/issues/new)

## Sub-Account Support

### MEXC v3 API Dual-Mode Sub-Account System

此專案支援 MEXC v3 API 的兩種子帳戶系統：

#### 1. **SPOT API** (一般用戶)
- 使用數字 `subAccountId` 識別子帳戶
- 支援主帳戶與子帳戶間的通用轉帳
- 支援不同帳戶類型：SPOT, MARGIN, ETF, CONTRACT
- 所有 MEXC 用戶可使用

#### 2. **BROKER API** (券商/機構用戶)
- 使用字串 `subAccount` 名稱識別子帳戶
- 需要特殊的 Broker API 權限
- 提供更全面的子帳戶管理功能
- 可查詢子帳戶餘額

### 配置

在 `.env` 文件中設置子帳戶模式：

```bash
# 選擇子帳戶模式 (SPOT 或 BROKER)
SUB_ACCOUNT_MODE=SPOT

# 如果你有 MEXC Broker 帳戶，設置為 true
IS_BROKER_ACCOUNT=false

# SPOT 模式：提供數字 ID
# SUB_ACCOUNT_ID=123456

# BROKER 模式：提供帳戶名稱
# SUB_ACCOUNT_NAME=trading_account_001
```

### API 端點

**獲取子帳戶列表**
```bash
GET /account/sub-accounts
```

**查詢子帳戶餘額** (僅 BROKER 模式)
```bash
GET /account/sub-account/balance?identifier=<sub_account_id_or_name>
```

**子帳戶間轉帳**
```bash
POST /account/sub-account/transfer
{
  "from_account": "源帳戶",
  "to_account": "目標帳戶",
  "asset": "USDT",
  "amount": "100",
  "from_type": "SPOT",  # SPOT 模式專用
  "to_type": "SPOT"     # SPOT 模式專用
}
```

**創建子帳戶 API Key**
```bash
POST /account/sub-account/api-key
{
  "sub_account_identifier": "子帳戶 ID 或名稱",
  "note": "API Key 說明",
  "permissions": "權限"
}
```

### 特性

✅ 自動模式檢測（SPOT/BROKER）  
✅ 統一的 API 接口  
✅ 完整的錯誤處理  
✅ 支援多種子帳戶操作  
✅ 向後兼容設計  
✅ 完整的測試覆蓋

### 注意事項

- **SPOT API**: 無法從主帳戶直接查詢子帳戶餘額，需使用子帳戶的 API Key
- **BROKER API**: 需要 MEXC Broker 帳戶權限
- 詳細的 API 文檔請參考 MEXC v3 官方文檔

