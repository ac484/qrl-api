"""
MarketFeed Port - Abstraction from ✨.md Section 6.5

Enables backtest/paper/live with same code:
- LiveWSFeed: Real-time WebSocket data
- ReplayFeed: Historical data for backtesting
- PaperFeed: Simulated live data

Strategy/Bot/Position layer doesn't need to change.
"""
from abc import ABC, abstractmethod
from typing import AsyncIterator

from src.app.application.market.timeframe_aggregator import MarketCandle


class MarketFeed(ABC):
    """
    Abstract market data feed.
    
    From ✨.md: "Same code supports backtest/paper/live"
    """

    @abstractmethod
    async def stream(self) -> AsyncIterator[MarketCandle]:
        """
        Stream market candles.
        
        Yields:
            MarketCandle instances
        """
        pass


__all__ = ["MarketFeed"]
