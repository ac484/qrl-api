"""OrderSide value object for buy/sell direction.

Represents the side of an order with validation.
Immutable and comparable by value as per DDD value object pattern.
"""

from dataclasses import dataclass
from enum import Enum


class OrderSideEnum(str, Enum):
    """Enumeration of valid order sides."""

    BUY = "BUY"
    SELL = "SELL"


@dataclass(frozen=True, slots=True)
class OrderSide:
    """Order side value object with validation.

    A value object representing the direction of an order (BUY or SELL).
    Two order sides with the same value are considered equal.

    Attributes:
        value: The order side (BUY or SELL)

    Examples:
        >>> side = OrderSide(OrderSideEnum.BUY)
        >>> side.value
        <OrderSideEnum.BUY: 'BUY'>

        >>> side = OrderSide.buy()
        >>> side.is_buy()
        True

        >>> side = OrderSide.sell()
        >>> side.is_sell()
        True

        >>> # Immutable - this will raise an error
        >>> side.value = OrderSideEnum.SELL  # FrozenInstanceError
    """

    value: OrderSideEnum

    def __post_init__(self) -> None:
        """Validate order side on creation."""
        if not isinstance(self.value, OrderSideEnum):
            raise TypeError(
                f"OrderSide value must be OrderSideEnum, got {type(self.value)}"
            )

    def __str__(self) -> str:
        """String representation of the order side."""
        return self.value.value

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"OrderSide({self.value})"

    @classmethod
    def buy(cls) -> "OrderSide":
        """Create a BUY order side.

        Returns:
            OrderSide instance for BUY

        Example:
            >>> side = OrderSide.buy()
            >>> side.is_buy()
            True
        """
        return cls(value=OrderSideEnum.BUY)

    @classmethod
    def sell(cls) -> "OrderSide":
        """Create a SELL order side.

        Returns:
            OrderSide instance for SELL

        Example:
            >>> side = OrderSide.sell()
            >>> side.is_sell()
            True
        """
        return cls(value=OrderSideEnum.SELL)

    @classmethod
    def from_string(cls, value: str) -> "OrderSide":
        """Create an order side from a string value.

        Args:
            value: The order side as a string ("BUY" or "SELL")

        Returns:
            OrderSide instance

        Raises:
            ValueError: If value is not a valid order side

        Example:
            >>> side = OrderSide.from_string("BUY")
            >>> side.is_buy()
            True
        """
        try:
            return cls(value=OrderSideEnum(value.upper()))
        except ValueError:
            raise ValueError(f"Invalid order side: {value}. Must be 'BUY' or 'SELL'")

    def is_buy(self) -> bool:
        """Check if this is a BUY order side.

        Returns:
            True if BUY, False otherwise
        """
        return self.value == OrderSideEnum.BUY

    def is_sell(self) -> bool:
        """Check if this is a SELL order side.

        Returns:
            True if SELL, False otherwise
        """
        return self.value == OrderSideEnum.SELL

    def opposite(self) -> "OrderSide":
        """Get the opposite order side.

        Returns:
            OrderSide instance for the opposite side

        Example:
            >>> buy = OrderSide.buy()
            >>> sell = buy.opposite()
            >>> sell.is_sell()
            True
        """
        if self.is_buy():
            return OrderSide.sell()
        return OrderSide.buy()


__all__ = ["OrderSide", "OrderSideEnum"]
