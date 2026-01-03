"""Domain value objects for trading system.

Value Objects are immutable objects that represent concepts through their values,
not their identity. They are fundamental to Domain-Driven Design (DDD).

Key Characteristics:
- Immutable (frozen dataclasses)
- Validated on creation
- Equality by value (not identity)
- No lifecycle or identity
- Can contain business logic related to their value

Examples:
    >>> from src.app.domain.value_objects import Symbol, Price, Quantity
    >>> from decimal import Decimal
    >>>
    >>> # Create value objects
    >>> symbol = Symbol("QRLUSDT")
    >>> price = Price.from_float(100.5, "USDT")
    >>> quantity = Quantity.from_float(10.0)
    >>>
    >>> # They are immutable
    >>> # symbol.value = "NEW"  # Raises FrozenInstanceError
    >>>
    >>> # They are comparable by value
    >>> price1 = Price.from_float(100.0, "USDT")
    >>> price2 = Price.from_float(100.0, "USDT")
    >>> price1 == price2  # True (same value)
    >>>
    >>> # They can be used as dictionary keys or in sets
    >>> prices = {symbol: price}
    >>> symbol_set = {symbol}

Contrast with Entities:
- Entities have identity (e.g., Order with order_id)
- Entities can change state over time
- Entities are compared by identity, not value
- Entities have lifecycle events

Usage in Domain Layer:
Value objects should be used to represent domain concepts that:
1. Are defined by their value, not identity
2. Should be immutable
3. Need validation logic
4. Can be compared and used in collections

This reduces cognitive load by making the domain model more explicit and type-safe.
"""

from src.app.domain.value_objects.balance import Balance
from src.app.domain.value_objects.order_side import OrderSide, OrderSideEnum
from src.app.domain.value_objects.order_status import OrderStatus, OrderStatusEnum
from src.app.domain.value_objects.percentage import Percentage
from src.app.domain.value_objects.price import Price
from src.app.domain.value_objects.quantity import Quantity
from src.app.domain.value_objects.symbol import Symbol

__all__ = [
    "Balance",
    "Symbol",
    "Price",
    "Quantity",
    "OrderSide",
    "OrderSideEnum",
    "OrderStatus",
    "OrderStatusEnum",
    "Percentage",
]
