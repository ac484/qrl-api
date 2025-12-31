# Dead Code Analysis Report

## Summary

- **Total Files Analyzed**: 227
- **Files with Dead Code**: 153 (67.4%)
- **Unused Imports**: 201
- **Unused Definitions**: 99

## Files with Dead Code

### src/app/application/account/balance_service.py

**Unused Definitions:**
- Line 10: Class `BalanceService`

### src/app/application/account/dto.py

**Unused Imports:**
- Line 8: `from src.app.infrastructure.external import QRL_USDT_SYMBOL`

### src/app/application/account/get_balance.py

**Unused Imports:**
- Line 7: `from src.app.application.account.balance_service import BalanceService`

### src/app/application/bot/start.py

**Unused Imports:**
- Line 5: `from src.app.application.trading.services import TradingService`

### src/app/application/bot/status.py

**Unused Imports:**
- Line 8: `from src.app.application.trading.services import TradingService`

### src/app/application/bot/stop.py

**Unused Imports:**
- Line 5: `from src.app.application.trading.services import TradingService`

### src/app/application/market/dto.py

**Unused Imports:**
- Line 7: `from src.app.infrastructure.external import QRL_USDT_SYMBOL`

### src/app/application/trading/execute_trade.py

**Unused Imports:**
- Line 8: `from src.app.application.trading.services import TradingService`

### src/app/application/trading/manage_risk.py

**Unused Imports:**
- Line 7: `from src.app.application.trading.services import RiskService`

### src/app/application/trading/services/__init__.py

**Unused Imports:**
- Line 7: `from src.app.application.trading.services.trading.trading_service import TradingService`
- Line 8: `from src.app.application.trading.services.trading.strategy_service import StrategyService`
- Line 9: `from src.app.application.trading.services.trading.risk_service import RiskService`
- Line 10: `from src.app.application.trading.services.trading.position_service import PositionService`
- Line 11: `from src.app.application.trading.services.trading.repository_service import RepositoryService`
- Line 12: `from src.app.application.trading.services.trading.trading_workflow import TradingWorkflow`
- Line 13: `from src.app.application.trading.services.trading.balance_resolver import BalanceResolver`
- Line 14: `from src.app.application.trading.services.trading.price_resolver import PriceResolver`
- Line 15: `from src.app.application.trading.services.trading.position_updater import PositionUpdater`
- Line 18: `from src.app.application.trading.services.market.market_service import MarketService`
- Line 19: `from src.app.application.trading.services.market.cache_service import CacheService`
- Line 20: `from src.app.application.trading.services.market.price_repo_service import PriceRepoService`
- Line 21: `from src.app.application.trading.services.market.mexc_client_service import MexcClientService`
- Line 22: `from src.app.application.trading.services.market.price_history_manager import PriceHistoryManager`
- Line 25: `from src.app.application.trading.services.account.balance_service import BalanceService`

### src/app/application/trading/services/account/__init__.py

**Unused Imports:**
- Line 1: `from balance_service import BalanceService`

### src/app/application/trading/services/account/balance_service.py

**Unused Imports:**
- Line 2: `from balance_service_core import BalanceService`

### src/app/application/trading/services/account/balance_service_core.py

**Unused Imports:**
- Line 6: `from src.app.application.account.balance_service import BalanceService`

### src/app/application/trading/services/market/__init__.py

**Unused Imports:**
- Line 1: `from market_service import MarketService`
- Line 2: `from cache_service import CacheService`
- Line 3: `from price_repo_service import PriceRepoService`
- Line 4: `from mexc_client_service import MexcClientService`

### src/app/application/trading/services/market/cache_policy.py

**Unused Definitions:**
- Line 16: Function `kline_ttl`

### src/app/application/trading/services/market/cache_service.py

**Unused Definitions:**
- Line 9: Class `CacheService`

### src/app/application/trading/services/market/cache_strategy.py

**Unused Definitions:**
- Line 5: Class `CacheStrategy`

### src/app/application/trading/services/market/market_service.py

**Unused Imports:**
- Line 2: `from market_service_core import MarketService`

### src/app/application/trading/services/market/market_service_core.py

**Unused Definitions:**
- Line 14: Class `MarketService`

### src/app/application/trading/services/market/mexc_client_service.py

**Unused Definitions:**
- Line 9: Class `MexcClientService`

### src/app/application/trading/services/market/price_history_manager.py

**Unused Definitions:**
- Line 4: Class `PriceHistoryManager`

### src/app/application/trading/services/market/price_repo_service.py

**Unused Definitions:**
- Line 9: Class `PriceRepoService`

### src/app/application/trading/services/market/price_resolver.py

**Unused Definitions:**
- Line 5: Class `PriceResolver`

### src/app/application/trading/services/trading/__init__.py

**Unused Imports:**
- Line 1: `from trading_service import TradingService`
- Line 2: `from strategy_service import StrategyService`
- Line 3: `from risk_service import RiskService`
- Line 4: `from position_service import PositionService`
- Line 5: `from repository_service import RepositoryService`

### src/app/application/trading/services/trading/balance_resolver.py

**Unused Definitions:**
- Line 10: Class `BalanceResolver`

### src/app/application/trading/services/trading/position_service.py

**Unused Definitions:**
- Line 9: Class `PositionService`

### src/app/application/trading/services/trading/position_updater.py

**Unused Definitions:**
- Line 8: Class `PositionUpdater`

### src/app/application/trading/services/trading/price_resolver.py

**Unused Definitions:**
- Line 7: Class `PriceResolver`

### src/app/application/trading/services/trading/repository_service.py

**Unused Definitions:**
- Line 9: Class `RepositoryService`

### src/app/application/trading/services/trading/risk_service.py

**Unused Definitions:**
- Line 9: Class `RiskService`

### src/app/application/trading/services/trading/strategy_service.py

**Unused Definitions:**
- Line 10: Class `StrategyService`

### src/app/application/trading/services/trading/trading_service.py

**Unused Imports:**
- Line 2: `from trading_service_core import TradingService`

### src/app/application/trading/services/trading/trading_service_core.py

**Unused Definitions:**
- Line 17: Class `TradingService`

### src/app/application/trading/services/trading/trading_workflow.py

**Unused Definitions:**
- Line 15: Class `TradingWorkflow`

### src/app/application/trading/update_position.py

**Unused Imports:**
- Line 7: `from src.app.application.trading.services import PositionUpdater`

### src/app/application/trading/validate_trade.py

**Unused Imports:**
- Line 7: `from src.app.application.trading.services import StrategyService`

### src/app/application/trading/workflow.py

**Unused Imports:**
- Line 7: `from src.app.application.trading.services import TradingWorkflow`

### src/app/bootstrap.py

**Unused Definitions:**
- Line 11: Function `build_app_placeholder`

### src/app/domain/events/__init__.py

**Unused Imports:**
- Line 1: `from src.app.domain.events.trading_events import OrderPlaced`
- Line 1: `from src.app.domain.events.trading_events import PriceUpdated`
- Line 1: `from src.app.domain.events.trading_events import TradeExecuted`

### src/app/domain/events/trading_events.py

**Unused Definitions:**
- Line 8: Class `PriceUpdated`
- Line 15: Class `OrderPlaced`
- Line 25: Class `TradeExecuted`

### src/app/domain/models/__init__.py

**Unused Imports:**
- Line 1: `from src.app.domain.models.account import Account`
- Line 2: `from src.app.domain.models.balance import Balance`
- Line 3: `from src.app.domain.models.order import Order`
- Line 4: `from src.app.domain.models.position import Position`
- Line 5: `from src.app.domain.models.price import Price`
- Line 6: `from src.app.domain.models.trade import Trade`

### src/app/domain/models/account.py

**Unused Definitions:**
- Line 10: Class `Account`

### src/app/domain/models/balance.py

**Unused Definitions:**
- Line 10: Class `Balance`

### src/app/domain/models/order.py

**Unused Definitions:**
- Line 12: Class `Order`

### src/app/domain/models/position.py

**Unused Definitions:**
- Line 8: Class `Position`

### src/app/domain/models/price.py

**Unused Definitions:**
- Line 8: Class `Price`

### src/app/domain/models/trade.py

**Unused Definitions:**
- Line 8: Class `Trade`

### src/app/domain/ports/account_port.py

**Unused Definitions:**
- Line 8: Class `IAccountDataProvider`

### src/app/domain/ports/cost_port.py

**Unused Definitions:**
- Line 8: Class `ICostRepository`

### src/app/domain/ports/market_port.py

**Unused Definitions:**
- Line 8: Class `IMarketDataProvider`

### src/app/domain/ports/position_port.py

**Unused Definitions:**
- Line 8: Class `IPositionRepository`

### src/app/domain/ports/price_port.py

**Unused Definitions:**
- Line 8: Class `IPriceRepository`

### src/app/domain/ports/trade_port.py

**Unused Definitions:**
- Line 8: Class `ITradeRepository`

### src/app/domain/position/__init__.py

**Unused Imports:**
- Line 1: `from src.app.domain.position.calculator import PositionManager`
- Line 2: `from src.app.domain.position.updater import PositionUpdater`

### src/app/domain/position/calculator.py

**Unused Definitions:**
- Line 13: Class `PositionManager`

### src/app/domain/position/updater.py

**Unused Imports:**
- Line 2: `from __future__ import annotations`

**Unused Definitions:**
- Line 8: Class `PositionUpdater`

### src/app/domain/risk/__init__.py

**Unused Imports:**
- Line 1: `from src.app.domain.risk.limits import RiskManager`
- Line 2: `from src.app.domain.risk.stop_loss import StopLossGuard`

### src/app/domain/risk/limits.py

**Unused Definitions:**
- Line 13: Class `RiskManager`

### src/app/domain/risk/stop_loss.py

**Unused Definitions:**
- Line 6: Class `StopLossGuard`

### src/app/domain/strategies/__init__.py

**Unused Imports:**
- Line 1: `from src.app.domain.strategies.base import BaseStrategy`
- Line 2: `from src.app.domain.strategies.example_strategy import ExampleStrategy`
- Line 3: `from src.app.domain.strategies.trading_strategy import TradingStrategy`

### src/app/domain/strategies/base.py

**Unused Imports:**
- Line 2: `from __future__ import annotations`

**Unused Definitions:**
- Line 8: Class `BaseStrategy`

### src/app/domain/strategies/example_strategy.py

**Unused Definitions:**
- Line 7: Class `ExampleStrategy`

### src/app/domain/strategies/trading_strategy.py

**Unused Definitions:**
- Line 8: Class `TradingStrategy`

### src/app/infrastructure/bot_runtime/__init__.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.bot_runtime.core import TradingBot`
- Line 3: `from src.app.infrastructure.bot_runtime.utils import calculate_moving_average`
- Line 3: `from src.app.infrastructure.bot_runtime.utils import derive_ma_pair`
- Line 3: `from src.app.infrastructure.bot_runtime.utils import compute_cost_metrics`

### src/app/infrastructure/bot_runtime/core.py

**Unused Definitions:**
- Line 16: Class `TradingBot`

### src/app/infrastructure/bot_runtime/executor.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.bot_runtime import TradingBot`

### src/app/infrastructure/bot_runtime/lifecycle.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.bot_runtime import TradingBot`

### src/app/infrastructure/bot_runtime/phases/__init__.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.bot_runtime.phases.startup import phase_startup`
- Line 3: `from src.app.infrastructure.bot_runtime.phases.data_collection import phase_data_collection`
- Line 4: `from src.app.infrastructure.bot_runtime.phases.strategy import phase_strategy`
- Line 5: `from src.app.infrastructure.bot_runtime.phases.risk import phase_risk_control`
- Line 6: `from src.app.infrastructure.bot_runtime.phases.execution import phase_execution`
- Line 7: `from src.app.infrastructure.bot_runtime.phases.cleanup import phase_cleanup`

### src/app/infrastructure/bot_runtime/risk_adapter.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.bot_runtime import TradingBot`

### src/app/infrastructure/bot_runtime/utils.py

**Unused Definitions:**
- Line 21: Function `derive_ma_pair`
- Line 36: Function `compute_cost_metrics`

### src/app/infrastructure/config/__init__.py

**Unused Imports:**
- Line 7: `from settings import Config`
- Line 7: `from settings import config`

### src/app/infrastructure/config/env.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.config import config`

### src/app/infrastructure/exchange/mexc/_shared/http_client.py

**Unused Imports:**
- Line 7: `from src.app.infrastructure.external.mexc.connection import MexcConnection`

### src/app/infrastructure/exchange/mexc/_shared/response_parser.py

**Unused Definitions:**
- Line 10: Function `passthrough`

### src/app/infrastructure/exchange/mexc/adapters/account_adapter.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.external.mexc import MEXCClient`
- Line 5: `from src.app.infrastructure.external.mexc import mexc_client`

### src/app/infrastructure/exchange/mexc/adapters/market_adapter.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.external.mexc import MEXCClient`
- Line 5: `from src.app.infrastructure.external.mexc import mexc_client`

### src/app/infrastructure/exchange/mexc/http/auth/headers.py

**Unused Definitions:**
- Line 9: Function `build_headers`

### src/app/infrastructure/exchange/mexc/http/auth/sign_request.py

**Unused Imports:**
- Line 7: `from src.app.infrastructure.external.mexc.signer import generate_signature`

### src/app/infrastructure/exchange/mexc/ws/connect.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.external.mexc import connect_public_trades`
- Line 5: `from src.app.infrastructure.external.mexc import connect_user_stream`
- Line 5: `from src.app.infrastructure.external.mexc import websocket_manager`
- Line 5: `from src.app.infrastructure.external.mexc import MEXCWebSocketClient`

### src/app/infrastructure/exchange/mexc/ws/handlers.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import BinaryDecoder`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import book_ticker_batch_stream`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import book_ticker_stream`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import build_protobuf_decoder`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import diff_depth_stream`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import kline_stream`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import mini_tickers_stream`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import partial_depth_stream`
- Line 5: `from src.app.infrastructure.external.mexc.ws_channels import trade_stream`

### src/app/infrastructure/external/__init__.py

**Unused Imports:**
- Line 6: `from src.app.infrastructure.external.mexc import mexc_client`
- Line 6: `from src.app.infrastructure.external.mexc import MEXCClient`
- Line 7: `from src.app.infrastructure.external.mexc.account import QRL_USDT_SYMBOL`
- Line 8: `from src.app.infrastructure.persistence.redis import redis_client`
- Line 8: `from src.app.infrastructure.persistence.redis import RedisClient`

### src/app/infrastructure/external/mexc/__init__.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.external.mexc.client import MEXCClient`
- Line 2: `from src.app.infrastructure.external.mexc.client import mexc_client`
- Line 3: `from src.app.infrastructure.external.mexc.exceptions import MEXCAPIException`
- Line 4: `from src.app.infrastructure.external.mexc.ws.channels import diff_depth_stream`
- Line 4: `from src.app.infrastructure.external.mexc.ws.channels import partial_depth_stream`
- Line 4: `from src.app.infrastructure.external.mexc.ws.channels import trade_stream`
- Line 4: `from src.app.infrastructure.external.mexc.ws.channels import kline_stream`
- Line 4: `from src.app.infrastructure.external.mexc.ws.channels import account_update_stream`

### src/app/infrastructure/external/mexc/account.py

**Unused Imports:**
- Line 13: `from client import MEXCClient`

### src/app/infrastructure/external/mexc/client.py

**Unused Imports:**
- Line 2: `from __future__ import annotations`

### src/app/infrastructure/external/mexc/config.py

**Unused Definitions:**
- Line 16: Function `load_settings`

### src/app/infrastructure/external/mexc/connection.py

**Unused Imports:**
- Line 2: `from __future__ import annotations`

**Unused Definitions:**
- Line 16: Class `MexcConnection`

### src/app/infrastructure/external/mexc/core.py

**Unused Imports:**
- Line 2: `from client import MEXCClient`
- Line 2: `from client import mexc_client`

### src/app/infrastructure/external/mexc/endpoints/__init__.py

**Unused Imports:**
- Line 2: `from account import AccountEndpoints`
- Line 3: `from market import MarketEndpoints`
- Line 4: `from order import OrderEndpoints`
- Line 5: `from sub_account import SubAccountEndpoints`
- Line 6: `from helpers import UserStreamMixin`
- Line 6: `from helpers import TradingHelpersMixin`

### src/app/infrastructure/external/mexc/endpoints/helpers.py

**Unused Definitions:**
- Line 7: Class `UserStreamMixin`
- Line 31: Class `TradingHelpersMixin`

### src/app/infrastructure/external/mexc/endpoints/sub_account.py

**Unused Definitions:**
- Line 11: Class `SubAccountEndpoints`

### src/app/infrastructure/external/mexc/exceptions.py

**Unused Definitions:**
- Line 4: Class `MexcAPIError`
- Line 8: Class `MexcRequestError`

### src/app/infrastructure/external/mexc/facades/__init__.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.external.mexc.facades.sub_account_facade import SubAccountFacade`

### src/app/infrastructure/external/mexc/facades/sub_account_facade.py

**Unused Definitions:**
- Line 10: Class `SubAccountFacadeMixin`

### src/app/infrastructure/external/mexc/market_endpoints.py

**Unused Definitions:**
- Line 7: Class `MarketEndpointsMixin`

### src/app/infrastructure/external/mexc/repos/__init__.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.external.mexc.repos.account_repo import AccountRepository`
- Line 3: `from src.app.infrastructure.external.mexc.repos.trade_repo import TradeRepository`
- Line 4: `from src.app.infrastructure.external.mexc.repos.sub_account_broker_repo import SubAccountBrokerRepository`
- Line 5: `from src.app.infrastructure.external.mexc.repos.sub_account_spot_repo import SubAccountSpotRepository`

### src/app/infrastructure/external/mexc/repos/account_repo.py

**Unused Definitions:**
- Line 10: Class `AccountRepoMixin`

### src/app/infrastructure/external/mexc/repos/sub_account_broker_repo.py

**Unused Definitions:**
- Line 6: Class `SubAccountBrokerRepoMixin`

### src/app/infrastructure/external/mexc/repos/sub_account_spot_repo.py

**Unused Definitions:**
- Line 6: Class `SubAccountSpotRepoMixin`

### src/app/infrastructure/external/mexc/repos/trade_repo.py

**Unused Definitions:**
- Line 5: Class `TradeRepoMixin`

### src/app/infrastructure/external/mexc/session.py

**Unused Definitions:**
- Line 7: Function `build_async_client`

### src/app/infrastructure/external/mexc/signer.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.external.mexc.utils.signature import generate_signature`

### src/app/infrastructure/external/mexc/utils/__init__.py

**Unused Imports:**
- Line 2: `from signature import generate_signature`
- Line 3: `from parser import ensure_dict`
- Line 4: `from types import JSONMapping`

### src/app/infrastructure/external/mexc/utils/parser.py

**Unused Definitions:**
- Line 5: Function `ensure_dict`

### src/app/infrastructure/external/mexc/utils/signature.py

**Unused Definitions:**
- Line 8: Function `generate_signature`

### src/app/infrastructure/external/mexc/websocket/__init__.py

**Unused Imports:**
- Line 2: `from client import MEXCWebSocketClient`
- Line 2: `from client import WS_BASE`
- Line 3: `from manager import websocket_manager`
- Line 4: `from handlers import MessageHandler`

### src/app/infrastructure/external/mexc/websocket/client.py

**Unused Imports:**
- Line 2: `from __future__ import annotations`

**Unused Definitions:**
- Line 14: Class `MEXCWebSocketClient`

### src/app/infrastructure/external/mexc/ws/__init__.py

**Unused Imports:**
- Line 2: `from src.app.infrastructure.external.mexc.ws.client import MEXCWebSocketClient`
- Line 3: `from src.app.infrastructure.external.mexc.ws.channels import diff_depth_stream`
- Line 3: `from src.app.infrastructure.external.mexc.ws.channels import partial_depth_stream`
- Line 3: `from src.app.infrastructure.external.mexc.ws.channels import trade_stream`
- Line 3: `from src.app.infrastructure.external.mexc.ws.channels import kline_stream`
- Line 3: `from src.app.infrastructure.external.mexc.ws.channels import account_update_stream`

### src/app/infrastructure/external/mexc/ws/ws_channels.py

**Unused Imports:**
- Line 4: `from __future__ import annotations`

**Unused Definitions:**
- Line 29: Function `build_protobuf_decoder`
- Line 42: Function `trade_stream`
- Line 48: Function `kline_stream`
- Line 54: Function `diff_depth_stream`
- Line 60: Function `partial_depth_stream`
- Line 66: Function `book_ticker_stream`
- Line 72: Function `book_ticker_batch_stream`
- Line 76: Function `mini_tickers_stream`

### src/app/infrastructure/external/mexc/ws/ws_client.py

**Unused Imports:**
- Line 4: `from __future__ import annotations`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import book_ticker_batch_stream`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import book_ticker_stream`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import build_protobuf_decoder`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import diff_depth_stream`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import kline_stream`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import mini_tickers_stream`
- Line 11: `from src.app.infrastructure.external.mexc.ws_channels import partial_depth_stream`

### src/app/infrastructure/external/mexc/ws/ws_core.py

**Unused Imports:**
- Line 2: `import websockets`
- Line 4: `from src.app.infrastructure.external.mexc.websocket.client import MEXCWebSocketClient`
- Line 4: `from src.app.infrastructure.external.mexc.websocket.client import WS_BASE`

### src/app/infrastructure/persistence/redis/__init__.py

**Unused Imports:**
- Line 2: `from client import RedisClient`
- Line 2: `from client import redis_client`

### src/app/infrastructure/persistence/redis/cache/__init__.py

**Unused Imports:**
- Line 2: `from balance import BalanceCacheMixin`
- Line 3: `from market import MarketCacheMixin`

### src/app/infrastructure/persistence/redis/cache/balance.py

**Unused Definitions:**
- Line 12: Class `BalanceCacheMixin`

### src/app/infrastructure/persistence/redis/cache/market.py

**Unused Definitions:**
- Line 14: Class `MarketCacheMixin`

### src/app/infrastructure/persistence/redis/connection/connect.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.persistence.redis import RedisClient`
- Line 5: `from src.app.infrastructure.persistence.redis import redis_client`

### src/app/infrastructure/persistence/redis/connection/pool.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.persistence.redis import RedisClient`
- Line 5: `from src.app.infrastructure.persistence.redis import redis_client`

### src/app/infrastructure/persistence/redis/repos/__init__.py

**Unused Imports:**
- Line 2: `from bot_status import BotStatusRepoMixin`
- Line 3: `from cost import CostRepoMixin`
- Line 4: `from mexc_raw import MexcRawRepoMixin`
- Line 5: `from position import PositionRepoMixin`
- Line 6: `from position_layers import PositionLayersRepoMixin`
- Line 7: `from price import PriceRepoMixin`
- Line 8: `from trade_counter import TradeCounterRepoMixin`
- Line 9: `from trade_history import TradeHistoryRepoMixin`

### src/app/infrastructure/persistence/redis/repos/account_balance_repo.py

**Unused Imports:**
- Line 7: `from src.app.infrastructure.persistence.redis.balance_cache import BalanceCacheMixin`

### src/app/infrastructure/persistence/redis/repos/bot_status.py

**Unused Definitions:**
- Line 9: Class `BotStatusRepoMixin`

### src/app/infrastructure/persistence/redis/repos/cost.py

**Unused Definitions:**
- Line 7: Class `CostRepoMixin`

### src/app/infrastructure/persistence/redis/repos/market_price_repo.py

**Unused Imports:**
- Line 7: `from src.app.infrastructure.persistence.redis.market_cache import MarketCacheMixin`

### src/app/infrastructure/persistence/redis/repos/mexc_raw.py

**Unused Definitions:**
- Line 6: Class `MexcRawRepoMixin`

### src/app/infrastructure/persistence/redis/repos/position.py

**Unused Definitions:**
- Line 8: Class `PositionRepoMixin`

### src/app/infrastructure/persistence/redis/repos/position_layers.py

**Unused Definitions:**
- Line 8: Class `PositionLayersRepoMixin`

### src/app/infrastructure/persistence/redis/repos/price.py

**Unused Definitions:**
- Line 9: Class `PriceRepoMixin`

### src/app/infrastructure/persistence/redis/repos/trade_counter.py

**Unused Definitions:**
- Line 8: Class `TradeCounterRepoMixin`

### src/app/infrastructure/persistence/redis/repos/trade_history.py

**Unused Definitions:**
- Line 8: Class `TradeHistoryRepoMixin`

### src/app/infrastructure/persistence/repos/__init__.py

**Unused Imports:**
- Line 3: `from src.app.infrastructure.persistence.repos.account import CostCalculator`
- Line 3: `from src.app.infrastructure.persistence.repos.account import CostRepository`
- Line 3: `from src.app.infrastructure.persistence.repos.account import PositionRepository`
- Line 8: `from src.app.infrastructure.persistence.repos.market import PriceRepository`
- Line 9: `from src.app.infrastructure.persistence.repos.trade import TradeRepository`

### src/app/infrastructure/persistence/repos/account/__init__.py

**Unused Imports:**
- Line 1: `from position_repository import PositionRepository`
- Line 2: `from cost_repository import CostRepository`

### src/app/infrastructure/persistence/repos/account/cost_calculator.py

**Unused Definitions:**
- Line 28: Function `summarize_cost_data`
- Line 58: Function `update_after_buy_values`
- Line 71: Function `update_after_sell_values`

### src/app/infrastructure/persistence/repos/account/cost_repository.py

**Unused Imports:**
- Line 2: `from cost_repository_core import CostRepository`

### src/app/infrastructure/persistence/repos/account/cost_repository_core.py

**Unused Definitions:**
- Line 17: Class `CostRepository`

### src/app/infrastructure/persistence/repos/account/position_repository.py

**Unused Imports:**
- Line 2: `from position_repository_core import PositionRepository`

### src/app/infrastructure/persistence/repos/account/position_repository_core.py

**Unused Definitions:**
- Line 11: Class `PositionRepository`

### src/app/infrastructure/persistence/repos/market/__init__.py

**Unused Imports:**
- Line 1: `from price_repository import PriceRepository`

### src/app/infrastructure/persistence/repos/market/price_repository.py

**Unused Imports:**
- Line 2: `from price_repository_core import PriceRepository`

### src/app/infrastructure/persistence/repos/market/price_repository_core.py

**Unused Definitions:**
- Line 11: Class `PriceRepository`

### src/app/infrastructure/persistence/repos/trade/__init__.py

**Unused Imports:**
- Line 1: `from trade_repository import TradeRepository`

### src/app/infrastructure/persistence/repos/trade/trade_repository.py

**Unused Imports:**
- Line 2: `from trade_repository_core import TradeRepository`

### src/app/infrastructure/persistence/repos/trade/trade_repository_core.py

**Unused Definitions:**
- Line 12: Class `TradeRepository`

### src/app/infrastructure/scheduler/cloud_tasks.py

**Unused Imports:**
- Line 5: `from src.app.interfaces.tasks.router import router`

### src/app/infrastructure/utils/__init__.py

**Unused Imports:**
- Line 6: `from type_safety import safe_float`
- Line 6: `from type_safety import safe_int`
- Line 7: `from decorators import handle_redis_errors`
- Line 7: `from decorators import handle_api_errors`
- Line 7: `from decorators import log_execution`
- Line 8: `from keys import RedisKeyBuilder`
- Line 8: `from keys import validate_symbol`
- Line 9: `from redis_data_manager import RedisDataManager`
- Line 10: `from metadata import create_metadata`

### src/app/infrastructure/utils/decorators.py

**Unused Definitions:**
- Line 12: Function `handle_redis_errors`
- Line 31: Function `handle_api_errors`
- Line 48: Function `log_execution`

### src/app/infrastructure/utils/keys.py

**Unused Imports:**
- Line 4: `from __future__ import annotations`

**Unused Definitions:**
- Line 51: Function `validate_symbol`

### src/app/infrastructure/utils/metadata.py

**Unused Definitions:**
- Line 8: Function `create_metadata`

### src/app/infrastructure/utils/redis_data_manager.py

**Unused Definitions:**
- Line 12: Class `RedisDataManager`

### src/app/infrastructure/utils/redis_helpers_core.py

**Unused Imports:**
- Line 5: `from redis_data_manager import RedisDataManager`
- Line 6: `from metadata import create_metadata`

### src/app/infrastructure/utils/type_safety.py

**Unused Definitions:**
- Line 7: Function `safe_float`
- Line 15: Function `safe_int`

### src/app/infrastructure/utils/utils_core.py

**Unused Imports:**
- Line 7: `from decorators import handle_redis_errors`
- Line 7: `from decorators import handle_api_errors`
- Line 7: `from decorators import log_execution`
- Line 8: `from keys import RedisKeyBuilder`
- Line 8: `from keys import validate_symbol`
- Line 9: `from type_safety import safe_float`
- Line 9: `from type_safety import safe_int`

### src/app/shared/clock.py

**Unused Definitions:**
- Line 7: Function `now_iso`

### src/app/shared/errors.py

**Unused Definitions:**
- Line 6: Class `ApplicationError`

### src/app/shared/ids.py

**Unused Definitions:**
- Line 7: Function `new_uuid`

### src/app/shared/typing.py

**Unused Imports:**
- Line 5: `from src.app.infrastructure.utils import safe_float`


## Recommendations

### Immediate Actions

1. **Remove Unused Imports** - Clean up import statements
2. **Review Unused Definitions** - Verify these are not used elsewhere
3. **Update Tests** - Ensure removal doesn't break tests

### Safe Removal Process

1. Verify with `git grep <name>` that the code is truly unused
2. Check if exported in `__init__.py` or `__all__`
3. Run full test suite after removal
4. Commit removals separately for easy rollback

---

*Generated by Dead Code Analyzer*