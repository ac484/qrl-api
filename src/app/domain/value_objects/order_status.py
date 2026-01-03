"""OrderStatus value object for order state tracking.

Represents the status of an order with validation.
Immutable and comparable by value as per DDD value object pattern.
"""

from dataclasses import dataclass
from enum import Enum


class OrderStatusEnum(str, Enum):
    """Enumeration of valid order statuses.

    Based on MEXC API order status values and common trading system states.
    """

    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass(frozen=True, slots=True)
class OrderStatus:
    """Order status value object with validation.

    A value object representing the current state of an order.
    Two order statuses with the same value are considered equal.

    Attributes:
        value: The order status

    Examples:
        >>> status = OrderStatus(OrderStatusEnum.NEW)
        >>> status.value
        <OrderStatusEnum.NEW: 'NEW'>

        >>> status = OrderStatus.new()
        >>> status.is_new()
        True

        >>> status = OrderStatus.filled()
        >>> status.is_final()
        True

        >>> # Immutable - this will raise an error
        >>> status.value = OrderStatusEnum.FILLED  # FrozenInstanceError
    """

    value: OrderStatusEnum

    def __post_init__(self) -> None:
        """Validate order status on creation."""
        if not isinstance(self.value, OrderStatusEnum):
            raise TypeError(
                f"OrderStatus value must be OrderStatusEnum, got {type(self.value)}"
            )

    def __str__(self) -> str:
        """String representation of the order status."""
        return self.value.value

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"OrderStatus({self.value})"

    @classmethod
    def new(cls) -> "OrderStatus":
        """Create a NEW order status.

        Returns:
            OrderStatus instance for NEW
        """
        return cls(value=OrderStatusEnum.NEW)

    @classmethod
    def partially_filled(cls) -> "OrderStatus":
        """Create a PARTIALLY_FILLED order status.

        Returns:
            OrderStatus instance for PARTIALLY_FILLED
        """
        return cls(value=OrderStatusEnum.PARTIALLY_FILLED)

    @classmethod
    def filled(cls) -> "OrderStatus":
        """Create a FILLED order status.

        Returns:
            OrderStatus instance for FILLED
        """
        return cls(value=OrderStatusEnum.FILLED)

    @classmethod
    def canceled(cls) -> "OrderStatus":
        """Create a CANCELED order status.

        Returns:
            OrderStatus instance for CANCELED
        """
        return cls(value=OrderStatusEnum.CANCELED)

    @classmethod
    def rejected(cls) -> "OrderStatus":
        """Create a REJECTED order status.

        Returns:
            OrderStatus instance for REJECTED
        """
        return cls(value=OrderStatusEnum.REJECTED)

    @classmethod
    def from_string(cls, value: str) -> "OrderStatus":
        """Create an order status from a string value.

        Args:
            value: The order status as a string

        Returns:
            OrderStatus instance

        Raises:
            ValueError: If value is not a valid order status

        Example:
            >>> status = OrderStatus.from_string("FILLED")
            >>> status.is_filled()
            True
        """
        try:
            return cls(value=OrderStatusEnum(value.upper()))
        except ValueError:
            raise ValueError(
                f"Invalid order status: {value}. Must be one of: "
                f"{', '.join([s.value for s in OrderStatusEnum])}"
            )

    def is_new(self) -> bool:
        """Check if this is a NEW order status."""
        return self.value == OrderStatusEnum.NEW

    def is_partially_filled(self) -> bool:
        """Check if this is a PARTIALLY_FILLED order status."""
        return self.value == OrderStatusEnum.PARTIALLY_FILLED

    def is_filled(self) -> bool:
        """Check if this is a FILLED order status."""
        return self.value == OrderStatusEnum.FILLED

    def is_canceled(self) -> bool:
        """Check if this is a CANCELED order status."""
        return self.value == OrderStatusEnum.CANCELED

    def is_rejected(self) -> bool:
        """Check if this is a REJECTED order status."""
        return self.value == OrderStatusEnum.REJECTED

    def is_expired(self) -> bool:
        """Check if this is an EXPIRED order status."""
        return self.value == OrderStatusEnum.EXPIRED

    def is_active(self) -> bool:
        """Check if order is in an active state (can still be executed or modified).

        Returns:
            True if order is NEW, PARTIALLY_FILLED, or PENDING_CANCEL
        """
        return self.value in {
            OrderStatusEnum.NEW,
            OrderStatusEnum.PARTIALLY_FILLED,
            OrderStatusEnum.PENDING_CANCEL,
        }

    def is_final(self) -> bool:
        """Check if order is in a final state (cannot be modified further).

        Returns:
            True if order is FILLED, CANCELED, REJECTED, or EXPIRED
        """
        return self.value in {
            OrderStatusEnum.FILLED,
            OrderStatusEnum.CANCELED,
            OrderStatusEnum.REJECTED,
            OrderStatusEnum.EXPIRED,
        }

    def can_cancel(self) -> bool:
        """Check if order can be canceled.

        Returns:
            True if order is NEW or PARTIALLY_FILLED
        """
        return self.value in {
            OrderStatusEnum.NEW,
            OrderStatusEnum.PARTIALLY_FILLED,
        }


__all__ = ["OrderStatus", "OrderStatusEnum"]
