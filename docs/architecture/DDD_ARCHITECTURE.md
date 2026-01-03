# DDD Architecture - Complete Reference

## Overview

This document describes the Domain-Driven Design (DDD) architecture implemented in the qrl-api project. The architecture enforces complete separation of Value Objects and Entities throughout the domain layer, with zero primitive obsession.

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│                    Interface Layer                           │
│  (HTTP Routes, Tasks, DTOs - To Be Migrated)                │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                 Application Layer                            │
│  (Services, Use Cases - To Be Migrated)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                   Domain Layer ✅ COMPLETE                   │
│  ├── Value Objects (Immutable, No Identity)                 │
│  ├── Entities (Identity, Mutable State, Behavior)           │
│  ├── Domain Events (Immutable Facts with VOs)               │
│  ├── Policy Objects (Business Rules with VOs)               │
│  ├── Domain Services (Orchestrate VOs and Entities)         │
│  └── Result Types (Typed Returns, No Dict)                  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                Infrastructure Layer                          │
│  (Repositories, Adapters - To Be Migrated)                  │
└─────────────────────────────────────────────────────────────┘
```

## Domain Layer Components

### Value Objects (Immutable, No Identity)

#### Symbol
- **Purpose**: Trading pair validation
- **Validation**: Uppercase, alphanumeric, min length
- **File**: `src/app/domain/value_objects/symbol.py`
- **Example**:
```python
symbol = Symbol("QRLUSDT")  # Validated on construction
# Symbol("")  # ValueError: Symbol cannot be empty
```

#### Price
- **Purpose**: Decimal-based monetary values
- **Features**: Currency awareness, arithmetic operations
- **File**: `src/app/domain/value_objects/price.py`
- **Example**:
```python
price = Price(Decimal("100.5"), "USDT")
# price_float = Price.from_float(100.5, "USDT")  # Factory method
total = price * Quantity(Decimal("10"))  # Returns Decimal
```

#### Quantity
- **Purpose**: Positive-validated trading amounts
- **Features**: Arithmetic operations, validation
- **File**: `src/app/domain/value_objects/quantity.py`
- **Example**:
```python
qty = Quantity(Decimal("10.5"))
# qty_float = Quantity.from_float(10.5)  # Factory method
# Quantity(Decimal("0"))  # ValueError: must be positive
```

#### Percentage
- **Purpose**: 0-1 range proportions/ratios
- **Features**: apply_to(), complement() operations
- **File**: `src/app/domain/value_objects/percentage.py`
- **Example**:
```python
pct = Percentage.from_float(0.7)  # 70%
result = pct.apply_to(Decimal("1000"))  # Decimal('700')
remaining = pct.complement()  # Percentage(0.3) = 30%
```

#### OrderSide
- **Purpose**: Type-safe BUY/SELL enum
- **Features**: Domain methods (is_buy(), is_sell())
- **File**: `src/app/domain/value_objects/order_side.py`
- **Example**:
```python
side = OrderSide.buy()
if side.is_buy():
    # Buy logic
```

#### OrderStatus
- **Purpose**: Order lifecycle states
- **Features**: State predicates (is_active(), is_final())
- **File**: `src/app/domain/value_objects/order_status.py`

#### Balance
- **Purpose**: Asset amounts with free/locked portions
- **Features**: Immutable operations returning new instances
- **File**: `src/app/domain/value_objects/balance.py`
- **Example**:
```python
balance = Balance.from_float("USDT", 1000.0, 50.0)
new_balance = balance.lock(Decimal("100"))  # Returns new instance
```

### Entities (Identity, Mutable State, Behavior)

#### Order Entity
- **Identity**: `order_id` (required, string)
- **State Transitions**: fill(), partial_fill(), cancel(), reject(), expire()
- **Business Rules**: Price limits, quantity validation
- **File**: `src/app/domain/models/order.py`
- **Example**:
```python
order = Order(
    order_id="12345",
    symbol=Symbol("QRLUSDT"),
    side=OrderSide.buy(),
    quantity=Quantity.from_float(10.0),
    price=Price.from_float(100.5, "USDT"),
)
order.fill(Quantity.from_float(10.0), Price.from_float(100.0, "USDT"))
```

#### Trade Entity
- **Identity**: `trade_id` (required, string)
- **Immutable After Creation**: No state transitions
- **File**: `src/app/domain/models/trade.py`
- **Example**:
```python
trade = Trade(
    trade_id="T12345",
    symbol=Symbol("QRLUSDT"),
    side=OrderSide.buy(),
    quantity=Quantity.from_float(10.0),
    price=Price.from_float(100.5, "USDT"),
)
```

#### Position Entity
- **Identity**: `symbol` (Symbol VO - one position per trading pair)
- **State Transitions**: apply_buy(), apply_sell(), update_unrealized_pnl()
- **Domain Methods**: get_tradeable_quantity(Percentage)
- **File**: `src/app/domain/models/position.py`
- **Example**:
```python
position = Position(
    symbol=Symbol("QRLUSDT"),
    total_quantity=Quantity.from_float(100.0),
    average_cost=Price.from_float(100.0, "USDT"),
)
position.apply_buy(Quantity.from_float(50.0), Price.from_float(110.0, "USDT"))

core_pct = Percentage.from_float(0.7)
tradeable = position.get_tradeable_quantity(core_pct)  # Quantity VO
```

#### Account Entity (Aggregate Root)
- **Identity**: `account_id` (required, string)
- **Aggregate Root**: Manages Balance VOs
- **Operations**: deposit(), withdraw(), lock_for_order(), unlock_from_order()
- **File**: `src/app/domain/models/account.py`
- **Example**:
```python
account = Account(account_id="A12345")
account.deposit("USDT", Decimal("1000.0"))
account.lock_for_order("USDT", Decimal("100.0"))
balance = account.get_balance("USDT")  # Returns Balance VO
```

### Domain Events (Immutable Facts)

All events use Value Objects, not primitives. Events are frozen/immutable.

- **PriceUpdated**: Uses Symbol, Price VOs
- **OrderPlaced**: Uses Symbol, OrderSide, Quantity, Price VOs
- **TradeExecuted**: Uses Symbol, OrderSide, Quantity, Price VOs

**File**: `src/app/domain/events/trading_events.py`

**Example**:
```python
event = TradeExecuted(
    symbol=Symbol("QRLUSDT"),
    side=OrderSide.buy(),
    quantity=Quantity.from_float(10.0),
    price=Price.from_float(100.5, "USDT"),
)
```

### Policy Objects (Business Rules)

Policy objects encapsulate business decision logic using Value Objects.

#### StopLossGuard
- **Purpose**: Determines exit conditions
- **Uses**: Price, Percentage VOs
- **File**: `src/app/domain/risk/stop_loss.py`
- **Example**:
```python
guard = StopLossGuard(max_drawdown=Percentage.from_float(0.1))
should_exit = guard.should_exit(
    current_price=Price.from_float(90.0, "USDT"),
    avg_cost=Price.from_float(100.0, "USDT"),
)  # True if drawdown >= 10%
```

### Domain Services (Orchestration)

Domain services orchestrate Value Objects and Entities, returning typed results.

#### PositionManager
- **Purpose**: Position size calculations
- **Uses**: Percentage, Price, Quantity VOs
- **Returns**: Typed result objects (not Dict)
- **File**: `src/app/domain/position/calculator.py`
- **Example**:
```python
manager = PositionManager(
    max_position_size=Percentage.from_float(0.5),
    core_position_pct=Percentage.from_float(0.7)
)
result = manager.calculate_buy_quantity(
    usdt_balance=Quantity(Decimal("1000"), "USDT"),
    price=Price(Decimal("100"), "USDT")
)
# result.usdt_to_use is Quantity VO
# result.quantity_to_buy is Quantity VO
```

#### RiskManager
- **Purpose**: Risk validation
- **Uses**: Percentage, Quantity, Position entity
- **Returns**: RiskCheckResult (not Dict)
- **File**: `src/app/domain/risk/limits.py`

### Validators (Invariant Enforcement)

Validators enforce domain invariants using Value Objects.

#### PositionValidator
- **Purpose**: Position protection validation
- **Uses**: Percentage, Quantity, Position entity
- **Returns**: Typed result objects (SellProtectionResult, BuyProtectionResult)
- **File**: `src/app/domain/risk/validators/position_validator.py`
- **Example**:
```python
validator = PositionValidator(core_position_pct=Percentage.from_float(0.7))
result = validator.check_sell_protection(position)
# result.allowed is bool
# result.tradeable_quantity is Quantity VO or None
```

### Result Types (Typed Returns)

Domain services and validators return typed result dataclasses, not Dict[str, Any].

**Position Results** (`src/app/domain/position/results.py`):
- BuyCalculation
- SellCalculation
- AverageCostCalculation
- PnLCalculation

**Risk Results** (`src/app/domain/risk/results.py`):
- RiskCheckResult
- SellProtectionResult
- BuyProtectionResult

## Benefits Achieved

### 1. Zero Primitive Obsession
No float, str, or Dict[str, Any] in domain layer. All domain concepts use explicit types.

### 2. Complete Type Safety
Compiler catches errors at development time, not runtime.

### 3. Self-Documenting APIs
```python
# Bad (before)
def calculate_buy(balance: float, price: float) -> Dict[str, float]

# Good (after)
def calculate_buy_quantity(usdt_balance: Quantity, price: Price) -> BuyCalculation
```

### 4. IDE Support
Full autocomplete for all domain operations.

### 5. No Runtime Dict Errors
```python
# Bad (before)
result = service.calculate()
qty = result["quantity"]  # KeyError risk

# Good (after)
result = service.calculate_buy_quantity(...)
qty = result.quantity_to_buy  # Type-safe property
```

### 6. Reduced Cognitive Load
Clear separation of concerns. Easy to understand what each type represents.

### 7. Maintainability
Breaking changes caught at compile time. Refactoring is safe with IDE support.

### 8. Testability
Type-safe mocks and fixtures. No ambiguous Dict structures.

## Read Model Pattern

**MarketPrice** is neither Entity nor Value Object - it's a Read Model/DTO for market data snapshots.

- **Has timestamp** (point-in-time state) but no identity or lifecycle
- **Use for**: Display/reporting only
- **Don't use for**: Domain logic
- **File**: `src/app/domain/models/market_price.py`

For domain logic, use `value_objects.Price`.

## Breaking Changes

### No Backward Compatibility

This architecture enforces proper DDD from the core with no compromise:

1. ❌ Removed primitive type constructors
2. ❌ Removed `from_primitives()`/`to_primitives()` conversion methods
3. ❌ No direct primitive parameters accepted in domain layer
4. ✅ Value Objects required for all domain operations
5. ✅ Typed results replace Dict returns

### Migration Required

Application and infrastructure layers must be updated to:
1. Convert primitives to Value Objects at boundaries
2. Use typed results instead of Dict
3. Handle Value Object construction and validation

See MIGRATION_GUIDE.md for detailed migration patterns.

## Next Steps

1. **Application Layer**: Migrate services to use VOs (see migration guide)
2. **Infrastructure Layer**: Update repositories to work with VOs
3. **Interface Layer**: Create DTOs and mappers for external integration
4. **Tests**: Update all tests to use Value Objects

## References

- DDD Patterns: Eric Evans, "Domain-Driven Design"
- Value Object Pattern: Martin Fowler, "Value Object"
- Entity Pattern: Martin Fowler, "Entity"
- Aggregate Root Pattern: Vernon, "Implementing Domain-Driven Design"
