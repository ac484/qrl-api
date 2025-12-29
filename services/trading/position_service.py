"""
PositionService
---------------
Placeholder service for position and quantity calculations.
"""
from typing import Any, Dict


class PositionService:
    """Stub for position sizing helpers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

    def calculate_buy_quantity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Return zero quantities until implemented."""
        return {"quantity": 0, "usdt_amount": 0}

    def calculate_sell_quantity(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Return zero quantities until implemented."""
        return {"quantity": 0}
