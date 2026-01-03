# DDD Migration Guide

## Overview

This guide provides practical patterns for migrating application and infrastructure layers to use the new Domain-Driven Design (DDD) architecture with Value Objects and Entities.

## Migration Strategy

### Phase 1: Domain Layer ✅ COMPLETE
- Value Objects created and validated
- Entities refactored with proper encapsulation
- Domain events, policies, services refactored
- Result types created

### Phase 2: Application Layer (In Progress)
- Create boundary adapters/mappers
- Migrate service by service
- Update use case handlers

### Phase 3: Infrastructure Layer (Planned)
- Update repositories to work with VOs
- Create VO serialization/deserialization
- Migrate database adapters

### Phase 4: Interface Layer (Planned)
- Create DTOs for HTTP/Task interfaces
- Implement DTO ↔ VO mappers
- Update route handlers

## Common Migration Patterns

### Pattern 1: Converting Primitives to Value Objects

#### Before (Primitives):
```python
def calculate_buy(balance: float, price: float) -> Dict[str, float]:
    qty = balance / price
    return {"quantity": qty, "cost": balance}
```

#### After (Value Objects):
```python
from src.app.domain.value_objects import Quantity, Price
from src.app.domain.position.results import BuyCalculation

def calculate_buy_quantity(
    usdt_balance: Quantity, 
    price: Price
) -> BuyCalculation:
    qty_value = usdt_balance.value / price.value
    quantity_to_buy = Quantity(qty_value)
    return BuyCalculation(
        usdt_to_use=usdt_balance,
        quantity_to_buy=quantity_to_buy
    )
```

### Pattern 2: Boundary Conversion (DTO → VO)

Create mappers at application/infrastructure boundaries:

```python
# At HTTP boundary
from dataclasses import dataclass
from src.app.domain.value_objects import Symbol, Price, Quantity, OrderSide
from src.app.domain.models import Order

@dataclass
class CreateOrderDTO:
    """External HTTP request format"""
    symbol: str
    side: str
    quantity: float
    price: float

class OrderMapper:
    """Converts between DTO and domain types"""
    
    @staticmethod
    def from_dto(dto: CreateOrderDTO, order_id: str) -> Order:
        """Convert DTO to domain Order entity"""
        return Order(
            order_id=order_id,
            symbol=Symbol(dto.symbol.upper()),
            side=OrderSide.buy() if dto.side.upper() == "BUY" else OrderSide.sell(),
            quantity=Quantity.from_float(dto.quantity),
            price=Price.from_float(dto.price, "USDT"),
        )
    
    @staticmethod
    def to_dto(order: Order) -> dict:
        """Convert domain Order to HTTP response"""
        return {
            "order_id": order.order_id,
            "symbol": order.symbol.value,
            "side": "BUY" if order.side.is_buy() else "SELL",
            "quantity": float(order.quantity.value),
            "price": float(order.price.value),
            "status": order.status.value,
        }
```

### Pattern 3: Repository Pattern with VOs

Update repositories to work with Value Objects:

#### Before (Primitives):
```python
class PositionRepository:
    async def save(self, symbol: str, quantity: float, avg_cost: float):
        await self.redis.set(f"position:{symbol}", {
            "quantity": quantity,
            "avg_cost": avg_cost
        })
    
    async def get(self, symbol: str) -> Optional[Dict]:
        data = await self.redis.get(f"position:{symbol}")
        return data  # Returns Dict or None
```

#### After (Value Objects):
```python
from src.app.domain.value_objects import Symbol, Quantity, Price
from src.app.domain.models import Position
from decimal import Decimal

class PositionRepository:
    async def save(self, position: Position) -> None:
        """Save Position entity using VOs"""
        data = {
            "symbol": position.symbol.value,
            "total_quantity": str(position.total_quantity.value),
            "average_cost": str(position.average_cost.value),
            "currency": position.average_cost.currency,
        }
        await self.redis.set(
            f"position:{position.symbol.value}", 
            data
        )
    
    async def get(self, symbol: Symbol) -> Optional[Position]:
        """Retrieve Position entity with VOs"""
        data = await self.redis.get(f"position:{symbol.value}")
        if not data:
            return None
        
        return Position(
            symbol=Symbol(data["symbol"]),
            total_quantity=Quantity(Decimal(data["total_quantity"])),
            average_cost=Price(Decimal(data["average_cost"]), data["currency"]),
        )
```

### Pattern 4: Service Layer Migration

#### Before (Application Service with Primitives):
```python
class RebalanceService:
    def __init__(self, target_ratio: float, threshold: float):
        self.target_ratio = target_ratio
        self.threshold = threshold
    
    async def compute_plan(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        qrl_balance = snapshot["balances"]["QRL"]["total"]
        usdt_balance = snapshot["balances"]["USDT"]["total"]
        price = snapshot["prices"]["QRLUSDT"]
        
        qrl_value = qrl_balance * price
        total_value = qrl_value + usdt_balance
        target_value = total_value * self.target_ratio
        
        return {
            "action": "BUY" if qrl_value < target_value else "SELL",
            "quantity": abs(qrl_value - target_value) / price,
        }
```

#### After (Application Service with VOs):
```python
from dataclasses import dataclass
from src.app.domain.value_objects import Symbol, Price, Quantity, Percentage, OrderSide
from src.app.domain.models import Position, Account

@dataclass(frozen=True)
class RebalancePlan:
    """Typed result for rebalance computation"""
    action: OrderSide
    quantity: Quantity
    target_value: Quantity  # In USDT
    current_value: Quantity  # In USDT

class RebalanceService:
    def __init__(
        self, 
        target_ratio: Percentage, 
        threshold: Percentage
    ):
        self.target_ratio = target_ratio
        self.threshold = threshold
    
    async def compute_plan(
        self, 
        position: Position, 
        account: Account, 
        current_price: Price
    ) -> RebalancePlan:
        """Compute rebalance plan using domain types"""
        usdt_balance = account.get_balance("USDT")
        
        # Calculate values using VOs
        qrl_value_decimal = position.total_quantity.value * current_price.value
        qrl_value = Quantity(qrl_value_decimal, "USDT")
        
        total_value_decimal = qrl_value.value + usdt_balance.free
        total_value = Quantity(total_value_decimal, "USDT")
        
        target_value_decimal = self.target_ratio.apply_to(total_value.value)
        target_value = Quantity(target_value_decimal, "USDT")
        
        # Determine action
        if qrl_value.value < target_value.value:
            action = OrderSide.buy()
            delta = target_value.value - qrl_value.value
        else:
            action = OrderSide.sell()
            delta = qrl_value.value - target_value.value
        
        quantity = Quantity(delta / current_price.value)
        
        return RebalancePlan(
            action=action,
            quantity=quantity,
            target_value=target_value,
            current_value=qrl_value,
        )
```

### Pattern 5: Event Handler Migration

#### Before (Event Handler with Dict):
```python
async def handle_trade_executed(event: Dict[str, Any]):
    symbol = event["symbol"]
    side = event["side"]
    quantity = event["quantity"]
    price = event["price"]
    
    # Update position
    if side == "BUY":
        await position_repo.add_quantity(symbol, quantity, price)
    else:
        await position_repo.subtract_quantity(symbol, quantity, price)
```

#### After (Event Handler with VOs):
```python
from src.app.domain.events.trading_events import TradeExecuted
from src.app.domain.models import Position

async def handle_trade_executed(event: TradeExecuted):
    """Type-safe event handler using domain types"""
    position = await position_repo.get(event.symbol)
    
    if position is None:
        # Create new position for first trade
        position = Position(
            symbol=event.symbol,
            total_quantity=Quantity.zero(),
            average_cost=event.price,
        )
    
    # Use entity methods for state transitions
    if event.side.is_buy():
        position.apply_buy(event.quantity, event.price)
    else:
        position.apply_sell(event.quantity, event.price)
    
    await position_repo.save(position)
```

### Pattern 6: Validation at Boundaries

Always validate external input and convert to VOs at boundaries:

```python
from fastapi import HTTPException
from src.app.domain.value_objects import Symbol, Price, Quantity

def validate_and_convert_order_input(
    symbol: str, 
    quantity: float, 
    price: float
) -> tuple[Symbol, Quantity, Price]:
    """Validate HTTP input and convert to VOs"""
    try:
        symbol_vo = Symbol(symbol.upper())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid symbol: {e}")
    
    try:
        quantity_vo = Quantity.from_float(quantity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid quantity: {e}")
    
    try:
        price_vo = Price.from_float(price, "USDT")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid price: {e}")
    
    return symbol_vo, quantity_vo, price_vo
```

## Handling Decimal vs Float

### Rule: Use Decimal in Domain, Float at Boundaries

```python
from decimal import Decimal

# At HTTP boundary (incoming)
request_price = 100.5  # float from HTTP
price_vo = Price.from_float(request_price, "USDT")  # Converts to Decimal internally

# Domain operations use Decimal
total = price_vo.value * quantity_vo.value  # Both are Decimal

# At HTTP boundary (outgoing)
response_price = float(price_vo.value)  # Convert back to float for JSON
```

## Testing with VOs

### Unit Test Pattern:

```python
import pytest
from decimal import Decimal
from src.app.domain.value_objects import Price, Quantity, Symbol
from src.app.domain.models import Position

def test_position_apply_buy():
    # Arrange
    position = Position(
        symbol=Symbol("QRLUSDT"),
        total_quantity=Quantity.from_float(100.0),
        average_cost=Price.from_float(100.0, "USDT"),
    )
    
    # Act
    position.apply_buy(
        Quantity.from_float(50.0), 
        Price.from_float(110.0, "USDT")
    )
    
    # Assert
    assert position.total_quantity.value == Decimal("150.0")
    assert position.average_cost.value == Decimal("103.33333333333333333333333333")
```

### Integration Test Pattern:

```python
import pytest
from src.app.domain.value_objects import Symbol, Percentage
from src.app.domain.position.calculator import PositionManager

@pytest.fixture
def position_manager():
    return PositionManager(
        max_position_size=Percentage.from_float(0.5),
        core_position_pct=Percentage.from_float(0.7)
    )

async def test_calculate_buy_quantity(position_manager):
    # Arrange
    from src.app.domain.value_objects import Quantity, Price
    usdt_balance = Quantity(Decimal("1000"), "USDT")
    price = Price(Decimal("100"), "USDT")
    
    # Act
    result = position_manager.calculate_buy_quantity(usdt_balance, price)
    
    # Assert
    assert result.usdt_to_use.value == Decimal("500")  # 50% of balance
    assert result.quantity_to_buy.value == Decimal("5")  # 500 / 100
```

## Common Pitfalls

### Pitfall 1: Mixing Primitives and VOs
```python
# ❌ BAD: Mixing primitives and VOs
def calculate(price: Price, qty: float):  # Don't mix!
    return price.value * qty

# ✅ GOOD: Use VOs throughout
def calculate(price: Price, qty: Quantity) -> Decimal:
    return price.value * qty.value
```

### Pitfall 2: Bypassing VO Validation
```python
# ❌ BAD: Creating invalid state
qty = Quantity(Decimal("-10"))  # Should fail but might not if validation is weak

# ✅ GOOD: Use factory methods with validation
qty = Quantity.from_float(-10)  # Raises ValueError
```

### Pitfall 3: Returning Primitives from Domain
```python
# ❌ BAD: Domain service returning primitives
def calculate_total(self) -> float:
    return float(self.price.value * self.qty.value)

# ✅ GOOD: Domain service returning VOs or typed results
def calculate_total(self) -> Quantity:
    return Quantity(self.price.value * self.qty.value, "USDT")
```

### Pitfall 4: Modifying VOs
```python
# ❌ BAD: Trying to modify frozen VO
price.value = Decimal("200")  # Error: frozen dataclass

# ✅ GOOD: Create new instance
new_price = Price(Decimal("200"), "USDT")
```

## Migration Checklist

### For Each Service/Module:

- [ ] Identify all primitive parameters (float, str, Dict)
- [ ] Replace with appropriate Value Objects
- [ ] Create typed result dataclasses to replace Dict returns
- [ ] Update method signatures with VOs
- [ ] Convert primitives to VOs at boundaries (HTTP, DB)
- [ ] Update tests to use VOs
- [ ] Verify type safety with mypy/pylance
- [ ] Update documentation

### For Repositories:

- [ ] Update save() to accept Entities with VOs
- [ ] Update get() to return Entities with VOs
- [ ] Implement VO serialization/deserialization
- [ ] Handle None/missing data gracefully
- [ ] Update tests with VO fixtures

### For HTTP Routes:

- [ ] Create DTO dataclasses for requests/responses
- [ ] Create mappers between DTOs and domain types
- [ ] Validate input and convert to VOs
- [ ] Convert VOs to DTOs for responses
- [ ] Handle validation errors with proper HTTP status codes
- [ ] Update OpenAPI/Swagger docs

## Benefits After Migration

1. **Type Safety**: Compiler catches errors before runtime
2. **Self-Documenting**: Function signatures explain themselves
3. **IDE Support**: Full autocomplete and type checking
4. **Refactoring**: Safe, automated refactoring with IDE
5. **Testing**: Type-safe mocks and fixtures
6. **Maintainability**: Clear domain model, easy to understand
7. **No Dict Errors**: No more KeyError at runtime
8. **Validation**: Input validation at boundaries, invalid states impossible

## Getting Help

- See `DDD_ARCHITECTURE.md` for complete architecture reference
- Check existing domain layer for patterns and examples
- Use IDE type hints for guidance
- Consult stored DDD patterns in copilot memory

## Next Steps

1. Start with one application service
2. Create boundary mappers (DTO ↔ VO)
3. Update service to use VOs
4. Update tests
5. Repeat for next service

Gradual migration is acceptable. Domain layer is complete and stable.
