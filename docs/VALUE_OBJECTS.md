# Value Objects in Domain Layer

## Overview

Value Objects are a fundamental building block of Domain-Driven Design (DDD). This document explains what they are, why they matter, and how to use them in this project.

## What Are Value Objects?

**Value Objects** are domain concepts that are defined by their **values**, not by their identity.

### Key Characteristics

1. **Immutable**: Once created, they cannot be modified
2. **Validated**: Always in a valid state (validation happens on creation)
3. **Equality by Value**: Two value objects with the same value are considered equal
4. **No Identity**: They don't have a unique identifier like entities do
5. **Hashable**: Can be used as dictionary keys or in sets

## Value Objects vs Entities

Understanding the difference between Value Objects and Entities is crucial for clear domain modeling:

| Aspect | Value Object | Entity |
|--------|-------------|--------|
| Identity | No unique identity | Has unique identifier (ID) |
| Equality | By value | By identity |
| Mutability | Immutable | Mutable (controlled) |
| Example | Price, Symbol, Quantity | Order, Account, Position |
| Purpose | Describe properties | Track lifecycle |

### Examples

**Value Objects** (defined by their values):
- `Symbol("QRLUSDT")` - The symbol itself is the important thing
- `Price(100.5, "USDT")` - The price value is what matters
- `Quantity(10.0)` - The amount is the key concept
- `OrderSide.BUY` - The direction of the trade

**Entities** (defined by their identity):
- `Order(order_id="12345")` - Each order is unique even with same properties
- `Trade(trade_id="67890")` - Each trade has its own history
- `Account(account_id="abc")` - Identity persists regardless of balance changes
- `Position(symbol="QRLUSDT")` - Tracks specific holdings over time

## Implementation in This Project

### Location

Value objects are located in:
```
src/app/domain/value_objects/
├── __init__.py
├── symbol.py          # Trading pair symbol
├── price.py           # Monetary price
├── quantity.py        # Trading amount
├── order_side.py      # BUY/SELL direction
└── order_status.py    # Order state
```

### Pattern

All value objects in this project follow this pattern:

```python
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True, slots=True)  # frozen=True makes it immutable
class Price:
    """Price value object with validation."""
    
    value: Decimal
    currency: str = "USDT"
    
    def __post_init__(self) -> None:
        """Validate on creation."""
        if self.value < 0:
            raise ValueError(f"Price cannot be negative: {self.value}")
        if not self.currency:
            raise ValueError("Currency cannot be empty")
    
    @classmethod
    def from_float(cls, value: float, currency: str = "USDT") -> "Price":
        """Factory method for convenience."""
        return cls(value=Decimal(str(value)), currency=currency)
```

## Usage Examples

### Creating Value Objects

```python
from src.app.domain.value_objects import Symbol, Price, Quantity, OrderSide
from decimal import Decimal

# Direct creation
symbol = Symbol("QRLUSDT")
price = Price(Decimal("100.5"), "USDT")
quantity = Quantity(Decimal("10.0"))

# Using factory methods (recommended for convenience)
price = Price.from_float(100.5, "USDT")
quantity = Quantity.from_float(10.0)
side = OrderSide.buy()
```

### Immutability

```python
price = Price.from_float(100.5, "USDT")

# This will raise FrozenInstanceError
# price.value = Decimal("200")  # ❌ Error!

# Instead, create a new instance
new_price = Price.from_float(200.0, "USDT")  # ✅ Correct
```

### Validation

```python
# These will raise ValueError on creation
Symbol("")                    # Empty symbol
Symbol("qrlusdt")            # Must be uppercase
Price.from_float(-100, "USDT")  # Negative price
Quantity.from_float(0)        # Must be positive
```

### Equality and Hashing

```python
# Value objects are equal if their values are equal
price1 = Price.from_float(100.5, "USDT")
price2 = Price.from_float(100.5, "USDT")
assert price1 == price2  # ✅ True (same value)

# Can be used as dictionary keys
prices_by_symbol = {
    Symbol("QRLUSDT"): Price.from_float(100.5, "USDT"),
    Symbol("BTCUSDT"): Price.from_float(50000.0, "USDT"),
}

# Can be used in sets (duplicates removed)
symbols = {Symbol("QRLUSDT"), Symbol("QRLUSDT")}
assert len(symbols) == 1  # ✅ Duplicate removed
```

### Operations

Value objects can have methods that return new instances:

```python
# Price operations
price = Price.from_float(100.0, "USDT")
doubled = price.multiply(Decimal("2"))  # Returns new Price(200.0)
total = price.add(Price.from_float(50.0, "USDT"))  # Returns new Price(150.0)

# Quantity operations
qty = Quantity.from_float(10.0)
increased = qty.add(Quantity.from_float(5.0))  # Returns new Quantity(15.0)

# OrderSide operations
buy = OrderSide.buy()
sell = buy.opposite()  # Returns OrderSide.sell()
```

### Using with Entities

Value objects compose well with entities:

```python
from src.app.domain.models import Order
from src.app.domain.value_objects import Symbol, Price, Quantity, OrderSide

# Entities use value objects for their properties
order = Order(
    symbol=Symbol("QRLUSDT"),
    price=Price.from_float(100.5, "USDT"),
    quantity=Quantity.from_float(10.0),
    side=OrderSide.buy(),
    order_id="12345",  # Entity has identity
)
```

## Benefits

### 1. Reduced Cognitive Load

**Before** (primitive obsession):
```python
def place_order(symbol: str, price: float, quantity: float, side: str):
    # What are valid values? What format for symbol?
    # Can price be negative? Can quantity be zero?
    # Is "buy" or "BUY" correct?
    pass
```

**After** (with value objects):
```python
def place_order(
    symbol: Symbol, 
    price: Price, 
    quantity: Quantity, 
    side: OrderSide
):
    # All values are validated and type-safe
    # Clear semantic meaning
    # Impossible to pass invalid data
    pass
```

### 2. Type Safety

```python
# Before: Easy to mix up parameters
place_order("100.5", "QRLUSDT", "10.0", "BUY")  # Wrong order!

# After: Type checker catches errors
place_order(
    symbol=Symbol("QRLUSDT"),
    price=Price.from_float(100.5),
    quantity=Quantity.from_float(10.0),
    side=OrderSide.buy()
)
```

### 3. Domain Logic Centralization

```python
# Business logic lives in value objects
if price.is_zero():
    raise ValueError("Cannot place order with zero price")

if order_status.is_final():
    raise ValueError("Cannot modify completed order")

if side.is_buy() and not has_sufficient_funds():
    raise ValueError("Insufficient funds for buy order")
```

### 4. Testability

```python
def test_price_validation():
    """Value objects make testing domain rules easy."""
    with pytest.raises(ValueError, match="negative"):
        Price.from_float(-100, "USDT")
    
    with pytest.raises(ValueError, match="empty"):
        Symbol("")
```

## Migration Strategy

### Phase 1: Establish Pattern (Current)

- ✅ Create `domain/value_objects/` directory
- ✅ Implement core value objects (Symbol, Price, Quantity, etc.)
- ✅ Add comprehensive tests
- ✅ Document usage patterns
- ✅ Keep backward compatibility

### Phase 2: Progressive Adoption (Future)

1. **New Code**: Always use value objects
2. **Existing Code**: Gradually refactor as you touch files
3. **Critical Paths**: Prioritize high-value areas (order placement, validation)
4. **Update Imports**: Slowly migrate from `models` to value objects where appropriate

### Example Migration

**Before**:
```python
# Old style with primitive types
def validate_order(symbol: str, price: float, qty: float):
    if not symbol:
        raise ValueError("Symbol required")
    if price <= 0:
        raise ValueError("Price must be positive")
    if qty <= 0:
        raise ValueError("Quantity must be positive")
```

**After**:
```python
# New style with value objects (validation built-in)
def validate_order(symbol: Symbol, price: Price, qty: Quantity):
    # No validation needed - value objects are always valid
    pass
```

## Best Practices

### DO ✅

1. **Use value objects for domain concepts**
   - Prices, quantities, symbols, timestamps
   - Status codes, types, enums
   - Measurements, coordinates, ranges

2. **Make them immutable**
   - Use `frozen=True` in dataclass decorator
   - Return new instances for modifications

3. **Validate in `__post_init__`**
   - Ensure value objects are always valid
   - Fail fast with clear error messages

4. **Provide factory methods**
   - `from_float()`, `from_string()`, `from_parts()`
   - Make creation convenient

5. **Implement comparison methods**
   - `__eq__`, `__hash__`, `__lt__`, etc.
   - Enable usage in collections

### DON'T ❌

1. **Don't use primitives for domain concepts**
   - ❌ `price: float` → ✅ `price: Price`
   - ❌ `symbol: str` → ✅ `symbol: Symbol`

2. **Don't make value objects mutable**
   - ❌ `price.value = 200` → ✅ `new_price = Price(...)`

3. **Don't skip validation**
   - ❌ Accept any value → ✅ Validate in `__post_init__`

4. **Don't use value objects when identity matters**
   - ❌ `Order` as value object → ✅ `Order` as entity

5. **Don't mix entities and value objects**
   - Keep them in separate directories
   - Clear naming and documentation

## Common Pitfalls

### Pitfall 1: Not Using Decimal for Money

```python
# ❌ BAD: Float has precision issues
price = Price(100.1 + 0.2, "USDT")  # 100.30000000000001

# ✅ GOOD: Decimal is precise
price = Price.from_float(100.1, "USDT").add(Price.from_float(0.2, "USDT"))
```

### Pitfall 2: Comparing Different Currencies

```python
# ❌ BAD: Will raise ValueError
usd_price = Price.from_float(100, "USD")
usdt_price = Price.from_float(100, "USDT")
if usd_price < usdt_price:  # Error!
    pass

# ✅ GOOD: Convert first or compare same currency
if usd_price.currency == usdt_price.currency:
    if usd_price < usdt_price:
        pass
```

### Pitfall 3: Mutating Value Objects

```python
# ❌ BAD: Trying to mutate (will raise error)
price = Price.from_float(100, "USDT")
price.value = Decimal("200")  # FrozenInstanceError

# ✅ GOOD: Create new instance
new_price = Price.from_float(200, "USDT")
```

## Summary

Value Objects are a powerful tool for building clear, type-safe domain models:

- **Immutable** → Thread-safe and predictable
- **Validated** → Always in valid state
- **Type-safe** → Compiler catches errors
- **Self-documenting** → Clear semantic meaning
- **Composable** → Build complex concepts from simple ones

By using value objects, we reduce cognitive load, increase type safety, and make the domain model more explicit and maintainable.

## Further Reading

- [Domain-Driven Design: Value Objects](https://martinfowler.com/bliki/ValueObject.html)
- [Architecture Documentation](./✨.md) - Section on Domain Layer
- [Domain Model Reference](../src/app/domain/value_objects/)
