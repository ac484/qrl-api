"""Order entity for domain workflows.

NOTE: This is an Entity (has identity via order_id), not a Value Object.
Entities represent things with unique identity and lifecycle.

This module demonstrates both legacy (primitive types) and modern (value objects)
approaches for backward compatibility during migration.

For new code, prefer the OrderWithValueObjects class that uses proper DDD value objects.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Import value objects for enhanced type safety (optional usage)
try:
    from src.app.domain.value_objects import (
        OrderSide as OrderSideVO,
    )
    from src.app.domain.value_objects import (
        OrderStatus as OrderStatusVO,
    )
    from src.app.domain.value_objects import (
        Price as PriceVO,
    )
    from src.app.domain.value_objects import (
        Quantity as QuantityVO,
    )
    from src.app.domain.value_objects import (
        Symbol as SymbolVO,
    )

    VALUE_OBJECTS_AVAILABLE = True
except ImportError:
    VALUE_OBJECTS_AVAILABLE = False


@dataclass(slots=True)
class Order:
    """Order entity using primitive types (legacy, backward compatible).

    This is kept for backward compatibility with existing code.
    For new code, consider using OrderWithValueObjects instead.

    Attributes:
        symbol: Trading pair symbol (e.g., "QRLUSDT")
        side: Order side ("BUY" or "SELL")
        quantity: Amount to trade
        price: Order price (None for market orders)
        order_id: Unique order identifier (entity identity)
        status: Order status (e.g., "NEW", "FILLED")
        created_at: Order creation timestamp
    """

    symbol: str
    side: str
    quantity: float
    price: Optional[float] = None
    order_id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


if VALUE_OBJECTS_AVAILABLE:

    @dataclass(slots=True)
    class OrderWithValueObjects:
        """Order entity using value objects (recommended for new code).

        This demonstrates the DDD approach with proper value objects.
        Value objects provide:
        - Immutability and validation
        - Type safety and clear semantics
        - Domain logic encapsulation
        - Better testability

        Attributes:
            symbol: Trading pair (validated, immutable)
            side: Order direction (BUY/SELL, type-safe)
            quantity: Amount to trade (validated positive)
            price: Order price (validated, currency-aware)
            order_id: Unique order identifier (entity identity)
            status: Order lifecycle state (enum-based)
            created_at: Order creation timestamp

        Example:
            >>> from src.app.domain.value_objects import Symbol, OrderSide, Quantity, Price
            >>> order = OrderWithValueObjects(
            ...     symbol=Symbol("QRLUSDT"),
            ...     side=OrderSide.buy(),
            ...     quantity=Quantity.from_float(10.0),
            ...     price=Price.from_float(100.5, "USDT"),
            ...     order_id="12345",
            ... )
            >>> order.symbol.value
            'QRLUSDT'
            >>> order.side.is_buy()
            True
        """

        symbol: SymbolVO
        side: OrderSideVO
        quantity: QuantityVO
        price: Optional[PriceVO] = None
        order_id: Optional[str] = None
        status: Optional[OrderStatusVO] = None
        created_at: Optional[datetime] = None

        @classmethod
        def from_primitives(
            cls,
            symbol: str,
            side: str,
            quantity: float,
            price: Optional[float] = None,
            order_id: Optional[str] = None,
            status: Optional[str] = None,
            created_at: Optional[datetime] = None,
        ) -> "OrderWithValueObjects":
            """Create order from primitive values (for migration/interop).

            Args:
                symbol: Trading pair string
                side: Order side string ("BUY" or "SELL")
                quantity: Quantity as float
                price: Price as float (optional)
                order_id: Order identifier
                status: Status string (optional)
                created_at: Creation timestamp

            Returns:
                OrderWithValueObjects instance

            Example:
                >>> order = OrderWithValueObjects.from_primitives(
                ...     symbol="QRLUSDT",
                ...     side="BUY",
                ...     quantity=10.0,
                ...     price=100.5,
                ...     order_id="12345"
                ... )
            """
            return cls(
                symbol=SymbolVO(symbol),
                side=OrderSideVO.from_string(side),
                quantity=QuantityVO.from_float(quantity),
                price=PriceVO.from_float(price, "USDT") if price is not None else None,
                order_id=order_id,
                status=OrderStatusVO.from_string(status) if status else None,
                created_at=created_at,
            )

        def to_primitives(self) -> dict:
            """Convert to primitive dictionary (for serialization/API).

            Returns:
                Dictionary with primitive values

            Example:
                >>> order_dict = order.to_primitives()
                >>> order_dict["symbol"]
                'QRLUSDT'
            """
            return {
                "symbol": self.symbol.value,
                "side": str(self.side),
                "quantity": float(self.quantity),
                "price": float(self.price) if self.price else None,
                "order_id": self.order_id,
                "status": str(self.status) if self.status else None,
                "created_at": self.created_at,
            }

        def is_market_order(self) -> bool:
            """Check if this is a market order (no price specified)."""
            return self.price is None

        def is_limit_order(self) -> bool:
            """Check if this is a limit order (price specified)."""
            return self.price is not None

        def is_buy(self) -> bool:
            """Check if this is a buy order."""
            return self.side.is_buy()

        def is_sell(self) -> bool:
            """Check if this is a sell order."""
            return self.side.is_sell()

        def is_active(self) -> bool:
            """Check if order is in active state."""
            return self.status.is_active() if self.status else False

        def is_final(self) -> bool:
            """Check if order is in final state."""
            return self.status.is_final() if self.status else False

        def can_cancel(self) -> bool:
            """Check if order can be canceled."""
            return self.status.can_cancel() if self.status else False

    # Export both classes
    __all__ = ["Order", "OrderWithValueObjects"]
else:
    __all__ = ["Order"]
