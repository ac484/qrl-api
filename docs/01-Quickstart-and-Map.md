## 01 快速開始與導覽

**目的**：5 分鐘內啟動服務並知道後續閱讀路線。  
**必要條件**：Python 3.11+、Redis（本地或雲端）、MEXC API Key（僅開啟 Spot Trading）。

### 立即啟動（本地）
```bash
git clone https://github.com/7Spade/qrl-api.git
cd qrl-api
python -m venv venv && source venv/bin/activate   # Windows 用 venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # 填入 MEXC_API_KEY、MEXC_SECRET_KEY、REDIS_URL
docker run -d -p 6379:6379 --name redis redis:7-alpine  # 無 Redis 可用此
uvicorn main:app --reload --port 8080
open http://localhost:8080/docs
```

### 立即啟動（Docker）
```bash
docker build -t qrl-api .
docker run -p 8080:8080 \
  -e MEXC_API_KEY=your_key \
  -e MEXC_SECRET_KEY=your_secret \
  -e REDIS_URL=redis://host.docker.internal:6379/0 \
  qrl-api
```

### 最小必填環境變數
```bash
MEXC_API_KEY=xxx
MEXC_SECRET_KEY=xxx
REDIS_URL=redis://localhost:6379/0
TRADING_SYMBOL=QRLUSDT  # 預設
DRY_RUN=true            # 實盤前請保留 true
```

### 啟動後自我檢查
```bash
curl http://localhost:8080/health          # 期待 {"status":"healthy"}
curl http://localhost:8080/market/price/QRLUSDT
curl http://localhost:8080/status          # 應有 latest_price/position 字段
```

### 路線圖（像看書一樣）
- 部署/啟動：00 → 03  
- 架構速讀：02  
- 監控/排障：04 → 07  
- 策略與資料：05 → 06  
- 成本安全：08

### 常見快速解法
- 連不上 MEXC：確認 API Key 只開 Spot Trading、未過期、未打開提款權限。
- Redis 無資料：確定 Scheduler 任務有跑（見 04），或本地先手動呼叫 `/tasks/05-min-job`。
- Balance 為 0：優先信任 API 回傳；若 API 正常但顯示異常，檢查 07 提到的資料一致性修復。
