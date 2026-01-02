"""Market price snapshot model (Read Model / Data Transfer Object).

This is NOT a Value Object or Entity:
- Not a VO: Has timestamp (point-in-time state), not purely conceptual
- Not an Entity: No identity field, no lifecycle management
- Is a Read Model: Represents market data snapshot from exchange

Use this for:
- Market data display/reporting
- Price history tracking
- Exchange API responses

For domain logic, use value_objects.Price (monetary value with currency).
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(slots=True)
class MarketPrice:
    """Market price snapshot from exchange (Read Model).
    
    Represents point-in-time market data, not domain value object.
    
    Attributes:
        symbol: Trading pair (e.g., "QRLUSDT")
        value: Current price
        change_percent: 24h price change percentage
        volume_24h: 24h trading volume
        high_24h: 24h high price
        low_24h: 24h low price
        timestamp: Snapshot timestamp
    """
    symbol: str
    value: float
    change_percent: Optional[float] = None
    volume_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    timestamp: datetime = datetime.utcnow()


__all__ = ["MarketPrice"]
