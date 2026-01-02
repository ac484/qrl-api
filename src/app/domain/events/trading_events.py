"""Domain Events for trading system.

Domain Events are immutable facts that represent something that happened in the domain.
They use Value Objects instead of primitives for type safety and domain clarity.

Characteristics:
- Immutable (frozen dataclasses)
- Use Value Objects for domain concepts
- Timestamp when event occurred
- Represent facts (past tense names)

Examples:
    >>> from src.app.domain.value_objects import Symbol, Price, Quantity, OrderSide
    >>> from src.app.domain.events.trading_events import PriceUpdated, TradeExecuted
    >>> from datetime import datetime
    >>>
    >>> # Price updated event
    >>> event = PriceUpdated(
    ...     symbol=Symbol("QRLUSDT"),
    ...     price=Price.from_float(100.5, "USDT"),
    ...     timestamp=datetime.utcnow()
    ... )
    >>>
    >>> # Trade executed event
    >>> trade_event = TradeExecuted(
    ...     symbol=Symbol("QRLUSDT"),
    ...     side=OrderSide.buy(),
    ...     quantity=Quantity.from_float(10.0),
    ...     price=Price.from_float(100.5, "USDT")
    ... )
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

from src.app.domain.value_objects import Symbol, Price, Quantity, OrderSide


@dataclass(frozen=True, slots=True)
class PriceUpdated:
    """Event: Market price was updated.
    
    Attributes:
        symbol: Trading pair symbol
        price: Updated price
        timestamp: When price was updated
    """
    symbol: Symbol
    price: Price
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, slots=True)
class OrderPlaced:
    """Event: Order was placed.
    
    Attributes:
        symbol: Trading pair symbol
        side: Order side (BUY/SELL)
        quantity: Order quantity
        price: Order price (None for market orders)
        metadata: Additional order metadata
        timestamp: When order was placed
    """
    symbol: Symbol
    side: OrderSide
    quantity: Quantity
    price: Price | None = None
    metadata: Dict[str, Any] | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, slots=True)
class TradeExecuted:
    """Event: Trade was executed.
    
    Attributes:
        symbol: Trading pair symbol
        side: Trade side (BUY/SELL)
        quantity: Trade quantity
        price: Execution price
        timestamp: When trade was executed
    """
    symbol: Symbol
    side: OrderSide
    quantity: Quantity
    price: Price
    timestamp: datetime = field(default_factory=datetime.utcnow)


__all__ = ["PriceUpdated", "OrderPlaced", "TradeExecuted"]
