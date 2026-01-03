"""Quantity value object for trading amounts.

Represents a quantity/amount with validation.
Immutable and comparable by value as per DDD value object pattern.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Quantity:
    """Quantity value object with validation.

    A value object representing a trading quantity. Uses Decimal for precise
    calculations. Two quantities with the same value are considered equal.

    Attributes:
        value: The numeric quantity value (as Decimal for precision)

    Examples:
        >>> qty = Quantity(Decimal("10.5"))
        >>> qty.value
        Decimal('10.5')

        >>> # Convenience factory for float values
        >>> qty = Quantity.from_float(10.5)
        >>> qty.value
        Decimal('10.5')

        >>> # Immutable - this will raise an error
        >>> qty.value = Decimal("20")  # FrozenInstanceError
    """

    value: Decimal

    def __post_init__(self) -> None:
        """Validate quantity on creation."""
        if not isinstance(self.value, Decimal):
            raise TypeError(f"Quantity value must be Decimal, got {type(self.value)}")

        if self.value <= 0:
            raise ValueError(f"Quantity must be positive: {self.value}")

    def __str__(self) -> str:
        """String representation of the quantity."""
        return str(self.value)

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Quantity(Decimal('{self.value}'))"

    def __float__(self) -> float:
        """Convert to float for compatibility."""
        return float(self.value)

    def __lt__(self, other: "Quantity") -> bool:
        """Less than comparison."""
        return self.value < other.value

    def __le__(self, other: "Quantity") -> bool:
        """Less than or equal comparison."""
        return self.value <= other.value

    def __gt__(self, other: "Quantity") -> bool:
        """Greater than comparison."""
        return self.value > other.value

    def __ge__(self, other: "Quantity") -> bool:
        """Greater than or equal comparison."""
        return self.value >= other.value

    @classmethod
    def from_float(cls, value: float) -> "Quantity":
        """Create a quantity from a float value.

        Args:
            value: The quantity as a float

        Returns:
            Quantity instance

        Example:
            >>> qty = Quantity.from_float(10.5)
            >>> qty.value
            Decimal('10.5')
        """
        return cls(value=Decimal(str(value)))

    @classmethod
    def from_string(cls, value: str) -> "Quantity":
        """Create a quantity from a string value.

        Args:
            value: The quantity as a string

        Returns:
            Quantity instance

        Example:
            >>> qty = Quantity.from_string("10.50")
            >>> qty.value
            Decimal('10.50')
        """
        return cls(value=Decimal(value))

    def multiply(self, factor: Decimal) -> "Quantity":
        """Multiply quantity by a factor, returning a new Quantity.

        Args:
            factor: Multiplication factor

        Returns:
            New Quantity instance

        Example:
            >>> qty = Quantity.from_float(10.0)
            >>> doubled = qty.multiply(Decimal("2"))
            >>> doubled.value
            Decimal('20.0')
        """
        return Quantity(value=self.value * factor)

    def add(self, other: "Quantity") -> "Quantity":
        """Add two quantities, returning a new Quantity.

        Args:
            other: Another Quantity to add

        Returns:
            New Quantity instance

        Example:
            >>> qty1 = Quantity.from_float(10.0)
            >>> qty2 = Quantity.from_float(5.0)
            >>> total = qty1.add(qty2)
            >>> total.value
            Decimal('15.0')
        """
        return Quantity(value=self.value + other.value)

    def subtract(self, other: "Quantity") -> "Quantity":
        """Subtract a quantity from this one, returning a new Quantity.

        Args:
            other: Another Quantity to subtract

        Returns:
            New Quantity instance

        Raises:
            ValueError: If result would be negative or zero

        Example:
            >>> qty1 = Quantity.from_float(10.0)
            >>> qty2 = Quantity.from_float(5.0)
            >>> result = qty1.subtract(qty2)
            >>> result.value
            Decimal('5.0')
        """
        result = self.value - other.value
        if result <= 0:
            raise ValueError(
                f"Quantity subtraction would result in non-positive value: {result}"
            )
        return Quantity(value=result)


__all__ = ["Quantity"]
