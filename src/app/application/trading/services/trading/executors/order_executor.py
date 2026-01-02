"""
Order Executor - Pure MEXC order execution logic

Responsibility: Execute orders on MEXC exchange ONLY
Layer: Infrastructure (execution)
"""
import logging
from typing import Dict

logger = logging.getLogger(__name__)


class OrderExecutor:
    """
    Execute market orders on MEXC exchange

    Single Responsibility: Place orders via MEXC API
    No business logic, no state management, pure execution
    """

    def __init__(self, mexc_client):
        """
        Initialize order executor

        Args:
            mexc_client: MEXC API client for order placement
        """
        self.mexc = mexc_client

    async def execute_market_order(
        self, action: str, quantity: float, symbol: str = "QRLUSDT"
    ) -> Dict:
        """
        Execute market order on MEXC

        Args:
            action: "BUY" or "SELL"
            quantity: Order quantity
            symbol: Trading pair symbol

        Returns:
            Dict with order execution result

        Raises:
            ValueError: If action or quantity invalid
            Exception: If MEXC API call fails
        """
        # Validate parameters
        self._validate_order_params(action, quantity)

        logger.info(f"Executing {action} order: {quantity} {symbol}")

        # Execute order via MEXC
        async with self.mexc:
            if action == "BUY":
                return await self._execute_buy(symbol, quantity)
            else:  # SELL
                return await self._execute_sell(symbol, quantity)

    async def _execute_buy(self, symbol: str, quantity: float) -> Dict:
        """
        Execute BUY market order

        Args:
            symbol: Trading pair
            quantity: Buy quantity

        Returns:
            MEXC order response
        """
        return await self.mexc.place_market_order(
            symbol=symbol, side="BUY", quantity=quantity
        )

    async def _execute_sell(self, symbol: str, quantity: float) -> Dict:
        """
        Execute SELL market order

        Args:
            symbol: Trading pair
            quantity: Sell quantity

        Returns:
            MEXC order response
        """
        return await self.mexc.place_market_order(
            symbol=symbol, side="SELL", quantity=quantity
        )

    def _validate_order_params(self, action: str, quantity: float) -> None:
        """
        Validate order parameters

        Args:
            action: Order side
            quantity: Order quantity

        Raises:
            ValueError: If parameters invalid
        """
        if action not in ["BUY", "SELL"]:
            raise ValueError(f"Invalid action: {action}. Must be BUY or SELL")

        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}. Must be > 0")
