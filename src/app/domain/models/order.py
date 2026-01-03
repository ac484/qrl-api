"""Order entity for domain workflows.

DDD Entity Pattern:
- Entity: Has identity (order_id), can change state through methods
- Encapsulates business rules and state transitions
- Uses Value Objects for domain concepts
- State changes only through behavior methods

This is a pure DDD implementation without backward compatibility compromises.
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.app.domain.value_objects import (
    OrderSide,
    OrderStatus,
    OrderStatusEnum,
    Price,
    Quantity,
    Symbol,
)


@dataclass(slots=True)
class Order:
    """Order entity using DDD value objects.

    Entity Characteristics:
    - Has identity via order_id (required)
    - Encapsulates state and behavior
    - State changes through methods only
    - Uses value objects for domain concepts

    The Order entity represents a trading order with its complete lifecycle.
    All domain rules and state transitions are enforced through methods.

    Attributes:
        order_id: Unique order identifier (entity identity, required)
        symbol: Trading pair (immutable value object)
        side: Order direction BUY/SELL (immutable value object)
        quantity: Amount to trade (immutable value object)
        price: Order price (immutable value object, None for market orders)
        status: Order lifecycle state (managed through state transition methods)
        created_at: Order creation timestamp
        filled_quantity: Amount filled so far (for partial fills)

    Example:
        >>> from src.app.domain.value_objects import Symbol, OrderSide, Quantity, Price
        >>> order = Order(
        ...     order_id="12345",
        ...     symbol=Symbol("QRLUSDT"),
        ...     side=OrderSide.buy(),
        ...     quantity=Quantity.from_float(10.0),
        ...     price=Price.from_float(100.5, "USDT"),
        ... )
        >>> order.is_buy()
        True
        >>> order.fill(Quantity.from_float(10.0), Price.from_float(100.5, "USDT"))
        >>> order.is_filled()
        True
    """

    order_id: str  # Entity identity - required
    symbol: Symbol
    side: OrderSide
    quantity: Quantity
    price: Optional[Price] = None
    status: OrderStatus = field(default_factory=OrderStatus.new)
    created_at: datetime = field(default_factory=datetime.utcnow)
    _filled_quantity: Decimal = field(default=Decimal("0"))

    def __post_init__(self) -> None:
        """Validate entity invariants on creation."""
        if not self.order_id:
            raise ValueError("Order must have an order_id (entity identity)")

        # Ensure filled_quantity doesn't exceed total quantity
        if self._filled_quantity > self.quantity.value:
            raise ValueError(
                f"Filled quantity ({self._filled_quantity}) cannot exceed "
                f"total quantity ({self.quantity.value})"
            )

    @property
    def filled_quantity(self) -> Quantity:
        """Get filled quantity as a Quantity value object.
        
        Returns Quantity even if zero (for consistency).
        """
        # For zero, we bypass the validation since it's a special case
        # In a real implementation, consider creating a special "ZeroQuantity" type
        if self._filled_quantity == 0:
            # Create Quantity with zero by temporarily bypassing validation
            # This is acceptable for filled_quantity tracking
            qty = object.__new__(Quantity)
            object.__setattr__(qty, "value", Decimal("0"))
            return qty
        return Quantity(self._filled_quantity)

    # Read-only properties (behavior over data)

    @property
    def remaining_quantity(self) -> Quantity:
        """Calculate remaining unfilled quantity."""
        remaining_value = self.quantity.value - self._filled_quantity
        if remaining_value == 0:
            # Create zero Quantity for remaining (bypass validation)
            qty = object.__new__(Quantity)
            object.__setattr__(qty, "value", Decimal("0"))
            return qty
        return Quantity(remaining_value)

    @property
    def is_fully_filled(self) -> bool:
        """Check if order is completely filled."""
        return self._filled_quantity >= self.quantity.value

    @property
    def is_partially_filled(self) -> bool:
        """Check if order is partially filled."""
        return (
            self._filled_quantity > Decimal("0")
            and self._filled_quantity < self.quantity.value
        )

    @property
    def total_value(self) -> Optional[Price]:
        """Calculate total order value (price * quantity).

        Returns None for market orders (no price).
        """
        if self.price is None:
            return None
        return self.price.multiply(Decimal(str(float(self.quantity))))

    # Query methods (behavior)

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
        """Check if order is in active state (can be filled or canceled)."""
        return self.status.is_active()

    def is_filled(self) -> bool:
        """Check if order is completely filled."""
        return self.status.value == OrderStatusEnum.FILLED

    def is_canceled(self) -> bool:
        """Check if order is canceled."""
        return self.status.value == OrderStatusEnum.CANCELED

    def is_final(self) -> bool:
        """Check if order is in final state (cannot be modified)."""
        return self.status.is_final()

    # State transition methods (commands)

    def fill(self, filled_qty: Quantity, execution_price: Price) -> None:
        """Fill the order completely.

        Args:
            filled_qty: Quantity that was filled
            execution_price: Price at which order was executed

        Raises:
            ValueError: If order cannot be filled or filled_qty invalid
        """
        if self.is_final():
            raise ValueError(f"Cannot fill order in final state: {self.status}")

        if filled_qty > self.quantity:
            raise ValueError(
                f"Fill quantity ({filled_qty}) exceeds order quantity ({self.quantity})"
            )

        # For limit orders, validate execution price matches
        if self.price is not None:
            if self.is_buy() and execution_price > self.price:
                raise ValueError(
                    f"Buy execution price ({execution_price}) exceeds "
                    f"limit price ({self.price})"
                )
            if self.is_sell() and execution_price < self.price:
                raise ValueError(
                    f"Sell execution price ({execution_price}) below "
                    f"limit price ({self.price})"
                )

        object.__setattr__(self, "_filled_quantity", filled_qty.value)
        object.__setattr__(self, "status", OrderStatus.filled())

    def partial_fill(self, filled_qty: Quantity, execution_price: Price) -> None:
        """Partially fill the order.

        Args:
            filled_qty: Additional quantity that was filled
            execution_price: Price at which this portion was executed

        Raises:
            ValueError: If order cannot be filled or filled_qty invalid
        """
        if self.is_final():
            raise ValueError(f"Cannot fill order in final state: {self.status}")

        new_filled = self._filled_quantity + filled_qty.value
        if new_filled > self.quantity.value:
            raise ValueError(
                f"Total fill ({new_filled}) would exceed order quantity ({self.quantity})"
            )

        # For limit orders, validate execution price
        if self.price is not None:
            if self.is_buy() and execution_price > self.price:
                raise ValueError(
                    f"Buy execution price ({execution_price}) exceeds "
                    f"limit price ({self.price})"
                )
            if self.is_sell() and execution_price < self.price:
                raise ValueError(
                    f"Sell execution price ({execution_price}) below "
                    f"limit price ({self.price})"
                )

        object.__setattr__(self, "_filled_quantity", new_filled)

        # Update status based on fill level
        if self.is_fully_filled:
            object.__setattr__(self, "status", OrderStatus.filled())
        else:
            object.__setattr__(self, "status", OrderStatus.partially_filled())

    def cancel(self) -> None:
        """Cancel the order.

        Raises:
            ValueError: If order cannot be canceled
        """
        if not self.status.can_cancel():
            raise ValueError(f"Cannot cancel order in state: {self.status}")

        object.__setattr__(self, "status", OrderStatus.canceled())

    def reject(self, reason: str = "") -> None:
        """Reject the order.

        Args:
            reason: Optional rejection reason

        Raises:
            ValueError: If order is already in a final state
        """
        if self.is_final():
            raise ValueError(f"Cannot reject order in final state: {self.status}")

        object.__setattr__(self, "status", OrderStatus.rejected())

    def expire(self) -> None:
        """Mark order as expired.

        Raises:
            ValueError: If order is already in a final state
        """
        if self.is_final():
            raise ValueError(f"Cannot expire order in final state: {self.status}")

        object.__setattr__(self, "status", OrderStatus(OrderStatusEnum.EXPIRED))

    # Serialization (minimal - only for external API/persistence)

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization.

        Use only for API responses or database persistence.
        Do not use for domain logic.
        """
        return {
            "order_id": self.order_id,
            "symbol": self.symbol.value,
            "side": str(self.side),
            "quantity": float(self.quantity),
            "price": float(self.price) if self.price else None,
            "status": str(self.status),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "filled_quantity": float(self.filled_quantity),
            "remaining_quantity": float(self.remaining_quantity),
            "total_value": float(self.total_value) if self.total_value else None,
        }


__all__ = ["Order"]
