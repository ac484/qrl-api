---
post_title: 'Copilot Memory Quick Reference'
author1: 'Copilot'
post_slug: 'copilot-memory-quick-reference'
microsoft_alias: 'copilot'
featured_image: ''
categories: ['documentation']
tags: ['copilot', 'memory', 'qrl-api']
ai_note: 'Generated with Copilot assistance'
summary: 'Quick commands for using Copilot memory on the QRL Trading API.'
post_date: '2026-01-01'
---

## Copilot Memory Quick Reference

### Core commands
- Store a fact
```javascript
store_memory({
  category: "general",
  citations: "README.md 技術架構",
  fact: "QRL Trading API uses FastAPI with async httpx and Redis caching for MEXC v3",
  reason: "Ensures suggestions match the async stack and caching approach",
  subject: "project overview"
})
```

- Search memories
```javascript
memory-search_nodes({ query: "caching" })
```

- Open specific subjects
```javascript
memory-open_nodes({ names: ["tooling"] })
```

- Read the graph
```javascript
memory-read_graph()
```

### Categories
| 類別 | 用途 |
|------|------|
| `general` | 架構、交易流程、快取策略 |
| `file_specific` | 模組慣例或特殊處理 |
| `user_preferences` | 命名、日誌欄位、審查偏好 |
| `bootstrap_and_build` | make 指令、啟動與部署設定 |

### What to log for this project
- Trading stages, risk controls, and dry-run expectations.
- Redis key patterns與 TTL 預設。
- MEXC API 簽名與節流注意事項。
- 必備環境變數與啟動指令。

### Good practice
- Keep facts < 200 字元；提供明確 citations。
- 不要寫入秘密；僅引用 .env 或 Secret Manager。
- 更新或刪除過時記憶，避免混淆未來的建議。

### Helpful subjects to query
```javascript
memory-open_nodes({ names: ["project overview", "caching", "tooling"] })
memory-search_nodes({ query: "mexc rate limit" })
```
