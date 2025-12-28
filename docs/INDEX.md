## QRL Trading API - 文檔導覽

**目的**：以 00/01/02 編號提供「像讀書一樣」的閱讀順序。`docs/00-Cloud Run Deploy.md` 保留原樣。

---

## 📚 推薦閱讀順序
1. [00-Cloud Run Deploy.md](00-Cloud%20Run%20Deploy.md)（保留原版）
2. [01-Quickstart-and-Map.md](01-Quickstart-and-Map.md) — 5 分鐘啟動與導覽
3. [02-System-Overview.md](02-System-Overview.md) — 架構與資料流摘要
4. [03-Deployment.md](03-Deployment.md) — 本地、Docker、Cloud Run 快速部署
5. [04-Operations-and-Tasks.md](04-Operations-and-Tasks.md) — Scheduler、監控、日誌
6. [05-Strategies-and-Data.md](05-Strategies-and-Data.md) — 屯幣策略、資料來源、倉位分層
7. [06-API-Compliance-and-Accounts.md](06-API-Compliance-and-Accounts.md) — MEXC 規範與子帳號
8. [07-Fixes-and-Troubleshooting.md](07-Fixes-and-Troubleshooting.md) — 核心修復與常見問題
9. [08-Costs-and-Controls.md](08-Costs-and-Controls.md) — 成本、風險與安全守則

---

## 🗂️ 分類與用途

| 編號 | 檔案 | 用途 |
|------|------|------|
| 00 | 00-Cloud Run Deploy.md | 原始 Cloud Run 部署筆記（不變動） |
| 01 | 01-Quickstart-and-Map.md | 5 分鐘啟動、必要環境、路線圖 |
| 02 | 02-System-Overview.md | 架構、資料流、核心模組摘要 |
| 03 | 03-Deployment.md | 本地/Docker/Cloud Run 部署步驟與驗證 |
| 04 | 04-Operations-and-Tasks.md | Scheduler 任務摘要、監控指標、日誌查詢 |
| 05 | 05-Strategies-and-Data.md | 屯幣策略、資料來源權威、倉位分層 |
| 06 | 06-API-Compliance-and-Accounts.md | MEXC API 合規、簽名、子帳號查詢 |
| 07 | 07-Fixes-and-Troubleshooting.md | Redis TTL、原始響應存放、OIDC/資料一致性修復；常見故障清單 |
| 08 | 08-Costs-and-Controls.md | 成本估算、節省手段、安全最小權限 |

---

## 🧭 角色導覽
- **新進開發者**：01 → 02 → 05 → 06  
- **部署工程師**：01 → 03 → 04 → 08  
- **維運/排障**：01 → 04 → 07  
- **策略/產品**：05 → 02 → 08  

---

## 🗄️ 備註與原始資料
- 深度內容仍可查閱：1-qrl-accumulation-strategy.md、2-bot.md、3-cost.md、4-scheduler.md、5-SCHEDULED_TASKS_DESIGN.md、6-ARCHITECTURE_CHANGES.md、DATA_SOURCE_STRATEGY.md、MEXC_API_COMPLIANCE.md、MONITORING_GUIDE.md、POSITION_LAYERS.md、SUB_ACCOUNT_GUIDE.md、TROUBLESHOOTING.md、mexc-dev-url.md。
- 冗餘的舊版彙總文件（CONSOLIDATED_*, QUICK_START.md）已移除，避免重複。
- 檔名遵循 `NN-Title.md`，標題使用 H2（避免 H1），語氣統一、內容聚焦。
- 日常查閱以 00–08 為主，深度或歷史決策再查原始細節檔。
