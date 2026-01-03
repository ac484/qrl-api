"""Balance Value Object representing asset amounts.

DDD Value Object Pattern:
- No identity (asset is the discriminator, not an ID)
- Immutable (frozen dataclass)
- Value equality
- Validated on construction
- Conceptual (represents amount of an asset)

Balance is NOT an entity because:
- Two balances with same asset/amounts are considered equal (value equality)
- No lifecycle or state transitions
- Represents a concept/amount, not a tracked thing

Example:
    >>> balance = Balance.from_float("USDT", 1000.0, 50.0)
    >>> balance.total
    Decimal('1050.0')
    >>> balance.asset
    'USDT'
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import ClassVar


@dataclass(frozen=True, slots=True)
class Balance:
    """Balance represents amount of an asset (Value Object).

    Characteristics:
    - No identity (asset is used as key, not an ID)
    - Immutable (frozen=True)
    - Value equality (two balances with same values are equal)
    - Validated (non-negative amounts, required asset)
    - Represents a concept/amount

    Attributes:
        asset: Asset symbol (e.g., "USDT", "QRL", "BTC")
        free: Available amount for trading
        locked: Amount locked in open orders

    Example:
        >>> balance = Balance.from_float("USDT", 1000.0, 50.0)
        >>> balance.free
        Decimal('1000.0')
        >>> balance.locked
        Decimal('50.0')
        >>> balance.total
        Decimal('1050.0')

    Raises:
        ValueError: If asset is empty or amounts are negative
    """

    asset: str
    free: Decimal
    locked: Decimal = Decimal("0")

    # Class constants
    ZERO: ClassVar[Decimal] = Decimal("0")

    def __post_init__(self) -> None:
        """Validate balance invariants."""
        if not self.asset or not self.asset.strip():
            raise ValueError("Asset symbol required")

        if self.free < self.ZERO:
            raise ValueError(f"Free balance cannot be negative: {self.free}")

        if self.locked < self.ZERO:
            raise ValueError(f"Locked balance cannot be negative: {self.locked}")

    @property
    def total(self) -> Decimal:
        """Total balance (free + locked)."""
        return self.free + self.locked

    @classmethod
    def from_float(
        cls, asset: str, free: float, locked: float = 0.0
    ) -> "Balance":
        """Create Balance from float values.

        Args:
            asset: Asset symbol
            free: Free balance amount
            locked: Locked balance amount (default: 0.0)

        Returns:
            Balance instance with Decimal precision

        Example:
            >>> balance = Balance.from_float("USDT", 1000.0, 50.0)
            >>> balance.total
            Decimal('1050.0')
        """
        return cls(
            asset=asset,
            free=Decimal(str(free)),
            locked=Decimal(str(locked)),
        )

    @classmethod
    def zero(cls, asset: str) -> "Balance":
        """Create zero balance for an asset.

        Args:
            asset: Asset symbol

        Returns:
            Balance with zero free and locked amounts

        Example:
            >>> balance = Balance.zero("USDT")
            >>> balance.total
            Decimal('0')
        """
        return cls(asset=asset, free=Decimal("0"), locked=Decimal("0"))

    def add_free(self, amount: Decimal) -> "Balance":
        """Return new Balance with additional free amount.

        Args:
            amount: Amount to add to free balance

        Returns:
            New Balance instance (immutable)

        Example:
            >>> balance = Balance.from_float("USDT", 1000.0)
            >>> new_balance = balance.add_free(Decimal("500"))
            >>> new_balance.free
            Decimal('1500.0')
        """
        if amount < self.ZERO:
            raise ValueError(f"Cannot add negative amount: {amount}")
        return Balance(
            asset=self.asset, free=self.free + amount, locked=self.locked
        )

    def subtract_free(self, amount: Decimal) -> "Balance":
        """Return new Balance with reduced free amount.

        Args:
            amount: Amount to subtract from free balance

        Returns:
            New Balance instance (immutable)

        Raises:
            ValueError: If subtraction would result in negative free balance

        Example:
            >>> balance = Balance.from_float("USDT", 1000.0)
            >>> new_balance = balance.subtract_free(Decimal("500"))
            >>> new_balance.free
            Decimal('500.0')
        """
        if amount < self.ZERO:
            raise ValueError(f"Cannot subtract negative amount: {amount}")
        new_free = self.free - amount
        if new_free < self.ZERO:
            raise ValueError(
                f"Insufficient free balance. Available: {self.free}, Requested: {amount}"
            )
        return Balance(asset=self.asset, free=new_free, locked=self.locked)

    def lock(self, amount: Decimal) -> "Balance":
        """Return new Balance with amount moved from free to locked.

        Args:
            amount: Amount to lock

        Returns:
            New Balance instance (immutable)

        Raises:
            ValueError: If insufficient free balance

        Example:
            >>> balance = Balance.from_float("USDT", 1000.0)
            >>> new_balance = balance.lock(Decimal("100"))
            >>> new_balance.free
            Decimal('900.0')
            >>> new_balance.locked
            Decimal('100.0')
        """
        if amount < self.ZERO:
            raise ValueError(f"Cannot lock negative amount: {amount}")
        if amount > self.free:
            raise ValueError(
                f"Insufficient free balance to lock. Available: {self.free}, Requested: {amount}"
            )
        return Balance(
            asset=self.asset,
            free=self.free - amount,
            locked=self.locked + amount,
        )

    def unlock(self, amount: Decimal) -> "Balance":
        """Return new Balance with amount moved from locked to free.

        Args:
            amount: Amount to unlock

        Returns:
            New Balance instance (immutable)

        Raises:
            ValueError: If insufficient locked balance

        Example:
            >>> balance = Balance.from_float("USDT", 1000.0, 100.0)
            >>> new_balance = balance.unlock(Decimal("50"))
            >>> new_balance.free
            Decimal('1050.0')
            >>> new_balance.locked
            Decimal('50.0')
        """
        if amount < self.ZERO:
            raise ValueError(f"Cannot unlock negative amount: {amount}")
        if amount > self.locked:
            raise ValueError(
                f"Insufficient locked balance to unlock. Locked: {self.locked}, Requested: {amount}"
            )
        return Balance(
            asset=self.asset,
            free=self.free + amount,
            locked=self.locked - amount,
        )


__all__ = ["Balance"]
