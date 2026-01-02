"""
Timeframe Aggregator - Multi-timeframe support from ✨.md

Implements single WS → multiple timeframes pattern:
- Single WS connection provides 1m candles
- Aggregates into 5m, 15m, 1h etc.
- Synchronizes strategy triggers across timeframes
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class MarketCandle:
    """
    Market candle data (DTO from ✨.md).
    
    Immutable data structure for market data.
    """
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    closed_at: datetime


class TimeframeAggregator:
    """
    Aggregates 1-minute candles into multiple timeframes.
    
    From ✨.md Section 6.4:
    ❌ Wrong: Open separate WS for each timeframe
    ✅ Right: Single WS → time aggregation
    
    Usage:
        aggregator = TimeframeAggregator([1, 5, 15])
        
        for candle_1m in ws_stream:
            completed = aggregator.on_candle(candle_1m)
            for timeframe, merged_candle in completed:
                await bot.on_market_tick(timeframe, merged_candle)
    """

    def __init__(self, timeframes: List[int]):
        """
        Initialize aggregator.
        
        Args:
            timeframes: List of timeframes in minutes (e.g., [1, 5, 15, 60])
        """
        self.timeframes = sorted(timeframes)
        self.buffers: Dict[int, List[MarketCandle]] = {
            tf: [] for tf in timeframes
        }

    def on_candle(self, candle: MarketCandle) -> List[Tuple[int, MarketCandle]]:
        """
        Process incoming 1-minute candle.
        
        Returns list of completed (timeframe, candle) pairs.
        Different timeframes complete at different times.
        
        Args:
            candle: 1-minute candle from WS
            
        Returns:
            List of (timeframe, merged_candle) for completed timeframes
        """
        completed = []
        
        for tf in self.timeframes:
            buf = self.buffers[tf]
            buf.append(candle)
            
            if self._is_timeframe_closed(buf, tf):
                merged = self._merge_candles(buf, tf)
                completed.append((tf, merged))
                buf.clear()
        
        return completed

    def _is_timeframe_closed(self, buffer: List[MarketCandle], timeframe: int) -> bool:
        """
        Check if timeframe period is complete.
        
        Args:
            buffer: Accumulated candles
            timeframe: Target timeframe in minutes
            
        Returns:
            True if timeframe period is complete
        """
        if not buffer:
            return False
        
        if len(buffer) < timeframe:
            return False
        
        start = buffer[0].closed_at
        end = buffer[-1].closed_at
        expected_duration = timedelta(minutes=timeframe)
        
        return (end - start) >= expected_duration

    def _merge_candles(self, buffer: List[MarketCandle], timeframe: int) -> MarketCandle:
        """
        Merge 1-minute candles into larger timeframe.
        
        Args:
            buffer: Accumulated 1-minute candles
            timeframe: Target timeframe in minutes
            
        Returns:
            Merged candle for the timeframe
        """
        if not buffer:
            raise ValueError("Cannot merge empty buffer")
        
        return MarketCandle(
            symbol=buffer[0].symbol,
            open=buffer[0].open,
            high=max(c.high for c in buffer),
            low=min(c.low for c in buffer),
            close=buffer[-1].close,
            volume=sum(c.volume for c in buffer),
            closed_at=buffer[-1].closed_at,
        )


__all__ = ["MarketCandle", "TimeframeAggregator"]
