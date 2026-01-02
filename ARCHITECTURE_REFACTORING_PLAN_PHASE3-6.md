# Architecture Refactoring Plan: Phase 3-6

## Executive Summary

This document outlines the refactoring strategy for 17 remaining files >4000 chars, addressing fundamental architectural issues of responsibility mixing and insufficient abstraction boundaries.

## Architectural Principles

### Core Principles
1. **Strict Layer Separation**: Application (orchestration) → Domain (policy) → Infrastructure (execution)
2. **Single Responsibility**: Each module has ONE clear reason to change
3. **< 4000 Chars Rule**: Any file exceeding this indicates architectural smell
4. **Delegation Pattern**: Services coordinate, specialists execute

### Responsibility Matrix

| Layer | Responsibility | Examples |
|-------|---------------|----------|
| Application | Orchestrate workflow | TradingService, RebalanceService |
| Domain | Define business rules | TradingStrategy, RiskManager |
| Infrastructure | Execute technical tasks | OrderExecutor, StateManager |

##Phase 3: Core Trading Services (12-16 hours)

### 3.1: trading_service_core.py Refactoring

**Current State** (12,051 chars):
- Mixes orchestration + execution + state management
- Violates single responsibility principle
- Hard to test individual concerns

**Target Architecture**:
```
trading_service_core.py (4,500 chars) - ORCHESTRATION
├── executors/
│   ├── order_executor.py (2,800 chars) - EXECUTION
│   └── state_manager.py (2,500 chars) - INFRASTRUCTURE
```

**Extraction Plan**:

#### order_executor.py (2,800 chars)
```python
"""Order execution - pure MEXC API interaction"""
class OrderExecutor:
    def __init__(self, mexc_client):
        self.mexc = mexc_client
    
    async def execute_market_order(self, action: str, quantity: float, symbol: str):
        """Place market order - EXECUTION ONLY"""
        self._validate_params(action, quantity)
        if action == "BUY":
            return await self._execute_buy(symbol, quantity)
        return await self._execute_sell(symbol, quantity)
    
    async def _execute_buy(self, symbol: str, qty: float):
        return await self.mexc.place_market_order(
            symbol=symbol, side="BUY", quantity=qty
        )
    
    async def _execute_sell(self, symbol: str, qty: float):
        return await self.mexc.place_market_order(
            symbol=symbol, side="SELL", quantity=qty
        )
```

#### state_manager.py (2,500 chars)
```python
"""State persistence - pure Redis interaction"""
class StateManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def save_bot_state(self, state: Dict):
        """Persist trading state - INFRASTRUCTURE ONLY"""
        serialized = self._serialize(state)
        await self.redis.set("bot:state", serialized)
    
    async def load_bot_state(self) -> Dict:
        """Retrieve trading state"""
        data = await self.redis.get("bot:state")
        return self._deserialize(data) if data else {}
```

#### trading_service_core.py (4,500 chars) - REFACTORED
```python
"""Trading orchestration - pure workflow coordination"""
class TradingService:
    def __init__(self, ..., order_executor, state_manager):
        self.order_executor = order_executor
        self.state_manager = state_manager
        # ... other dependencies
    
    async def execute_trade_decision(self):
        """Orchestrate 6-phase workflow - COORDINATION ONLY"""
        # Phase 1: Load state (delegate)
        state = await self.state_manager.load_bot_state()
        
        # Phase 2-5: Generate decision (delegate to workflow)
        decision = await self.workflow.generate_decision()
        
        # Phase 6: Execute order (delegate)
        if decision['action'] in ['BUY', 'SELL']:
            result = await self.order_executor.execute_market_order(
                decision['action'], decision['quantity'], "QRLUSDT"
            )
        
        # Save state (delegate)
        await self.state_manager.save_bot_state(new_state)
        return result
```

**Benefits**:
- OrderExecutor: Testable independently, reusable
- StateManager: Testable independently, reusable
- TradingService: Clear orchestration logic only

### 3.2: trading_strategy.py Refactoring

**Current State** (9,873 chars):
- Mixes policy + MA calculation + cost filtering
- Domain logic entangled with computations

**Target Architecture**:
```
trading_strategy.py (3,800 chars) - POLICY
├── indicators/
│   └── ma_signal_generator.py (3,200 chars) - COMPUTATION
└── filters/
    └── cost_filter.py (2,100 chars) - BUSINESS RULE
```

**Extraction Plan**:

#### ma_signal_generator.py (3,200 chars)
```python
"""MA signal generation - pure mathematical computation"""
class MASignalGenerator:
    def __init__(self, short_period: int = 7, long_period: int = 25):
        self.short_period = short_period
        self.long_period = long_period
    
    def generate_signal(self, prices: List[float]) -> Dict:
        """Calculate MA and detect crossover - COMPUTATION ONLY"""
        ma_short = self.calculate_ma(prices, self.short_period)
        ma_long = self.calculate_ma(prices, self.long_period)
        
        signal = "NEUTRAL"
        if ma_short > ma_long:
            signal = "GOLDEN_CROSS"  # Bullish
        elif ma_short < ma_long:
            signal = "DEATH_CROSS"   # Bearish
        
        return {
            "ma_short": ma_short,
            "ma_long": ma_long,
            "signal": signal
        }
    
    def calculate_ma(self, prices: List[float], period: int) -> float:
        """Simple Moving Average calculation"""
        return sum(prices[-period:]) / period
```

#### cost_filter.py (2,100 chars)
```python
"""Cost-based filtering - business rule application"""
class CostFilter:
    def __init__(self, buy_threshold: float = 1.00, sell_threshold: float = 1.03):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold
    
    def should_buy(self, current_price: float, avg_cost: float) -> bool:
        """Apply buy filter - BUSINESS RULE ONLY"""
        return current_price <= avg_cost * self.buy_threshold
    
    def should_sell(self, current_price: float, avg_cost: float) -> bool:
        """Apply sell filter - minimum 3% profit"""
        return current_price >= avg_cost * self.sell_threshold
```

#### trading_strategy.py (3,800 chars) - REFACTORED
```python
"""Trading strategy - pure policy definition"""
class TradingStrategy:
    def __init__(self, ma_generator, cost_filter):
        self.ma_generator = ma_generator
        self.cost_filter = cost_filter
    
    def generate_signal(self, prices: List[float], current_price: float, avg_cost: float) -> str:
        """Define trading policy - POLICY ONLY"""
        # Get MA signal (delegate computation)
        ma_signal = self.ma_generator.generate_signal(prices)
        
        # Apply policy rules
        if ma_signal["signal"] == "GOLDEN_CROSS":
            if self.cost_filter.should_buy(current_price, avg_cost):
                return "BUY"
        
        elif ma_signal["signal"] == "DEATH_CROSS":
            if self.cost_filter.should_sell(current_price, avg_cost):
                return "SELL"
        
        return "HOLD"
```

### 3.3: intelligent_rebalance_service.py Refactoring

**Current State** (10,915 chars):
- Mixes orchestration + tier allocation + validation

**Target Architecture**:
```
intelligent_rebalance_service.py (3,900 chars) - ORCHESTRATION
├── domain/
│   └── tier_allocator.py (2,400 chars) - BUSINESS LOGIC
└── validators/
    └── plan_validator.py (2,200 chars) - VALIDATION
```

## Phase 4: Task Interfaces (6-8 hours)

### Pattern: Extract Executors and Formatters

**Common Issues**:
- Task endpoints mix request handling + execution + formatting
- Violates single responsibility

**Solution Pattern**:
```
task_endpoint.py (3,200 chars) - API HANDLER
├── executors/task_executor.py (2,800 chars) - EXECUTION
└── formatters/response_formatter.py (2,100 chars) - FORMATTING
```

### Files to Refactor:
1. task_15_min_job.py (6,429 → 3,200 chars)
2. intelligent_rebalance.py (5,653 → 3,200 chars)
3. rebalance.py (4,727 → 2,900 chars)

## Phase 5: HTTP Interfaces (8-10 hours)

### Pattern: Extract Handlers and Builders

**Common Issues**:
- HTTP endpoints mix routing + validation + business logic + formatting
- Hard to test individual concerns

**Solution Pattern**:
```
endpoint.py (3,500 chars) - ROUTING
├── handlers/request_handler.py (2,500 chars) - REQUEST PROCESSING
└── builders/response_builder.py (2,000 chars) - RESPONSE CONSTRUCTION
```

### Files to Refactor:
1. account.py (6,032 → 3,500 chars)
2. market.py (6,001 → 3,500 chars)
3. sub_account.py (5,553 → 3,500 chars)

## Phase 6: Infrastructure (8-10 hours)

### Pattern: Extract Transformers and Managers

**Files to Refactor**:
1. market.py (cache) (6,014 → 3,500 chars)
2. balance.py (cache) (5,644 → 3,500 chars)
3. settings.py (5,809 → 3,500 chars)
4. trade_repository_core.py (5,038 → 3,500 chars)
5. trading_workflow.py (5,313 → 3,800 chars)
6. market_service_core.py (4,463 → 3,200 chars)
7. rebalance_service.py (4,396 → 3,000 chars)
8. redis_data_manager.py (4,164 → 3,000 chars)
9. client.py (4,058 → 3,000 chars)

## Validation Checklist

After each refactoring:
- [ ] File size < 4000 chars
- [ ] Single clear responsibility
- [ ] No layer mixing
- [ ] Tests pass
- [ ] App starts
- [ ] API unchanged

## Timeline

| Phase | Duration | Priority |
|-------|----------|----------|
| Phase 3 | 12-16h | CRITICAL |
| Phase 4 | 6-8h | HIGH |
| Phase 5 | 8-10h | MEDIUM |
| Phase 6 | 8-10h | LOW |
| **Total** | **34-44h** | 5-6 weeks |

## Success Metrics

- ✅ All files < 4000 chars
- ✅ Clear responsibility boundaries
- ✅ No orchestration/policy/execution mixing
- ✅ 100% test pass rate
- ✅ Application runs successfully
- ✅ Backward compatible APIs
