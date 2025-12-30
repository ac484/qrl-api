## 1️⃣ 心智模型（清晰分層）

```
[ Application Layer ]              ← 你的業務程式
        │
[ Redis Service Layer ]            ← 封裝 redis 操作（cache / repo / counter / history）
        │
[ redis-py Client Layer ]          ← sync/async client + connection pool
        │
[ Connection Layer ]               ← client → connection → socket IO
        │
[ Socket IO / RESP Parser Layer ]  ← Python parser fallback / hiredis C parser
        │
[ Redis Server ]                  ← 真正的 Redis
```

---

## 2️⃣ 調整後結構樹

```text
infrastructure\external\
├─ redis_client/                     ← Redis 封裝層
│  ├─ __init__.py                   ← 對外導出
│  ├─ asyncio/                      ← Async Redis client 封裝
│  │  ├─ __init__.py
│  │  ├─ client.py                  ← Async Client API
│  │  ├─ connection.py              ← Async Connection
│  │  └─ pool.py                    ← Async Connection Pool
│  ├─ client.py                     ← Sync Client API
│  ├─ connection.py                 ← Sync Connection
│  ├─ pool.py                       ← Sync Connection Pool
│  ├─ services/                     ← 業務邏輯層（Cache / Repo / Counter / History）
│  │   ├─ __init__.py
│  │   ├─ balance_cache.py
│  │   ├─ market_cache.py
│  │   ├─ position_repo.py
│  │   ├─ position_layers_repo.py
│  │   ├─ trade_history_repo.py
│  │   ├─ trade_counter_repo.py
│  │   ├─ cost_repo.py
│  │   └─ mexc_raw_repo.py
│  ├─ commands/                     ← Redis commands 封裝
│  │   ├─ __init__.py
│  │   └─ ...                       ← 可拆分每個 command 類別
│  ├─ _parsers/                     ← ⭐ RESP 解析層
│  │   ├─ __init__.py
│  │   ├─ base.py                   ← Parser 基礎抽象類
│  │   ├─ socket.py                 ← Socket / IO parser
│  │   ├─ hiredis.py                ← 封裝 hiredis C parser
│  │   ├─ resp2.py                  ← Python fallback RESP2 parser
│  │   └─ resp3.py                  ← Python fallback RESP3 parser
│  └─ exceptions.py                 ← Exception 定義
│
├─ hiredis/                          ← C 擴充套件（optional）
│  ├─ __init__.py
│  └─ hiredis*.pyd / .so
```

---

## 3️⃣ 調整邏輯與拆分理由

1. **services/**

   * 將原本散落在 redis_client 下的 `balance_cache.py`、`position_repo.py` 等檔案統一放在 `services/`
   * 方便與 redis-py client 層分離，專注於業務邏輯（cache、repo、counter、history）
   * 每個檔案保持單一責任，避免過大 (>4000字元)

2. **async / sync client 分層**

   * 原本 client.py、core.py 等混在一起 → 明確區分 `asyncio/` 與 sync 層
   * Async 層對應 `async def` API，sync 層對應普通方法

3. **_parsers/**

   * 將 parser 抽象層單獨拆出來，Python fallback 與 hiredis C parser 都在 `_parsers/`
   * 符合心智模型中「Socket IO → RESP Parser → Redis Server」流程

4. **commands/**

   * 未來可拆每個命令成模組，如 `get.py`、`set.py`，避免單檔過大

5. **exceptions.py**

   * 單檔集中定義所有 Redis client 可能丟出的例外

---

## 4️⃣ 遷移優先順序（Sequential Thinking）

1. **先建立資料夾結構**：`services/`、`asyncio/`、`_parsers/`
2. **拆分 client 層**：sync 與 async 分別移入 `client.py` / `asyncio/client.py`
3. **拆分業務服務層**：`balance_cache.py`、`position_repo.py` 等依功能移入 `services/`
4. **整合 core.py**：將共用方法、工具抽成 services 或 parser
5. **檢查依賴**：確保 services 只依賴 client，不直接操作 socket 或 hiredis
6. **逐檔測試**：每個拆分檔案保證功能正常
7. **重構 _parsers**：如有必要，先保留 Python fallback，再逐步整合 hiredis

---

## 5️⃣ 奧卡姆剃刀 / 極簡主義原則

* 每個檔案單一責任
* 避免在單檔中混合 sync/async、業務邏輯與底層 client
* 所有檔案 < 4000 字元（必要時再拆 services 或 parser）
* 最少依賴（只依賴 redis-py 或 hiredis，不額外封裝過度）

---
