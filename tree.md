├─api
│  │  account_routes.py
│  │  bot_routes.py
│  │  market_routes.py
│  │  README.md
│  │  status_routes.py
│  │  sub_account_routes.py
│  │  __init__.py
│  │
│  ├─account
│  │      balance.py
│  │      orders.py
│  │      sub_accounts.py
│  │      trades.py
│  │      __init__.py
│  │
│  ├─bot
│  │      control.py
│  │      execute.py
│  │      __init__.py
│  │
│  ├─market
│  │      agg_trades.py
│  │      book_ticker.py
│  │      exchange_info.py
│  │      klines.py
│  │      orderbook.py
│  │      price.py
│  │      ticker.py
│  │      trades.py
│  │      __init__.py
│  │
│  ├─status
│  │      api_info.py
│  │      dashboard.py
│  │      health.py
│  │      status.py
│  │      __init__.py
│  │
│  └─sub_account
│          api_key.py
│          balance.py
│          list.py
│          transfer.py
│          __init__.py
│
├─domain
│  │  __init__.py
│  │
│  ├─interfaces
│  │      account.py
│  │      cost.py
│  │      market.py
│  │      position.py
│  │      price.py
│  │      trade.py
│  │      __init__.py
│  │
│  ├─position_manager
│  │      core.py
│  │      __init__.py
│  │
│  ├─risk_manager
│  │      core.py
│  │      __init__.py
│  │
│  └─trading_strategy
│          core.py
│          __init__.py
│
├─infrastructure
│  │  bot.py
│  │  cloud_tasks.py
│  │  README.md
│  │  __init__.py
│  │
│  ├─bot
│  │  │  bot_utils.py
│  │  │  README.md
│  │  │  __init__.py
│  │  │
│  │  └─bot_core
│  │          core.py
│  │          __init__.py
│  │
│  ├─config
│  │      config.py
│  │      settings.py
│  │      __init__.py
│  │
│  ├─external
│  │  │  README.md
│  │  │  __init__.py
│  │  │
│  │  ├─mexc_client
│  │  │      account.py
│  │  │      account_repo.py
│  │  │      client.py
│  │  │      core.py
│  │  │      market_endpoints.py
│  │  │      signer.py
│  │  │      sub_account_broker_repo.py
│  │  │      sub_account_facade.py
│  │  │      sub_account_spot_repo.py
│  │  │      trade_repo.py
│  │  │      __init__.py
│  │  │
│  │  └─redis_client
│  │          balance_cache.py
│  │          bot_status_repo.py
│  │          client.py
│  │          core.py
│  │          cost_repo.py
│  │          market_cache.py
│  │          mexc_raw_repo.py
│  │          position_layers_repo.py
│  │          position_repo.py
│  │          price_repo.py
│  │          trade_counter_repo.py
│  │          trade_history_repo.py
│  │          __init__.py
│  │
│  ├─tasks
│  │      auth.py
│  │      mexc_tasks.py
│  │      mexc_tasks_core.py
│  │      router.py
│  │      __init__.py
│  │
│  └─utils
│          decorators.py
│          keys.py
│          metadata.py
│          redis_data_manager.py
│          redis_helpers.py
│          redis_helpers_core.py
│          type_safety.py
│          utils.py
│          utils_core.py
│          __init__.py
│
├─models
│      __init__.py
│
├─repositories
│  │  README.md
│  │  __init__.py
│  │
│  ├─account
│  │      cost_calculator.py
│  │      cost_repository.py
│  │      cost_repository_core.py
│  │      position_repository.py
│  │      position_repository_core.py
│  │      __init__.py
│  │
│  ├─market
│  │      price_repository.py
│  │      price_repository_core.py
│  │      __init__.py
│  │
│  └─trade
│          trade_repository.py
│          trade_repository_core.py
│          __init__.py
│
├─services
│  │  README.md
│  │  __init__.py
│  │
│  ├─account
│  │      balance_service.py
│  │      balance_service_core.py
│  │      __init__.py
│  │
│  ├─market
│  │      cache_policy.py
│  │      cache_service.py
│  │      cache_strategy.py
│  │      market_service.py
│  │      market_service_core.py
│  │      mexc_client_service.py
│  │      price_history_manager.py
│  │      price_repo_service.py
│  │      price_resolver.py
│  │      __init__.py
│  │
│  └─trading
│          balance_resolver.py
│          position_service.py
│          position_updater.py
│          price_resolver.py
│          repository_service.py
│          risk_service.py
│          strategy_service.py
│          trading_service.py
│          trading_service_core.py
│          trading_workflow.py
│          __init__.py
│
└─templates
        dashboard.html
