"""Symbol value object for trading pairs.

Represents a trading pair symbol (e.g., QRLUSDT, BTCUSDT) with validation.
Immutable and comparable by value as per DDD value object pattern.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class Symbol:
    """Trading pair symbol with validation.

    A value object representing a trading symbol. Two symbols with the same
    value are considered equal, regardless of instance identity.

    Attributes:
        value: The symbol string (e.g., "QRLUSDT", "BTCUSDT")
        base: Optional base asset (e.g., "QRL" in "QRLUSDT")
        quote: Optional quote asset (e.g., "USDT" in "QRLUSDT")

    Examples:
        >>> symbol = Symbol("QRLUSDT")
        >>> symbol.value
        'QRLUSDT'

        >>> symbol_with_parts = Symbol("BTCUSDT", base="BTC", quote="USDT")
        >>> symbol_with_parts.base
        'BTC'

        >>> # Immutable - this will raise an error
        >>> symbol.value = "NEWVALUE"  # FrozenInstanceError
    """

    value: str
    base: Optional[str] = None
    quote: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate symbol on creation."""
        if not self.value:
            raise ValueError("Symbol value cannot be empty")

        if not self.value.isupper():
            raise ValueError(f"Symbol must be uppercase: {self.value}")

        if len(self.value) < 3:
            raise ValueError(f"Symbol too short: {self.value}")

        if not self.value.isalnum():
            raise ValueError(f"Symbol must be alphanumeric: {self.value}")

    def __str__(self) -> str:
        """String representation of the symbol."""
        return self.value

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        if self.base and self.quote:
            return f"Symbol('{self.value}', base='{self.base}', quote='{self.quote}')"
        return f"Symbol('{self.value}')"

    @classmethod
    def from_parts(cls, base: str, quote: str) -> "Symbol":
        """Create a symbol from base and quote assets.

        Args:
            base: Base asset (e.g., "QRL")
            quote: Quote asset (e.g., "USDT")

        Returns:
            Symbol instance

        Example:
            >>> symbol = Symbol.from_parts("QRL", "USDT")
            >>> symbol.value
            'QRLUSDT'
        """
        return cls(value=f"{base}{quote}", base=base, quote=quote)


__all__ = ["Symbol"]
