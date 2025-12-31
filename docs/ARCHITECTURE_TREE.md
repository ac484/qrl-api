# Deployable Architecture Tree

This file presents a concrete, implementable project structure derived from the current architecture guardrails. Use this as the canonical layout to migrate toward; each file should be small (one responsibility) and testable.
See `ARCHITECTURE_RULES.md` and `architecture/ARCHITECTURE.md` for the active guardrails; legacy planning notes are archived.

## Progress snapshot
- Stage 0 skeleton created under `src/app/*` with empty packages and `bootstrap.py` placeholders.
- Interfaces: HTTP shim modules expose legacy routers from `api/*`; account routes now assembled directly in `interfaces/http/account.py` (balance logic inlined, orders/trades/sub-account routers included).
- Cloud tasks: task handlers now live in `src/app/application/account` and `src/app/application/market`, and `interfaces/tasks` mounts them; removed the old `infrastructure/tasks/*` router files.
- Cleanup: legacy `infrastructure/cloud_tasks.py` shim removed after the interfaces/tasks router took over mounting; removed unused `infrastructure/tasks/auth.py` placeholder.
- Runtime logic still relies on legacy handlers for HTTP, while tasks now use the application-layer handlers; see `src/app/README.md` for legacy → target mapping.

src/
└── app/
    ├── interfaces/
    │   ├── http/
    │   │   ├── account.py                # API controllers: request -> application
    │   │   ├── market.py
    │   │   ├── bot.py
    │   │   ├── status.py
    │   │   └── sub_account.py
    │   └── tasks/
    │       ├── mexc/
    │       │   ├── sync_market.py
    │       │   ├── sync_account.py
    │       │   └── sync_trades.py
    │       └── auth.py
    ├── application/
    │   ├── account/
    │   │   ├── get_balance.py
    │   │   ├── list_orders.py
    │   │   ├── list_trades.py
    │   │   └── dto.py
    │   ├── market/
    │   │   ├── get_price.py
    │   │   ├── get_orderbook.py
    │   │   ├── get_klines.py
    │   │   └── dto.py
    │   ├── trading/
    │   │   ├── execute_trade.py
    │   │   ├── validate_trade.py
    │   │   ├── update_position.py
    │   │   ├── manage_risk.py
    │   │   └── workflow.py
    │   └── bot/
    │       ├── start.py
    │       ├── stop.py
    │       └── status.py
    ├── domain/
    │   ├── models/
    │   │   ├── account.py
    │   │   ├── balance.py
    │   │   ├── price.py
    │   │   ├── trade.py
    │   │   ├── position.py
    │   │   └── order.py
    │   ├── strategies/
    │   │   ├── base.py
    │   │   └── example_strategy.py
    │   ├── risk/
    │   │   ├── limits.py
    │   │   └── stop_loss.py
    │   ├── position/
    │   │   ├── calculator.py
    │   │   └── updater.py
    │   ├── ports/
    │   │   ├── account_port.py
    │   │   ├── market_port.py
    │   │   ├── trade_port.py
    │   │   └── position_port.py
    │   └── events/
    │       └── trading_events.py
    ├── infrastructure/
    │   ├── exchange/
    │   │   └── mexc/
    │   │       ├── http/
    │   │       │   ├── auth/
    │   │       │   │   ├── sign_request.py
    │   │       │   │   └── headers.py
    │   │       │   ├── market/
    │   │       │   │   ├── get_price.py
    │   │       │   │   └── get_orderbook.py
    │   │       │   ├── account/
    │   │       │   │   ├── get_balance.py
    │   │       │   │   └── list_orders.py
    │   │       │   └── trade/
    │   │       │       ├── place_order.py
    │   │       │       └── cancel_order.py
    │   │       ├── ws/
    │   │       │   ├── connect.py
    │   │       │   └── handlers.py
    │   │       ├── adapters/
    │   │       │   ├── market_adapter.py
    │   │       │   └── account_adapter.py
    │   │       └── _shared/
    │   │           ├── http_client.py
    │   │           └── response_parser.py
    │   ├── persistence/
    │   │   └── redis/
    │   │       ├── connection/
    │   │       │   ├── pool.py
    │   │       │   └── connect.py
    │   │       ├── codecs/
    │   │       │   └── json_codec.py
    │   │       ├── keys/
    │   │       │   ├── account_keys.py
    │   │       │   └── market_keys.py
    │   │       └── repos/
    │   │           ├── account_balance_repo.py
    │   │           └── market_price_repo.py
    │   ├── bot_runtime/
    │   │   ├── lifecycle.py
    │   │   ├── executor.py
    │   │   └── risk_adapter.py
    │   ├── scheduler/
    │   │   └── cloud_tasks.py
    │   └── config/
    │       ├── settings.py
    │       └── env.py
    ├── shared/
    │   ├── clock.py
    │   ├── ids.py
    │   ├── typing.py
    │   └── errors.py
    └── bootstrap.py

# Top-level files (project root)
- README.md
- Dockerfile
- cloudbuild.yaml
- main.py                # lightweight app entry (imports bootstrap)
- requirements.txt
- tests/                 # keep tests next to project (follow existing)

# Notes / Migration hints
- Keep `interfaces/http/` free of infrastructure imports; controllers should call `application` use-cases.
- Implement `domain/ports/*` as abstract protocols; `infrastructure/*/adapters` implement them.
- Enforce file-size rule (recommended): single .py <= 4000 bytes.
- Add `ARCHITECTURE_RULES.md` for CI checks (optional): file-size test, forbidden filenames, mapping conventions.

# Suggested next tasks
1. Create `ARCHITECTURE_RULES.md` + file-size checker script.
2. Provide an example `application/trading/execute_trade.py` with tests.
3. Add thin adapters for one MEXC endpoint and a Redis repo example.
