一、檔案樹（示意，實務可用）
infrastructure\external\mexc_client
├─ __init__.py
├─ client.py                  ← 核心 API client（同步 + 異步封裝）
├─ connection.py              ← HTTP / WebSocket 連線管理
├─ session.py                 ← requests / aiohttp session 管理
├─ exceptions.py              ← API error / trading exception
├─ endpoints/                 ← 各類 API 封裝
│   ├─ __init__.py
│   ├─ account.py              ← 帳戶相關 API
│   ├─ market.py               ← 市場行情 API
│   ├─ order.py                ← 下單 / 查單 API
│   └─ sub_account.py          ← 子帳戶相關 API
├─ websocket/                 ← WebSocket 封裝
│   ├─ __init__.py
│   ├─ client.py               ← WS client
│   ├─ manager.py              ← WS 事件管理 / reconnect
│   └─ handlers.py             ← 事件 callback handler
├─ utils/                     ← 工具 / 輔助函數
│   ├─ __init__.py
│   ├─ signature.py            ← 簽名 / 驗證
│   ├─ types.py                ← 自訂型別 / data models
│   └─ parser.py               ← JSON / dict 解析
└─ config.py                  ← API Key / URL / timeout 設定

二、邏輯分層（心智模型）
[ Application / Trading Bot ]
            │
            ▼
[ mexc_v3_api.client ]
   ├─ 同步 API (requests)
   └─ 異步 API (aiohttp / asyncio)
            │
            ▼
[ connection / session ]
   ├─ HTTP requests / responses
   ├─ WebSocket 連線管理
   └─ Retry / Timeout / Pool
            │
            ▼
[ endpoints ]
   ├─ account.py      ← 帳戶餘額、資金轉入轉出
   ├─ market.py       ← 市場行情、K線、深度
   ├─ order.py        ← 下單 / 改單 / 查單
   └─ sub_account.py  ← 子帳戶操作
            │
            ▼
[ websocket ]
   ├─ client.py       ← 建立 WS 連線
   ├─ manager.py      ← 重連 / 訂閱管理
   └─ handlers.py     ← 消息回調 / 推送解析
            │
            ▼
[ utils / parser / signature ]
   ├─ JSON / dict / DataClass 轉換
   ├─ API request 簽名
   └─ type safety / logging


三、心智模型（概念圖）

核心 client

封裝所有 API 呼叫

提供 sync / async 統一接口

連線層

HTTP / WebSocket 基礎設施

Pool / Retry / Timeout

保證高頻交易穩定性

API 分類層

Account / Market / Order / SubAccount

對應交易所官方文檔

單一模組管理單一功能

WebSocket 層

實時數據 / 訂閱管理

Event callback / handler

工具層

API 簽名 / JSON parser / 型別檢查

保證 client 層乾淨、單一責任

四、使用建議

Async 專案：client.py + aiohttp session + WebSocket manager

高併發 / trading bot：Session pool + retry + signature utils

架構清晰：每個 endpoint 單獨模組 → 易於測試與擴展
