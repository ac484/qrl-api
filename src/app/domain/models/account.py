"""Account entity managing user balances (Aggregate Root).

DDD Entity Pattern:
- Entity: Has identity (account_id), can change state
- Aggregate Root: Manages Balance value objects
- Encapsulates balance operations and invariants
- Uses Value Objects for domain concepts

Account is an Entity (and Aggregate Root) because:
- Has unique identity (account_id)
- Manages lifecycle of Balance VOs
- Enforces invariants (no negative balances)
- Changes state through controlled methods

Example:
    >>> from src.app.domain.value_objects import Balance
    >>> from decimal import Decimal
    >>> account = Account(account_id="A12345")
    >>> account.deposit("USDT", Decimal("1000.0"))
    >>> account.get_balance("USDT").free
    Decimal('1000.0')
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict

from src.app.domain.value_objects import Balance


@dataclass(slots=True)
class Account:
    """Account entity managing user balances (Aggregate Root).
    
    Entity/Aggregate Root Characteristics:
    - Has identity (account_id required)
    - Manages Balance value objects (aggregate)
    - Encapsulates balance operations
    - Enforces invariants through methods
    
    The Account entity is the aggregate root for balance management,
    ensuring all balance operations maintain consistency.
    
    Attributes:
        account_id: Unique account identifier (entity identity, required)
        _balances: Internal balance storage (managed through methods)
    
    Example:
        >>> account = Account(account_id="A12345")
        >>> account.deposit("USDT", Decimal("1000.0"))
        >>> balance = account.get_balance("USDT")
        >>> balance.free
        Decimal('1000.0')
        >>> account.lock_for_order("USDT", Decimal("100.0"))
        >>> balance = account.get_balance("USDT")
        >>> balance.locked
        Decimal('100.0')
    """

    account_id: str  # Entity identity - required
    _balances: Dict[str, Balance] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate entity invariants on creation."""
        if not self.account_id:
            raise ValueError("Account must have an account_id (entity identity)")

    def get_balance(self, asset: str) -> Balance:
        """Get balance for an asset.
        
        Args:
            asset: Asset symbol
        
        Returns:
            Balance VO (zero balance if asset not found)
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> balance = account.get_balance("USDT")
            >>> balance.total
            Decimal('0')
        """
        return self._balances.get(asset, Balance.zero(asset))

    def deposit(self, asset: str, amount: Decimal) -> None:
        """Deposit amount to free balance.
        
        Args:
            asset: Asset symbol
            amount: Amount to deposit
        
        Raises:
            ValueError: If amount is negative
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> account.deposit("USDT", Decimal("1000.0"))
            >>> account.get_balance("USDT").free
            Decimal('1000.0')
        """
        if amount < Decimal("0"):
            raise ValueError(f"Cannot deposit negative amount: {amount}")
        
        current_balance = self.get_balance(asset)
        new_balance = current_balance.add_free(amount)
        self._balances[asset] = new_balance

    def withdraw(self, asset: str, amount: Decimal) -> None:
        """Withdraw amount from free balance.
        
        Args:
            asset: Asset symbol
            amount: Amount to withdraw
        
        Raises:
            ValueError: If insufficient free balance
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> account.deposit("USDT", Decimal("1000.0"))
            >>> account.withdraw("USDT", Decimal("500.0"))
            >>> account.get_balance("USDT").free
            Decimal('500.0')
        """
        if amount < Decimal("0"):
            raise ValueError(f"Cannot withdraw negative amount: {amount}")
        
        current_balance = self.get_balance(asset)
        new_balance = current_balance.subtract_free(amount)
        self._balances[asset] = new_balance

    def lock_for_order(self, asset: str, amount: Decimal) -> None:
        """Lock amount for an open order (move from free to locked).
        
        Args:
            asset: Asset symbol
            amount: Amount to lock
        
        Raises:
            ValueError: If insufficient free balance
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> account.deposit("USDT", Decimal("1000.0"))
            >>> account.lock_for_order("USDT", Decimal("100.0"))
            >>> balance = account.get_balance("USDT")
            >>> balance.free
            Decimal('900.0')
            >>> balance.locked
            Decimal('100.0')
        """
        if amount < Decimal("0"):
            raise ValueError(f"Cannot lock negative amount: {amount}")
        
        current_balance = self.get_balance(asset)
        new_balance = current_balance.lock(amount)
        self._balances[asset] = new_balance

    def unlock_from_order(self, asset: str, amount: Decimal) -> None:
        """Unlock amount from cancelled order (move from locked to free).
        
        Args:
            asset: Asset symbol
            amount: Amount to unlock
        
        Raises:
            ValueError: If insufficient locked balance
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> account.deposit("USDT", Decimal("1000.0"))
            >>> account.lock_for_order("USDT", Decimal("100.0"))
            >>> account.unlock_from_order("USDT", Decimal("100.0"))
            >>> account.get_balance("USDT").free
            Decimal('1000.0')
        """
        if amount < Decimal("0"):
            raise ValueError(f"Cannot unlock negative amount: {amount}")
        
        current_balance = self.get_balance(asset)
        new_balance = current_balance.unlock(amount)
        self._balances[asset] = new_balance

    def release_locked(self, asset: str, amount: Decimal) -> None:
        """Release locked amount (consumed by filled order).
        
        Args:
            asset: Asset symbol
            amount: Amount to release
        
        Raises:
            ValueError: If insufficient locked balance
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> account.deposit("USDT", Decimal("1000.0"))
            >>> account.lock_for_order("USDT", Decimal("100.0"))
            >>> account.release_locked("USDT", Decimal("100.0"))
            >>> balance = account.get_balance("USDT")
            >>> balance.total
            Decimal('900.0')
        """
        if amount < Decimal("0"):
            raise ValueError(f"Cannot release negative amount: {amount}")
        
        current_balance = self.get_balance(asset)
        if amount > current_balance.locked:
            raise ValueError(
                f"Cannot release {amount} - only {current_balance.locked} locked"
            )
        
        # Release by reducing locked amount
        new_balance = Balance(
            asset=asset,
            free=current_balance.free,
            locked=current_balance.locked - amount,
        )
        self._balances[asset] = new_balance

    def get_all_balances(self) -> Dict[str, Balance]:
        """Get all non-zero balances.
        
        Returns:
            Dictionary of asset -> Balance
        
        Example:
            >>> account = Account(account_id="A12345")
            >>> account.deposit("USDT", Decimal("1000.0"))
            >>> account.deposit("QRL", Decimal("500.0"))
            >>> balances = account.get_all_balances()
            >>> len(balances)
            2
        """
        return {
            asset: balance
            for asset, balance in self._balances.items()
            if balance.total > Decimal("0")
        }


__all__ = ["Account"]
