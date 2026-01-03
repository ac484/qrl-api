"""
Percentage Value Object

Represents a percentage value (0-1 range) used throughout the domain for ratios,
thresholds, and proportional calculations.
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Percentage:
    """
    Percentage value object (0-1 range)
    
    Examples:
        - 0.1 = 10%
        - 0.5 = 50%
        - 1.0 = 100%
    
    Characteristics:
        - Immutable (frozen=True)
        - Validated (0 ≤ value ≤ 1)
        - Value equality
        - No identity
    """
    
    value: Decimal
    
    def __post_init__(self) -> None:
        """Validate percentage is in valid range."""
        if not isinstance(self.value, Decimal):
            raise TypeError(f"Percentage value must be Decimal, got {type(self.value).__name__}")
        
        if self.value < 0 or self.value > 1:
            raise ValueError(f"Percentage must be between 0 and 1, got {self.value}")
    
    @classmethod
    def from_float(cls, value: float) -> "Percentage":
        """
        Create Percentage from float
        
        Args:
            value: Float between 0.0 and 1.0
        
        Returns:
            Percentage instance
        
        Example:
            >>> pct = Percentage.from_float(0.7)  # 70%
            >>> pct.value
            Decimal('0.7')
        """
        return cls(value=Decimal(str(value)))
    
    @classmethod
    def from_percent(cls, percent: float) -> "Percentage":
        """
        Create Percentage from percentage value (0-100)
        
        Args:
            percent: Percentage value (0-100)
        
        Returns:
            Percentage instance
        
        Example:
            >>> pct = Percentage.from_percent(70)  # 70%
            >>> pct.value
            Decimal('0.7')
        """
        if percent < 0 or percent > 100:
            raise ValueError(f"Percent must be between 0 and 100, got {percent}")
        return cls(value=Decimal(str(percent / 100)))
    
    @classmethod
    def zero(cls) -> "Percentage":
        """Create 0% percentage."""
        return cls(value=Decimal("0"))
    
    @classmethod
    def full(cls) -> "Percentage":
        """Create 100% percentage."""
        return cls(value=Decimal("1"))
    
    def to_percent(self) -> Decimal:
        """
        Convert to percentage value (0-100)
        
        Returns:
            Decimal percentage value
        
        Example:
            >>> pct = Percentage.from_float(0.7)
            >>> pct.to_percent()
            Decimal('70')
        """
        return self.value * Decimal("100")
    
    def apply_to(self, amount: Decimal) -> Decimal:
        """
        Apply percentage to an amount
        
        Args:
            amount: Amount to calculate percentage of
        
        Returns:
            Result of amount * percentage
        
        Example:
            >>> pct = Percentage.from_float(0.7)
            >>> pct.apply_to(Decimal("1000"))
            Decimal('700')
        """
        return amount * self.value
    
    def complement(self) -> "Percentage":
        """
        Get complement percentage (1 - value)
        
        Returns:
            New Percentage instance
        
        Example:
            >>> pct = Percentage.from_float(0.3)  # 30%
            >>> pct.complement().value
            Decimal('0.7')  # 70%
        """
        return Percentage(value=Decimal("1") - self.value)
    
    def __str__(self) -> str:
        """String representation as percentage."""
        return f"{self.to_percent()}%"
    
    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"Percentage({self.value})"


__all__ = ["Percentage"]
