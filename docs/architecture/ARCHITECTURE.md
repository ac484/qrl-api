# QRL Trading API - Clean Architecture Refactoring

## Overview

This document describes the architectural refactoring of the QRL Trading API to follow clean architecture principles, improve maintainability, and reduce code complexity.

## Problem Statement

### Original Issues

1. **Large Monolithic Files**
   - `main.py`: 1162 lines - Mixed routing, business logic, validation
   - `redis_client.py`: 670 lines - Multiple responsibilities
   - `mexc_client.py`: 761 lines - Mixed SPOT and BROKER logic
   - `bot.py`: 464 lines - Tightly coupled dependencies

2. **Violations of Single Responsibility Principle (SRP)**
   - Files handling I/O, business logic, validation, and data transformation
   - No clear separation between API, Domain, and Infrastructure layers

3. **High Coupling**
   - Direct dependencies between modules
   - Hard-coded singletons
   - Difficult to test and extend

4. **Code Duplication**
   - Multiple validation scripts
   - Repeated error handling patterns
   - Duplicated data serialization logic

## Architecture Solution

### Clean Architecture Layers

```
┌─────────────────────────────────────────┐
│          API Layer (FastAPI)            │
│  - HTTP endpoints                       │
│  - Request/Response handling            │
│  - Routes: market, account, bot, etc.   │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│        Application Services             │
│  - Orchestration                        │
│  - Use case coordination                │
└──────────────┬──────────────────────────┘
               │ depends on
┌──────────────▼──────────────────────────┐
│         Domain Layer                    │
│  - Business logic                       │
│  - Trading strategy                     │
│  - Risk management                      │
│  - Position management                  │
│  - Domain interfaces (abstractions)     │
└──────────────┬──────────────────────────┘
               │ implemented by
┌──────────────▼──────────────────────────┐
│     Infrastructure Layer                │
│  - Repositories (Redis)                 │
│  - External services (MEXC API)         │
│  - Adapters                             │
└─────────────────────────────────────────┘
```

### Directory Structure

```
qrl-api/
├── api/                    # API Routes (Presentation Layer)
│   ├── __init__.py
│   ├── market_routes.py    # Market data endpoints
│   ├── account_routes.py   # Account management
│   ├── bot_routes.py       # Trading bot control
│   ├── sub_account_routes.py
│   └── cloud_task_routes.py
│
├── domain/                 # Domain Layer (Business Logic)
│   ├── __init__.py
│   ├── interfaces/         # Abstract interfaces for DIP
│   │   ├── account.py
│   │   ├── cost.py
│   │   ├── market.py
│   │   ├── position.py
│   │   ├── price.py
│   │   └── trade.py
│   ├── trading_strategy/   # Pure strategy logic
│   │   └── core.py
│   ├── risk_manager/       # Risk control rules
│   │   └── core.py
│   └── position_manager/   # Position calculations
│       └── core.py
│
├── services/               # Application Services
│   ├── __init__.py
│   ├── trading_service.py  # Trading orchestration (wrapper)
│   └── market_service.py   # Market data operations (wrapper)
│
├── repositories/           # Data Access Layer
│   ├── __init__.py
│   ├── position_repository.py  # Wrapper
│   ├── price_repository.py     # Wrapper
│   ├── trade_repository.py     # Wrapper
│   └── cost_repository.py      # Wrapper
│
├── models/                 # Data Models
│   ├── __init__.py
│   ├── market_data.py
│   └── account_data.py
│
├── main.py                 # Application entry point (minimal)
├── config.py               # Configuration management wrapper
└── bot.py                  # Legacy bot (to be refactored)
```

## Domain Layer Design

### Interfaces (Dependency Inversion Principle)

**File**: `domain/interfaces/`

Defines abstract interfaces to decouple domain logic from infrastructure:

- `IMarketDataProvider` - Market data access
- `IAccountDataProvider` - Account operations
- `IPositionRepository` - Position storage
- `IPriceRepository` - Price data storage
- `ITradeRepository` - Trade history
- `ICostRepository` - Cost tracking

### Trading Strategy

**File**: `domain/trading_strategy/core.py`

Pure business logic for trading signal generation:

```python
class TradingStrategy:
    """Moving Average Crossover Strategy"""
    
    def generate_signal(price, short_prices, long_prices, avg_cost) -> str:
        """Returns: BUY, SELL, or HOLD"""
```

**Key Features**:
- No infrastructure dependencies
- Pure functions with clear inputs/outputs
- Easily testable
- Configurable parameters

### Risk Manager

**File**: `domain/risk_manager/core.py`

Risk control rules and validation:

```python
class RiskManager:
    """Risk control for trading operations"""
    
    def check_daily_limit(daily_trades) -> Dict
    def check_trade_interval(last_trade_time) -> Dict
    def check_sell_protection(position_layers) -> Dict
    def check_buy_protection(usdt_balance) -> Dict
    def check_all_risks(...) -> Dict
```

**Key Features**:
- Centralized risk rules
- Clear pass/fail responses
- Configurable limits
- No side effects

### Position Manager

**File**: `domain/position_manager/core.py`

Position sizing and P&L calculations:

```python
class PositionManager:
    """Position sizing and cost calculations"""
    
    def calculate_buy_quantity(usdt_balance, price) -> Dict
    def calculate_sell_quantity(total_qrl, core_qrl) -> Dict
    def calculate_new_average_cost(...) -> Dict
    def calculate_pnl_after_sell(...) -> Dict
```

**Key Features**:
- Pure calculation logic
- No database or API dependencies
- Deterministic results
- Easy to unit test

## API Layer Refactoring

### Market Routes

**File**: `api/market_routes.py`

Extracted market data endpoints:
- `GET /market/ticker/{symbol}`
- `GET /market/price/{symbol}`
- `GET /market/orderbook/{symbol}`
- `GET /market/trades/{symbol}`
- `GET /market/klines/{symbol}`

**Benefits**:
- Single responsibility (market data only)
- Reusable across applications
- Easier to test
- Clear API boundaries

### Account Routes

**File**: `api/account_routes.py`

Account management endpoints:
- `GET /account/balance` - Real-time from MEXC
- `GET /account/balance/redis` - Cached data

**Benefits**:
- Separation of account vs. market concerns
- Clear data source (API vs. cache)
- Independent testing

## Design Principles Applied

### 1. Single Responsibility Principle (SRP)
- Each module has one reason to change
- `trading_strategy/core.py` - Only changes when strategy logic changes
- `risk_manager/core.py` - Only changes when risk rules change
- `market_routes.py` - Only changes when API contracts change

### 2. Dependency Inversion Principle (DIP)
- Domain layer defines interfaces
- Infrastructure implements interfaces
- High-level modules don't depend on low-level details

### 3. Separation of Concerns
- API layer: HTTP handling
- Domain layer: Business rules
- Infrastructure layer: External systems

### 4. Open/Closed Principle
- Domain logic is closed for modification
- Extension through new implementations of interfaces
- Easy to add new trading strategies without changing existing code

### 5. Occam's Razor
- Simplest solution that works
- No premature optimization
- Clear, readable code over clever tricks

## Benefits Achieved

### Maintainability
- **Before**: Navigate 1000+ lines to find business logic
- **After**: Business logic in focused 100-200 line files
- Clear module boundaries

### Testability
- **Before**: Hard to test without mocking Redis and MEXC
- **After**: Domain logic tested independently
- Pure functions = deterministic tests

### Scalability
- **Before**: Adding features requires changing multiple files
- **After**: New features = new modules
- Existing code untouched

### Code Reuse
- **Before**: Copy-paste similar logic
- **After**: Reusable domain services
- Clear interfaces for different implementations

### Reduced Coupling
- **Before**: Direct dependencies everywhere
- **After**: Depend on abstractions
- Components evolve independently

## Migration Path

### Phase 1: Foundation ✅
- Create directory structure
- Define domain interfaces
- Extract core business logic

### Phase 2: API Refactoring (In Progress)
- Extract route modules
- Simplify main.py
- Maintain backward compatibility

### Phase 3: Repository Pattern
- Create repository implementations
- Wrap existing Redis client
- No behavior changes

### Phase 4: Service Layer
- Orchestrate domain logic
- Handle cross-cutting concerns
- Coordinate repositories

### Phase 5: Cleanup
- Remove code duplication
- Consolidate validation
- Update tests

## Testing Strategy

### Unit Tests
- Test domain logic independently
- No infrastructure dependencies
- Fast, deterministic tests

### Integration Tests
- Test API endpoints
- Use test doubles for external services
- Verify correct integration

### Contract Tests
- Ensure backward compatibility
- API contracts unchanged
- Existing clients work

## Performance Considerations

### No Performance Degradation
- Domain extraction = code organization only
- Same Redis caching strategy
- Same MEXC API calls
- Identical runtime behavior

### Improved Monitoring
- Clear module boundaries = better logging
- Easier to add metrics
- Simpler debugging

## Future Enhancements

### Dependency Injection Container
- Remove hard-coded singletons
- Configurable dependencies
- Easier testing

### Event-Driven Architecture
- Domain events for trading actions
- Audit log via events
- Decoupled notifications

### Strategy Plugin System
- Load strategies dynamically
- A/B test different strategies
- User-configurable rules

## Conclusion

This architectural refactoring transforms a monolithic codebase into a clean, maintainable system following industry best practices:

1. **Separation of Concerns**: Clear layer boundaries
2. **Single Responsibility**: Each module has one job
3. **Dependency Inversion**: Depend on abstractions
4. **Testability**: Pure business logic
5. **Maintainability**: Easy to understand and change

The refactoring is incremental, maintaining backward compatibility while progressively improving code quality.

## References

- Clean Architecture (Robert C. Martin)
- Domain-Driven Design (Eric Evans)
- SOLID Principles
- Hexagonal Architecture (Ports and Adapters)
