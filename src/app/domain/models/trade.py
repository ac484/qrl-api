"""Trade entity representing a completed trade execution.

DDD Entity Pattern:
- Entity: Has identity (trade_id required), immutable after creation
- Uses Value Objects for domain concepts
- No state transitions (trade is complete when created)

Trade is an Entity (not VO) because:
- Has unique identity (trade_id)
- Needs to be tracked individually
- Two trades with same values but different IDs are different trades

Example:
    >>> from src.app.domain.value_objects import Symbol, OrderSide, Quantity, Price
    >>> trade = Trade(
    ...     trade_id="T12345",
    ...     symbol=Symbol("QRLUSDT"),
    ...     side=OrderSide.buy(),
    ...     quantity=Quantity.from_float(10.0),
    ...     price=Price.from_float(100.5, "USDT"),
    ...     order_id="O12345",
    ... )
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.app.domain.value_objects import OrderSide, Price, Quantity, Symbol


@dataclass(slots=True)
class Trade:
    """Trade entity representing completed trade execution.
    
    Entity Characteristics:
    - Has identity (trade_id required)
    - Immutable after creation (no state transitions)
    - Uses value objects for domain concepts
    - Two trades are equal only if they have the same trade_id
    
    Attributes:
        trade_id: Unique trade identifier (entity identity, required)
        symbol: Trading pair (immutable value object)
        side: Trade direction BUY/SELL (immutable value object)
        quantity: Amount traded (immutable value object)
        price: Execution price (immutable value object)
        order_id: Related order ID (optional)
        executed_at: Trade execution timestamp
    
    Example:
        >>> trade = Trade(
        ...     trade_id="T12345",
        ...     symbol=Symbol("QRLUSDT"),
        ...     side=OrderSide.buy(),
        ...     quantity=Quantity.from_float(10.0),
        ...     price=Price.from_float(100.5, "USDT"),
        ... )
        >>> trade.trade_id
        'T12345'
        >>> trade.total_value
        Decimal('1005.0')
    """

    trade_id: str  # Entity identity - required
    symbol: Symbol
    side: OrderSide
    quantity: Quantity
    price: Price
    order_id: Optional[str] = None
    executed_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate entity invariants on creation."""
        if not self.trade_id:
            raise ValueError("Trade must have a trade_id (entity identity)")

    @property
    def total_value(self):
        """Calculate total trade value (quantity * price)."""
        return self.quantity.value * self.price.value

    def is_buy(self) -> bool:
        """Check if this is a buy trade."""
        return self.side.is_buy()

    def is_sell(self) -> bool:
        """Check if this is a sell trade."""
        return self.side.is_sell()


__all__ = ["Trade"]
