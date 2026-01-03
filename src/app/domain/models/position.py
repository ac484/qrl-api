"""Position entity for tracking holdings and costs.

DDD Entity Pattern:
- Entity: Has identity (symbol), can change state through methods
- Encapsulates position management logic
- Uses Value Objects for domain concepts
- State changes only through behavior methods

Position is an Entity (not VO) because:
- Has identity (symbol uniquely identifies position)
- Changes state over time (quantities, costs, PNL)
- Represents a tracked holding, not just a concept

Example:
    >>> from src.app.domain.value_objects import Symbol, Quantity, Price
    >>> position = Position(
    ...     symbol=Symbol("QRLUSDT"),
    ...     total_quantity=Quantity.from_float(100.0),
    ...     average_cost=Price.from_float(100.0, "USDT"),
    ... )
    >>> position.apply_buy(Quantity.from_float(50.0), Price.from_float(110.0, "USDT"))
    >>> position.total_quantity.value
    Decimal('150.0')
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from src.app.domain.value_objects import Percentage, Price, Quantity, Symbol


@dataclass(slots=True)
class Position:
    """Position entity representing holdings and cost basis.
    
    Entity Characteristics:
    - Has identity (symbol - one position per trading pair)
    - Mutable state (quantities, costs, PNL change over time)
    - State changes through methods (apply_buy, apply_sell)
    - Uses value objects for domain concepts
    
    The Position entity manages holdings for a specific trading pair,
    tracking quantity, average cost, and realized/unrealized PNL.
    
    Attributes:
        symbol: Trading pair (entity identity, immutable)
        total_quantity: Total amount held
        core_quantity: Core/reserved amount (subset of total)
        average_cost: Average acquisition cost per unit
        realized_pnl: Realized profit/loss from sells
        unrealized_pnl: Unrealized profit/loss (current value vs cost)
        last_updated: Last position update timestamp
    
    Example:
        >>> position = Position(
        ...     symbol=Symbol("QRLUSDT"),
        ...     total_quantity=Quantity.from_float(100.0),
        ...     average_cost=Price.from_float(100.0, "USDT"),
        ... )
        >>> position.apply_buy(Quantity.from_float(50.0), Price.from_float(110.0, "USDT"))
        >>> position.total_quantity.value > Decimal('100.0')
        True
    """

    symbol: Symbol  # Entity identity (immutable)
    total_quantity: Quantity
    core_quantity: Quantity = field(default_factory=lambda: Quantity(Decimal("0")))
    average_cost: Optional[Price] = None
    realized_pnl: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")
    last_updated: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        """Validate entity invariants on creation."""
        if not self.symbol:
            raise ValueError("Position must have a symbol (entity identity)")
        
        # Core quantity cannot exceed total quantity
        if self.core_quantity.value > self.total_quantity.value:
            raise ValueError(
                f"Core quantity ({self.core_quantity.value}) cannot exceed "
                f"total quantity ({self.total_quantity.value})"
            )

    def apply_buy(
        self,
        quantity: Quantity,
        price: Price,
        old_avg_cost: Optional[Price] = None,
        old_total_invested: Optional[Decimal] = None,
    ) -> None:
        """Apply a buy transaction to this position.
        
        Updates total quantity and recalculates average cost.
        Uses weighted average for cost calculation.
        
        Args:
            quantity: Amount being bought
            price: Buy price per unit
            old_avg_cost: Previous average cost (for calculation)
            old_total_invested: Previous total invested (for calculation)
        
        Example:
            >>> position = Position(
            ...     symbol=Symbol("QRLUSDT"),
            ...     total_quantity=Quantity.from_float(100.0),
            ...     average_cost=Price.from_float(100.0, "USDT"),
            ... )
            >>> position.apply_buy(Quantity.from_float(50.0), Price.from_float(110.0, "USDT"))
        """
        # Calculate new average cost
        current_avg = old_avg_cost or self.average_cost or price
        current_invested = old_total_invested or (
            current_avg.value * self.total_quantity.value if self.average_cost else Decimal("0")
        )
        
        new_invested = current_invested + (price.value * quantity.value)
        new_quantity = self.total_quantity.value + quantity.value
        new_avg_cost = new_invested / new_quantity if new_quantity > 0 else Decimal("0")
        
        # Update position (controlled mutation in entity)
        object.__setattr__(self, "total_quantity", Quantity(new_quantity))
        object.__setattr__(self, "average_cost", Price(new_avg_cost, price.currency))
        object.__setattr__(self, "last_updated", datetime.utcnow())

    def apply_sell(
        self,
        quantity: Quantity,
        price: Price,
    ) -> None:
        """Apply a sell transaction to this position.
        
        Updates total quantity and realizes PNL from the sell.
        
        Args:
            quantity: Amount being sold
            price: Sell price per unit
        
        Raises:
            ValueError: If selling more than available quantity
        
        Example:
            >>> position = Position(
            ...     symbol=Symbol("QRLUSDT"),
            ...     total_quantity=Quantity.from_float(100.0),
            ...     average_cost=Price.from_float(100.0, "USDT"),
            ... )
            >>> position.apply_sell(Quantity.from_float(50.0), Price.from_float(110.0, "USDT"))
        """
        if quantity.value > self.total_quantity.value:
            raise ValueError(
                f"Cannot sell {quantity.value} - only {self.total_quantity.value} available"
            )
        
        # Calculate realized PNL from this sell
        if self.average_cost:
            sell_pnl = (price.value - self.average_cost.value) * quantity.value
            new_realized_pnl = self.realized_pnl + sell_pnl
        else:
            new_realized_pnl = self.realized_pnl
        
        # Update position (controlled mutation in entity)
        new_quantity = self.total_quantity.value - quantity.value
        object.__setattr__(self, "total_quantity", Quantity(new_quantity))
        object.__setattr__(self, "realized_pnl", new_realized_pnl)
        object.__setattr__(self, "last_updated", datetime.utcnow())
        
        # If position is now empty, clear average cost
        if new_quantity == Decimal("0"):
            object.__setattr__(self, "average_cost", None)

    def calculate_unrealized_pnl(self, current_price: Price) -> Decimal:
        """Calculate unrealized PNL based on current market price.
        
        Args:
            current_price: Current market price
        
        Returns:
            Unrealized profit/loss
        
        Example:
            >>> position = Position(
            ...     symbol=Symbol("QRLUSDT"),
            ...     total_quantity=Quantity.from_float(100.0),
            ...     average_cost=Price.from_float(100.0, "USDT"),
            ... )
            >>> current = Price.from_float(110.0, "USDT")
            >>> pnl = position.calculate_unrealized_pnl(current)
            >>> pnl > Decimal('0')
            True
        """
        if not self.average_cost:
            return Decimal("0")
        
        return (current_price.value - self.average_cost.value) * self.total_quantity.value

    def update_unrealized_pnl(self, current_price: Price) -> None:
        """Update unrealized PNL with current market price.
        
        Args:
            current_price: Current market price
        """
        new_pnl = self.calculate_unrealized_pnl(current_price)
        object.__setattr__(self, "unrealized_pnl", new_pnl)
        object.__setattr__(self, "last_updated", datetime.utcnow())

    @property
    def total_pnl(self) -> Decimal:
        """Total PNL (realized + unrealized)."""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def has_holdings(self) -> bool:
        """Check if position has any holdings."""
        return self.total_quantity.value > Decimal("0")
    
    def get_tradeable_quantity(self, core_position_pct: Percentage) -> Quantity:
        """Calculate tradeable quantity after protecting core position.
        
        Formula: tradeable = total - (total * core_pct)
        
        This implements the core position protection rule: a percentage of the
        position is reserved as "core" and cannot be sold. Only the remaining
        "tradeable" portion can be sold.
        
        Args:
            core_position_pct: Percentage to protect as core (0-1 range)
        
        Returns:
            Tradeable quantity (may be zero if all is protected)
        
        Example:
            >>> position = Position(
            ...     symbol=Symbol("QRLUSDT"),
            ...     total_quantity=Quantity.from_float(100.0),
            ...     average_cost=Price.from_float(100.0, "USDT"),
            ... )
            >>> core_pct = Percentage.from_float(0.7)  # 70% protected
            >>> tradeable = position.get_tradeable_quantity(core_pct)
            >>> tradeable.value
            Decimal('30.0')
        """
        core_amount = core_position_pct.apply_to(self.total_quantity.value)
        tradeable_value = self.total_quantity.value - core_amount
        
        # Ensure tradeable is never negative
        if tradeable_value < Decimal("0"):
            tradeable_value = Decimal("0")
        
        return Quantity(tradeable_value)


__all__ = ["Position"]
