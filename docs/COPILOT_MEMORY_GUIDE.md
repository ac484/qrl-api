---
post_title: 'Copilot Memory Guide'
author1: 'Copilot'
post_slug: 'copilot-memory-guide'
microsoft_alias: 'copilot'
featured_image: ''
categories: ['documentation']
tags: ['copilot', 'memory', 'qrl-api']
ai_note: 'Generated with Copilot assistance'
summary: 'How to use Copilot memory for the QRL Trading API project.'
post_date: '2026-01-01'
---

## Copilot Memory Guide

### Overview
Copilot memory keeps the QRL Trading API context close to the assistant so suggestions align with our FastAPI + MEXC trading stack. Use it to preserve key facts about trading flows, cache rules, deployment commands, and coding conventions.

### When to save a memory
- New or updated trading logic, e.g., order lifecycle or risk controls.
- Changes to Redis TTL defaults or cache keys.
- MEXC API quirks, signing rules, or rate-limit handling.
- Required environment variables and bootstrap commands.
- Decisions from code review that should guide future work.

### How to save
Use `store_memory` with concise facts (< 200 characters) and clear citations.

```javascript
store_memory({
  category: "general",
  citations: "README.md 快速開始; src/infrastructure/redis",
  fact: "Market and account endpoints cache MEXC data in Redis with configurable TTLs to cut API calls",
  reason: "Caching behavior shapes performance tuning and must stay consistent across endpoints",
  subject: "caching"
})
```

Suggested categories:
- `general`: architecture, trading flow, cache strategy, risk rules.
- `file_specific`: module-level patterns (e.g., where to place repos or services).
- `user_preferences`: naming, logging fields, review feedback.
- `bootstrap_and_build`: make targets, env var requirements, runbook steps.

### What to capture for QRL Trading API
- **Architecture**: FastAPI async stack, repository pattern, Redis as the cache layer, MEXC v3 REST/WS integration.
- **Operations**: How to start (`uvicorn main:app --reload`), health endpoints, and make targets for lint/type/test.
- **Trading**: Strategy triggers (MA crossover), six-stage execution flow, and safeguards like dry-run mode.
- **Data**: Cache key patterns, TTL defaults, and when to bypass cache for freshness.
- **Secrets**: Required env vars (`MEXC_API_KEY`, `MEXC_SECRET_KEY`, `REDIS_URL`) and where they live (.env or Secret Manager).

### Retrieval quick steps
- Search by keyword: `memory-search_nodes({ query: "caching" })`
- Open by subject: `memory-open_nodes({ names: ["project overview"] })`
- Read everything (periodic audit): `memory-read_graph()`

### Hygiene
- Replace outdated facts when TTLs, endpoints, or strategies change.
- Avoid storing secrets; reference their locations instead.
- Keep citations specific (file + section) so future updates are easy to verify.
- Re-run searches after large refactors to spot stale memories.
