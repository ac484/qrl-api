# Redis Cloud 設定指南

## 使用 REDIS_URL 連接 Redis Cloud

本專案已支持使用 `REDIS_URL` 環境變數來連接 Redis Cloud 或其他 Redis 服務。

### 設定方式

#### 方法 1: 使用 REDIS_URL (推薦)

適用於 Redis Cloud、Upstash、或任何提供連接 URL 的 Redis 服務。

**環境變數**:
```bash
REDIS_URL=redis://default:your_password@your-redis-host.com:6379/0
```

**Redis Cloud URL 格式**:
```
redis://default:<password>@<endpoint>:<port>/<database>
```

**範例** (Redis Cloud):
```bash
REDIS_URL=redis://default:abc123xyz@redis-12345.c1.us-east-1-2.ec2.cloud.redislabs.com:12345/0
```

**範例** (Upstash Redis):
```bash
REDIS_URL=rediss://default:xyz789@us1-relaxed-mallard-12345.upstash.io:6379
```

#### 方法 2: 使用個別參數 (備用)

如果不使用 REDIS_URL，系統會自動使用個別參數：

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_password
REDIS_DB=0
```

### 配置優先級

1. 如果設置了 `REDIS_URL`，系統會使用它
2. 如果沒有 `REDIS_URL`，則使用 `REDIS_HOST`, `REDIS_PORT` 等個別參數

### 驗證連接

啟動應用後，檢查日誌：

```bash
# 使用 REDIS_URL 時
INFO - Connected to Redis using REDIS_URL

# 使用個別參數時
INFO - Connected to Redis at localhost:6379
```

### 測試連接

使用健康檢查端點：

```bash
curl http://localhost:8080/health
```

**成功響應**:
```json
{
  "status": "healthy",
  "redis_connected": true,
  "mexc_api_available": true,
  "timestamp": "2024-12-27T12:00:00"
}
```

### 常見問題

#### Q: Redis Cloud 需要 SSL/TLS 嗎？
A: 是的，使用 `rediss://` (注意雙 s) 而不是 `redis://`

```bash
REDIS_URL=rediss://default:password@host:port/0
```

#### Q: 如何獲取 Redis Cloud 連接 URL？
A: 
1. 登入 Redis Cloud 控制台
2. 選擇您的資料庫
3. 在 "General" 或 "Configuration" 頁面找到 "Public endpoint"
4. 複製連接字串，格式為: `redis://default:<password>@<endpoint>:<port>`

#### Q: 密碼中有特殊字符怎麼辦？
A: 需要進行 URL 編碼。例如：
- `@` → `%40`
- `#` → `%23`
- `/` → `%2F`

或使用 Python 編碼：
```python
from urllib.parse import quote
password = "my@pass#word"
encoded = quote(password)
print(f"redis://default:{encoded}@host:port/0")
```

### Docker 部署

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - REDIS_URL=${REDIS_URL}
      - MEXC_API_KEY=${MEXC_API_KEY}
      - MEXC_SECRET_KEY=${MEXC_SECRET_KEY}
```

**運行**:
```bash
# 設置環境變數
export REDIS_URL="redis://default:password@your-redis-cloud.com:6379/0"
export MEXC_API_KEY="your_api_key"
export MEXC_SECRET_KEY="your_secret_key"

# 啟動
docker-compose up -d
```

### Cloud Run 部署

```bash
gcloud run deploy qrl-trading-api \
  --image gcr.io/PROJECT_ID/qrl-trading-api \
  --set-env-vars REDIS_URL="redis://default:password@your-redis-cloud.com:6379/0" \
  --set-secrets MEXC_API_KEY=mexc-api-key:latest,MEXC_SECRET_KEY=mexc-secret-key:latest
```

### 效能建議

1. **使用連接池**: redis-py 自動處理連接池
2. **選擇就近區域**: 選擇與應用相同區域的 Redis Cloud 實例
3. **監控延遲**: 使用 Redis Cloud 控制台監控延遲
4. **設置適當超時**: 已在 config.py 設置 5 秒超時

### 安全提醒

⚠️ **不要將 REDIS_URL 提交到 Git**
- 使用 `.env` 文件（已在 .gitignore 中）
- 使用環境變數或密鑰管理服務
- Cloud Run: 使用 Secret Manager
- 本地開發: 使用 `.env` 文件

### 參考資源

- [Redis Cloud 文檔](https://redis.com/redis-enterprise-cloud/overview/)
- [redis-py 文檔](https://redis-py.readthedocs.io/)
- [FastAPI 環境變數](https://fastapi.tiangolo.com/advanced/settings/)
