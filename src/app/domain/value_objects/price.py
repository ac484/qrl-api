"""Price value object for monetary values.

Represents a price with validation and currency awareness.
Immutable and comparable by value as per DDD value object pattern.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Price:
    """Price value object with validation.

    A value object representing a monetary price. Uses Decimal for precise
    financial calculations. Two prices with the same value and currency are
    considered equal.

    Attributes:
        value: The numeric price value (as Decimal for precision)
        currency: The currency code (e.g., "USDT", "USD")

    Examples:
        >>> price = Price(Decimal("100.50"), "USDT")
        >>> price.value
        Decimal('100.50')

        >>> # Convenience factory for float values
        >>> price = Price.from_float(100.5, "USDT")
        >>> price.value
        Decimal('100.5')

        >>> # Immutable - this will raise an error
        >>> price.value = Decimal("200")  # FrozenInstanceError
    """

    value: Decimal
    currency: str = "USDT"

    def __post_init__(self) -> None:
        """Validate price on creation."""
        if not isinstance(self.value, Decimal):
            raise TypeError(f"Price value must be Decimal, got {type(self.value)}")

        if self.value < 0:
            raise ValueError(f"Price cannot be negative: {self.value}")

        if not self.currency:
            raise ValueError("Currency cannot be empty")

        if not self.currency.isupper():
            raise ValueError(f"Currency must be uppercase: {self.currency}")

    def __str__(self) -> str:
        """String representation of the price."""
        return f"{self.value} {self.currency}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Price(Decimal('{self.value}'), '{self.currency}')"

    def __float__(self) -> float:
        """Convert to float for compatibility."""
        return float(self.value)

    def __lt__(self, other: "Price") -> bool:
        """Less than comparison."""
        self._check_currency_match(other)
        return self.value < other.value

    def __le__(self, other: "Price") -> bool:
        """Less than or equal comparison."""
        self._check_currency_match(other)
        return self.value <= other.value

    def __gt__(self, other: "Price") -> bool:
        """Greater than comparison."""
        self._check_currency_match(other)
        return self.value > other.value

    def __ge__(self, other: "Price") -> bool:
        """Greater than or equal comparison."""
        self._check_currency_match(other)
        return self.value >= other.value

    def _check_currency_match(self, other: "Price") -> None:
        """Ensure currencies match for comparison."""
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot compare prices with different currencies: "
                f"{self.currency} vs {other.currency}"
            )

    @classmethod
    def from_float(cls, value: float, currency: str = "USDT") -> "Price":
        """Create a price from a float value.

        Args:
            value: The price as a float
            currency: The currency code

        Returns:
            Price instance

        Example:
            >>> price = Price.from_float(100.5, "USDT")
            >>> price.value
            Decimal('100.5')
        """
        return cls(value=Decimal(str(value)), currency=currency)

    @classmethod
    def from_string(cls, value: str, currency: str = "USDT") -> "Price":
        """Create a price from a string value.

        Args:
            value: The price as a string
            currency: The currency code

        Returns:
            Price instance

        Example:
            >>> price = Price.from_string("100.50", "USDT")
            >>> price.value
            Decimal('100.50')
        """
        return cls(value=Decimal(value), currency=currency)

    def multiply(self, factor: Decimal) -> "Price":
        """Multiply price by a factor, returning a new Price.

        Args:
            factor: Multiplication factor

        Returns:
            New Price instance

        Example:
            >>> price = Price.from_float(100.0, "USDT")
            >>> doubled = price.multiply(Decimal("2"))
            >>> doubled.value
            Decimal('200.0')
        """
        return Price(value=self.value * factor, currency=self.currency)

    def add(self, other: "Price") -> "Price":
        """Add two prices, returning a new Price.

        Args:
            other: Another Price to add

        Returns:
            New Price instance

        Example:
            >>> price1 = Price.from_float(100.0, "USDT")
            >>> price2 = Price.from_float(50.0, "USDT")
            >>> total = price1.add(price2)
            >>> total.value
            Decimal('150.0')
        """
        self._check_currency_match(other)
        return Price(value=self.value + other.value, currency=self.currency)

    def is_zero(self) -> bool:
        """Check if price is zero.

        Returns:
            True if price is zero
        """
        return self.value == 0


__all__ = ["Price"]
