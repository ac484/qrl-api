# Code Refactoring Execution Plan (Phases 3-6)

## Overview

Detailed implementation plan for completing refactoring of remaining files. Each phase includes specific extraction steps, validation procedures, and rollback plans.

---

## Phase 3: Core Trading Services (HIGHEST PRIORITY)

**Timeline**: 8-12 hours
**Files**: 3
**Risk**: Medium (core business logic)

### 3.1: trading_service_core.py (12,051 → 6,500 chars)

**Step 1: Create OrderExecutor** (2,500 chars)
```python
# src/app/application/trading/services/executors/order_executor.py

class OrderExecutor:
    def __init__(self, mexc_client, trade_repo):
        self.mexc = mexc_client
        self.trade_repo = trade_repo
    
    async def execute_market_order(self, symbol, action, quantity):
        """Execute market order on MEXC"""
        if action == "BUY":
            return await self._execute_buy(symbol, quantity)
        elif action == "SELL":
            return await self._execute_sell(symbol, quantity)
        raise ValueError(f"Invalid action: {action}")
    
    async def _execute_buy(self, symbol, quantity):
        """Place BUY market order"""
        order = await self.mexc.place_market_order(
            symbol=symbol, side="BUY", quantity=quantity
        )
        await self._record_execution(symbol, "BUY", quantity, order)
        return order
    
    async def _execute_sell(self, symbol, quantity):
        """Place SELL market order"""
        order = await self.mexc.place_market_order(
            symbol=symbol, side="SELL", quantity=quantity
        )
        await self._record_execution(symbol, "SELL", quantity, order)
        return order
    
    async def _record_execution(self, symbol, side, quantity, order):
        """Record trade execution in repository"""
        await self.trade_repo.increment_daily_trades()
        await self.trade_repo.set_last_trade_time(datetime.now().timestamp())
        await self.trade_repo.add_trade_record({
            "symbol": symbol,
            "side": side,
            "quantity": quantity,
            "order_id": order.get("orderId"),
            "timestamp": datetime.now().isoformat(),
        })
```

**Step 2: Create StateManager** (2,000 chars)
```python
# src/app/application/trading/services/executors/state_manager.py

class StateManager:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    async def get_bot_status(self):
        """Get current bot running status"""
        status = await self.redis.get_bot_status()
        running_flag = status.get("running")
        return running_flag if running_flag is not None else True
    
    async def start_bot(self):
        """Start bot and persist state"""
        await self.redis.set_bot_status({
            "running": True,
            "started_at": datetime.now().isoformat()
        })
    
    async def stop_bot(self):
        """Stop bot and persist state"""
        await self.redis.set_bot_status({
            "running": False,
            "stopped_at": datetime.now().isoformat()
        })
    
    async def save_execution_result(self, result):
        """Save trade execution result"""
        await self.redis.set_last_execution(result)
```

**Step 3: Refactor TradingService** (6,500 chars)
- Update __init__() to inject OrderExecutor and StateManager
- Replace direct order execution with executor.execute_market_order()
- Replace direct state management with state_manager methods
- Keep orchestration logic in execute_trade_decision()

**Validation**:
```bash
# Syntax check
python -m py_compile src/app/application/trading/services/executors/*.py
python -m py_compile src/app/application/trading/services/trading/trading_service_core.py

# Import check  
python -c "from src.app.application.trading.services.trading.trading_service_core import TradingService"

# Run tests
pytest tests/test_trading_service.py -v

# Start application
python main.py  # Verify startup
```

---

### 3.2: trading_strategy.py (9,873 → 5,500 chars)

**Step 1: Create MASignalGenerator** (2,800 chars)
```python
# src/app/domain/strategies/signals/ma_signal_generator.py

class MASignalGenerator:
    def __init__(self, ma_short_period=7, ma_long_period=25):
        self.ma_short_period = ma_short_period
        self.ma_long_period = ma_long_period
    
    def generate_signal(self, prices, current_price, avg_cost):
        """Generate BUY/SELL/HOLD signal from MA crossover"""
        if len(prices) < self.ma_long_period:
            return {"action": "HOLD", "reason": "Insufficient price data"}
        
        ma_short = self._calculate_ma(prices, self.ma_short_period)
        ma_long = self._calculate_ma(prices, self.ma_long_period)
        
        # Detect crossover
        if self._is_golden_cross(ma_short, ma_long):
            if current_price <= avg_cost:
                return {
                    "action": "BUY",
                    "signal": "GOLDEN_CROSS",
                    "strength": self._calculate_strength(ma_short, ma_long),
                    "ma_short": ma_short,
                    "ma_long": ma_long
                }
        
        elif self._is_death_cross(ma_short, ma_long):
            if current_price >= avg_cost * 1.03:
                return {
                    "action": "SELL",
                    "signal": "DEATH_CROSS",
                    "strength": self._calculate_strength(ma_short, ma_long),
                    "ma_short": ma_short,
                    "ma_long": ma_long
                }
        
        return {"action": "HOLD", "ma_short": ma_short, "ma_long": ma_long}
    
    def _calculate_ma(self, prices, period):
        """Calculate simple moving average"""
        return sum(prices[-period:]) / period
    
    def _is_golden_cross(self, ma_short, ma_long):
        """Check for golden cross (bullish)"""
        return ma_short > ma_long
    
    def _is_death_cross(self, ma_short, ma_long):
        """Check for death cross (bearish)"""
        return ma_short < ma_long
    
    def _calculate_strength(self, ma_short, ma_long):
        """Calculate signal strength percentage"""
        return abs((ma_short - ma_long) / ma_long * 100)
```

**Step 2: Create CostFilter** (1,600 chars)
```python
# src/app/domain/strategies/filters/cost_filter.py

class CostFilter:
    def __init__(self, min_profit_pct=0.03):
        self.min_profit_pct = min_profit_pct
    
    def should_buy(self, current_price, avg_cost):
        """Check if price is suitable for buying"""
        return current_price <= avg_cost
    
    def should_sell(self, current_price, avg_cost):
        """Check if price meets minimum profit threshold"""
        return current_price >= avg_cost * (1 + self.min_profit_pct)
    
    def calculate_profit_pct(self, current_price, avg_cost):
        """Calculate profit percentage"""
        return (current_price - avg_cost) / avg_cost * 100
    
    def is_profitable(self, current_price, avg_cost):
        """Check if current price is profitable"""
        return current_price > avg_cost
```

**Step 3: Refactor TradingStrategy** (5,500 chars)
- Keep public API methods
- Delegate to MASignalGenerator for signal generation
- Delegate to CostFilter for price validation
- Maintain backward compatibility

---

### 3.3: intelligent_rebalance_service.py (10,915 → 7,000 chars)

**Step 1: Create TierAllocator** (2,000 chars)
```python
# src/app/application/trading/services/position/tier_allocator.py

class TierAllocator:
    def __init__(self, core_pct=0.70, swing_pct=0.20, active_pct=0.10):
        self.core_pct = core_pct
        self.swing_pct = swing_pct
        self.active_pct = active_pct
    
    def calculate_tiers(self, total_qrl):
        """Calculate position tiers"""
        core_qrl = total_qrl * self.core_pct
        swing_qrl = total_qrl * self.swing_pct
        active_qrl = total_qrl * self.active_pct
        
        return {
            "total": total_qrl,
            "core": core_qrl,
            "swing": swing_qrl,
            "active": active_qrl,
            "tradeable": swing_qrl + active_qrl
        }
    
    def get_max_sellable(self, total_qrl):
        """Get maximum quantity that can be sold (non-core)"""
        tiers = self.calculate_tiers(total_qrl)
        return tiers["tradeable"]
```

**Step 2: Create PlanValidator** (1,900 chars)
```python
# src/app/application/trading/services/validators/plan_validator.py

class PlanValidator:
    def validate_plan(self, plan, ma_indicators, position_tiers):
        """Validate rebalance plan consistency"""
        errors = []
        
        # Check signal alignment
        if not self._check_signal_alignment(plan["action"], ma_indicators):
            errors.append("Action doesn't align with MA signal")
        
        # Check quantity limits
        if plan["action"] == "SELL":
            if plan["quantity"] > position_tiers["tradeable"]:
                errors.append("Sell quantity exceeds tradeable position")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _check_signal_alignment(self, action, ma_indicators):
        """Check if action aligns with MA signal"""
        signal = ma_indicators.get("signal")
        if action == "BUY" and signal != "GOLDEN_CROSS":
            return False
        if action == "SELL" and signal != "DEATH_CROSS":
            return False
        return True
```

**Step 3: Refactor IntelligentRebalanceService** (7,000 chars)
- Delegate tier calculations to TierAllocator
- Use PlanValidator for plan validation
- Keep core orchestration logic

---

## Phase 4: Task Interfaces (HIGH PRIORITY)

**Timeline**: 4-6 hours
**Files**: 3
**Risk**: Low (interface layer)

### 4.1-4.3: Task Endpoints

**Pattern**: Extract executors and formatters from each task endpoint

**Files**:
- task_15_min_job.py
- intelligent_rebalance.py  
- rebalance.py

**Approach**: Create reusable task components:
```python
# tasks/executors/{name}_executor.py
# tasks/formatters/task_response_formatter.py
```

---

## Phase 5: HTTP Interfaces (MEDIUM PRIORITY)

**Timeline**: 6-8 hours
**Files**: 6
**Risk**: Low (interface layer)

### 5.1-5.3: HTTP Endpoints

**Pattern**: Extract handlers and builders

**Files**:
- account.py
- market.py (HTTP)
- sub_account.py
- market.py (cache)
- balance.py (cache)
- trade_repository_core.py

---

## Phase 6: Infrastructure (LOWER PRIORITY)

**Timeline**: 4-6 hours
**Files**: 6
**Risk**: Very Low (utilities)

### 6.1-6.6: Utilities and Configuration

**Files**:
- settings.py
- trading_workflow.py
- market_service_core.py
- rebalance_service.py
- redis_data_manager.py
- client.py

**Approach**: Extract only where it significantly improves clarity

---

## Validation Procedures

**After Each File**:
1. Syntax check: `python -m py_compile <file>`
2. Import check: `python -c "from <module> import <class>"`
3. Format: `make fmt`
4. Lint: `make lint`

**After Each Phase**:
1. Run unit tests: `make test`
2. Start application: `python main.py`
3. Verify all routes registered
4. Check for import errors

**Before Final Commit**:
1. Full test suite: `pytest tests/ -v`
2. Type check: `make type`
3. Application startup verification
4. Smoke test critical endpoints

---

## Rollback Plan

**If Issues Arise**:
1. Revert via git: `git checkout HEAD~1 -- <file>`
2. Re-run validation
3. Document issue for later resolution
4. Continue with next file

---

## Success Criteria

✅ All files <4000 chars (or justified exceptions)
✅ All tests passing
✅ Application starts successfully
✅ No breaking changes to public APIs
✅ Improved code organization and testability

---

## Timeline Summary

- **Phase 3**: Week 1-2 (critical files)
- **Phase 4**: Week 2-3 (task interfaces)
- **Phase 5**: Week 3-4 (HTTP interfaces)
- **Phase 6**: Week 4-5 (infrastructure)

**Total**: 4-5 weeks for complete refactoring
