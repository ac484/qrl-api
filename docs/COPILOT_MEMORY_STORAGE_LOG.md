---
post_title: 'Copilot Memory Storage Log'
author1: 'Copilot'
post_slug: 'copilot-memory-storage-log'
microsoft_alias: 'copilot'
featured_image: ''
categories: ['documentation']
tags: ['copilot', 'memory', 'qrl-api']
ai_note: 'Generated with Copilot assistance'
summary: 'Storage log for Copilot memories that describe the QRL Trading API.'
post_date: '2026-01-01'
---

## Copilot Memory Storage Log

### Stored on 2026-01-01
- Total entries: 3

#### Project overview
- Category: general
- Subject: project overview
- Fact: QRL Trading API is a FastAPI + Uvicorn asynchronous service that automates QRL/USDT trading on MEXC v3 REST and WebSocket APIs with Redis-backed caching.
- Citations: README.md (overview, 技術架構), main.py

#### Development workflow
- Category: bootstrap_and_build
- Subject: tooling
- Fact: Development uses `make fmt` (black), `make lint` (ruff), `make type` (mypy), and `make test` (pytest) after installing dependencies via `pip install -r requirements-dev.txt`.
- Citations: README.md (開發常用指令), requirements-dev.txt

#### Data caching
- Category: general
- Subject: caching
- Fact: Market, account, and order data are cached in Redis with configurable TTLs to reduce MEXC API calls while keeping responses fresh.
- Citations: README.md (核心特性、API 端點說明), src/infrastructure/redis usage

### Maintenance notes
- Review memories when API endpoints, Redis TTL defaults, or trading flow changes.
- Update citations if files move or commands change.
