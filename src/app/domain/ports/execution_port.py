"""
ExecutionPort - Order execution abstraction from ✨.md Section 6.5

Enables backtest/paper/live with same code:
- SimExecution: Simulated for backtesting
- PaperExecution: Paper trading
- MexcExecution: Real exchange execution

Bot/Strategy layer doesn't need to change.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class ExecutionPort(ABC):
    """
    Abstract order execution interface.
    
    From ✨.md: "Bot/Strategy/Position completely unchanged"
    """

    @abstractmethod
    async def place(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order.
        
        Args:
            order: Order parameters (symbol, side, quantity, etc.)
            
        Returns:
            Order result/confirmation
        """
        pass

    @abstractmethod
    async def cancel(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel an order.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Cancellation confirmation
        """
        pass


__all__ = ["ExecutionPort"]
