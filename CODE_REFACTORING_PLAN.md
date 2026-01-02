# Code Refactoring Plan: Files Over 4000 Characters

## Executive Summary

**Goal**: Refactor 19 Python files exceeding 4000 characters to improve maintainability and follow single responsibility principle.

**Total Files**: 19 files identified (ranging from 4058 to 12634 characters)

**Approach**: Incremental refactoring with testing after each change to ensure functionality remains intact.

## Files Identified (Sorted by Size)

| File | Size (chars) | Lines | Priority |
|------|--------------|-------|----------|
| src/app/domain/risk/limits.py | 12,634 | 400 | High |
| src/app/application/trading/services/trading/intelligent_rebalance_service.py | 12,445 | 343 | High |
| src/app/application/trading/services/trading/trading_service_core.py | 12,051 | 323 | High |
| src/app/domain/strategies/trading_strategy.py | 9,873 | - | Medium |
| src/app/interfaces/tasks/task_15_min_job.py | 6,429 | - | Medium |
| src/app/interfaces/http/account.py | 6,032 | - | Medium |
| src/app/infrastructure/persistence/redis/cache/market.py | 6,014 | - | Low |
| src/app/interfaces/http/market.py | 6,001 | - | Low |
| src/app/infrastructure/config/settings.py | 5,809 | - | Low |
| src/app/interfaces/tasks/intelligent_rebalance.py | 5,653 | - | Low |
| src/app/infrastructure/persistence/redis/cache/balance.py | 5,644 | - | Low |
| src/app/interfaces/http/sub_account.py | 5,553 | - | Low |
| src/app/application/trading/services/trading/trading_workflow.py | 5,313 | - | Low |
| src/app/infrastructure/persistence/repos/trade/trade_repository_core.py | 5,038 | - | Low |
| src/app/interfaces/tasks/rebalance.py | 4,727 | - | Low |
| src/app/application/trading/services/market/market_service_core.py | 4,463 | - | Low |
| src/app/application/trading/services/trading/rebalance_service.py | 4,396 | - | Low |
| src/app/infrastructure/utils/redis_data_manager.py | 4,164 | - | Low |
| src/app/infrastructure/persistence/redis/client.py | 4,058 | - | Low |

## Phase 1: intelligent_rebalance_service.py (Priority: High)

### Current Structure
- Single class with 343 lines
- Contains: MA calculation, signal detection, rebalance logic, cost tracking

### Proposed Refactoring

#### 1.1 Create indicators/ma_calculator.py
**Extract**: `_calculate_ma_indicators()` method (lines 88-153)
**New Module**: `src/app/application/trading/services/indicators/ma_calculator.py`

```python
"""Moving Average calculator for technical analysis."""

from typing import Any, Dict, List
from src.app.infrastructure.utils import safe_float

class MACalculator:
    """Calculate moving averages from price data."""
    
    def __init__(self, short_period: int = 7, long_period: int = 25):
        self.short_period = short_period
        self.long_period = long_period
    
    async def calculate_from_klines(
        self, klines: List[List], symbol: str
    ) -> Dict[str, Any]:
        """Calculate MA indicators from kline data."""
        # Implementation from _calculate_ma_indicators
        ...
```

**Benefits**:
- Reusable for other strategies
- Independently testable
- Clear single responsibility
- Reduces main file by ~65 lines

#### 1.2 Create indicators/signal_detector.py
**Extract**: Signal detection logic (lines 131-136)
**New Module**: `src/app/application/trading/services/indicators/signal_detector.py`

```python
"""Trading signal detection from technical indicators."""

from typing import Literal

SignalType = Literal["GOLDEN_CROSS", "DEATH_CROSS", "NEUTRAL", "UNKNOWN"]

class SignalDetector:
    """Detect trading signals from MA crossovers."""
    
    @staticmethod
    def detect_ma_cross(ma_short: float, ma_long: float) -> SignalType:
        """Detect golden cross or death cross signals."""
        if ma_short > ma_long:
            return "GOLDEN_CROSS"  # Bullish
        elif ma_short < ma_long:
            return "DEATH_CROSS"   # Bearish
        else:
            return "NEUTRAL"
```

**Benefits**:
- Extensible for other signal types
- Simple, testable logic
- Type-safe with Literal types

#### 1.3 Create position/cost_tracker.py
**Extract**: `_get_cost_basis()` method (lines 310-330)
**New Module**: `src/app/application/trading/services/position/cost_tracker.py`

```python
"""Cost basis tracking for positions."""

from typing import Optional
from src.app.infrastructure.utils import safe_float

class CostTracker:
    """Track and retrieve cost basis for positions."""
    
    def __init__(self, redis_client=None, default_cost: float = 0.05):
        self.redis = redis_client
        self.default_cost = default_cost
    
    async def get_cost_basis(self, symbol: str, quantity: float) -> float:
        """Get cost basis from Redis or return default."""
        # Implementation from _get_cost_basis
        ...
```

**Benefits**:
- Separation of cost tracking concern
- Reduces main file by ~20 lines
- Easier to extend with persistence logic

#### 1.4 Update intelligent_rebalance_service.py
**Result**: Main service becomes a coordinator
- Delegates MA calculation to MACalculator
- Delegates signal detection to SignalDetector
- Delegates cost tracking to CostTracker
- Keeps orchestration logic (generate_plan, compute_plan)
- **Expected final size**: ~180 lines (~6000 chars)

### Implementation Steps

1. **Create new module structure** (Complexity: 2/10)
   ```bash
   mkdir -p src/app/application/trading/services/indicators
   mkdir -p src/app/application/trading/services/position
   touch src/app/application/trading/services/indicators/__init__.py
   touch src/app/application/trading/services/position/__init__.py
   ```

2. **Extract MACalculator** (Complexity: 4/10)
   - Create ma_calculator.py with extracted logic
   - Add unit tests for MA calculation
   - Verify calculations match original

3. **Extract SignalDetector** (Complexity: 2/10)
   - Create signal_detector.py with extracted logic
   - Add unit tests for signal detection
   - Simple, pure logic

4. **Extract CostTracker** (Complexity: 3/10)
   - Create cost_tracker.py with extracted logic
   - Add unit tests with mocked Redis
   - Handle fallback cases

5. **Refactor main service** (Complexity: 5/10)
   - Update imports
   - Initialize new components in __init__
   - Update _calculate_ma_indicators to delegate
   - Update _get_cost_basis to delegate
   - Update compute_plan to use new components
   - Verify all tests pass

6. **Test end-to-end** (Complexity: 3/10)
   - Run existing intelligent_rebalance tests
   - Test /tasks/rebalance/intelligent endpoint
   - Verify MA calculation accuracy
   - Verify signal detection works
   - Verify cost tracking works

## Phase 2: limits.py (Priority: High)

### Current Structure
- Single RiskManager class with 400 lines
- Contains multiple independent risk validations

### Proposed Refactoring

#### 2.1 Create risk validators structure
```
src/app/domain/risk/
├── limits.py (main coordinator)
├── validators/
│   ├── __init__.py
│   ├── daily_limit.py
│   ├── interval.py
│   ├── position.py
│   └── reserve.py
```

#### 2.2 Extract validators

**validators/daily_limit.py**:
- Daily trade count validation
- Track trades per day
- Enforce MAX_DAILY_TRADES limit

**validators/interval.py**:
- Trade interval validation
- Enforce MIN_TRADE_INTERVAL
- Prevent rapid-fire trading

**validators/position.py**:
- Core position protection
- Calculate tradeable positions
- Validate sell quantities

**validators/reserve.py**:
- USDT reserve validation
- Calculate available USDT
- Validate buy quantities

#### 2.3 Update RiskManager
- Becomes coordinator of validators
- Each validator is independently testable
- **Expected final size**: ~150 lines (~5000 chars)

### Implementation Steps

1. Create validator structure (Complexity: 2/10)
2. Extract daily_limit validator (Complexity: 4/10)
3. Extract interval validator (Complexity: 4/10)
4. Extract position validator (Complexity: 5/10)
5. Extract reserve validator (Complexity: 4/10)
6. Refactor RiskManager (Complexity: 5/10)
7. Test all validators (Complexity: 4/10)

## Phase 3: trading_service_core.py (Priority: High)

### Current Structure
- 323 lines, 12051 characters
- Core trading functionality

### Analysis Needed
- Examine file structure
- Identify natural split points
- Create extraction plan

### Proposed Approach
- Extract helper methods to separate modules
- Keep main trading logic in core
- Target: <4000 characters per file

## Phase 4: Remaining Files (Priority: Medium/Low)

### Files to Address
- trading_strategy.py (9873 chars)
- task_15_min_job.py (6429 chars)
- account.py (6032 chars)
- Others as time permits

### Strategy
- Quick wins: Extract large helper methods
- Focus on improving testability
- Aim for <4000 chars where possible

## Implementation Timeline

### Phase 1: intelligent_rebalance_service.py
- Estimated Time: 2-3 hours
- Steps: 6 tasks
- Testing: Comprehensive

### Phase 2: limits.py
- Estimated Time: 2-3 hours
- Steps: 7 tasks
- Testing: Per validator

### Phase 3: trading_service_core.py
- Estimated Time: 2-3 hours
- Analysis + Implementation

### Phase 4: Remaining files
- Estimated Time: 3-4 hours
- Quick improvements

### Total: 9-13 hours

## Success Criteria

✅ **Primary Goals**:
- All refactored files under 4000 characters (or well-justified exceptions)
- All existing tests pass
- No functionality regression
- Improved code organization

✅ **Secondary Goals**:
- Better test coverage
- Improved maintainability
- Clear separation of concerns
- Reusable components

## Risk Mitigation

1. **Incremental Changes**: Refactor one file at a time
2. **Test After Each Step**: Run tests after every extraction
3. **Keep Backups**: Git history preserves original versions
4. **Backward Compatibility**: Maintain all public interfaces
5. **Documentation**: Update docstrings and comments

## Testing Strategy

### Unit Tests
- Test extracted components independently
- Mock dependencies
- Cover edge cases

### Integration Tests
- Test refactored services end-to-end
- Verify API endpoints work
- Check Redis integration

### Regression Tests
- Run full test suite after each phase
- Manual testing of critical paths
- Performance verification

## Notes

- This plan prioritizes the largest files first
- Each phase is independent and can be executed separately
- Testing is critical after each change
- Code review recommended before merging
- Documentation updates needed for extracted modules

## Execution Status

- [ ] Phase 1: intelligent_rebalance_service.py
- [ ] Phase 2: limits.py
- [ ] Phase 3: trading_service_core.py
- [ ] Phase 4: Remaining files
- [ ] Final validation and testing

---

**Created**: 2026-01-02
**Last Updated**: 2026-01-02
**Status**: Planning Complete, Ready for Implementation
