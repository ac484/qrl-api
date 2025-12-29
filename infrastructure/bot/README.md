infrastructure/
└── bot/
    ├── __init__.py
    │
    ├── bot_utils.py                 # 共用工具（時間、格式、常數）
    │
    ├── bot_core/                    # Orchestrator（只負責流程）
    │   ├── __init__.py
    │   └── core.py                  # execute_cycle / phase 調度
    │
    ├── startup/                     # Phase 1
    │   ├── __init__.py
    │   └── startup_service.py       # Redis 檢查 / position 載入
    │
    ├── market_data/                 # Phase 2（最肥）
    │   ├── __init__.py
    │   ├── market_data_service.py   # 統一對外收集介面
    │   ├── price_collector.py       # ticker / price / volume
    │   ├── balance_collector.py     # QRL / USDT balance
    │   └── position_calculator.py   # avg_cost / pnl / invested
    │
    ├── strategy/                    # Phase 3
    │   ├── __init__.py
    │   └── ma_strategy.py           # MA 計算 / BUY SELL HOLD
    │
    ├── risk/                        # Phase 4
    │   ├── __init__.py
    │   └── risk_control_service.py  # 資金 / 倉位風控
    │
    ├── execution/                   # Phase 5
    │   ├── __init__.py
    │   └── execution_service.py     # 下單 / dry-run
    │
    └── reporting/                   # Phase 6
        ├── __init__.py
        └── cleanup_service.py       # 收尾 / completed_at
