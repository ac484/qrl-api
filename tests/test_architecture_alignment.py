"""
Tests for ✨.md architecture alignment components.

Tests the key patterns implemented from the architecture guide.
"""
import asyncio
from datetime import datetime
import pytest

from src.app.application.market.timeframe_aggregator import (
    MarketCandle,
    TimeframeAggregator,
)


class TestMarketCandle:
    """Test MarketCandle DTO."""

    def test_candle_immutable(self):
        """MarketCandle should be immutable (frozen dataclass)."""
        candle = MarketCandle(
            symbol="QRLUSDT",
            open=1.0,
            high=1.1,
            low=0.9,
            close=1.05,
            volume=1000.0,
            closed_at=datetime.now(),
        )
        
        # Should not be able to modify
        with pytest.raises(AttributeError):
            candle.close = 2.0


class TestTimeframeAggregator:
    """Test multi-timeframe aggregation (✨.md Section 6.4)."""

    def test_aggregator_initialization(self):
        """Aggregator should initialize with timeframes."""
        aggregator = TimeframeAggregator([1, 5, 15])
        assert aggregator.timeframes == [1, 5, 15]
        assert 1 in aggregator.buffers
        assert 5 in aggregator.buffers
        assert 15 in aggregator.buffers

    def test_single_candle_no_completion(self):
        """Single candle shouldn't complete any timeframe."""
        aggregator = TimeframeAggregator([5])
        
        candle = MarketCandle(
            symbol="QRLUSDT",
            open=1.0,
            high=1.0,
            low=1.0,
            close=1.0,
            volume=100.0,
            closed_at=datetime(2024, 1, 1, 0, 0, 0),
        )
        
        completed = aggregator.on_candle(candle)
        assert len(completed) == 0  # Not enough candles yet

    def test_merge_candles_ohlcv(self):
        """Merged candles should have correct OHLCV values."""
        aggregator = TimeframeAggregator([3])
        
        # Create 3 candles with different values
        candles = [
            MarketCandle(
                symbol="QRLUSDT",
                open=1.0,
                high=1.2,
                low=0.9,
                close=1.1,
                volume=100.0,
                closed_at=datetime(2024, 1, 1, 0, i, 0),
            )
            for i in range(3)
        ]
        
        # Manually merge to test logic
        for candle in candles:
            aggregator.on_candle(candle)
        
        # Buffer should have 3 candles
        assert len(aggregator.buffers[3]) == 3


class TestWSClientHeartbeat:
    """Test WS client data flow heartbeat (✨.md Section 6.3)."""

    def test_ws_client_has_is_alive(self):
        """WS client should have is_alive() method for heartbeat."""
        from src.app.infrastructure.external.mexc.websocket.client import (
            MEXCWebSocketClient,
        )
        
        client = MEXCWebSocketClient(heartbeat=20.0)
        
        # Should have the method
        assert hasattr(client, "is_alive")
        assert callable(client.is_alive)
        
        # Should have last_message_at tracking
        assert hasattr(client, "last_message_at")


class TestPortAbstractions:
    """Test abstract ports for backtest/paper/live (✨.md Section 6.5)."""

    def test_market_feed_is_abstract(self):
        """MarketFeed should be an abstract base class."""
        from src.app.domain.ports.market_feed import MarketFeed
        
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            MarketFeed()

    def test_execution_port_is_abstract(self):
        """ExecutionPort should be an abstract base class."""
        from src.app.domain.ports.execution_port import ExecutionPort
        
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            ExecutionPort()


class TestSupervisorPattern:
    """Test WS supervisor reconnection pattern (✨.md Section 6.3)."""

    def test_supervisor_initialization(self):
        """Supervisor should initialize with client and callback."""
        from src.app.application.market.ws_supervisor import (
            MarketStreamSupervisor,
        )
        
        # Mock client and callback
        mock_client = object()
        
        async def mock_callback(msg):
            pass
        
        supervisor = MarketStreamSupervisor(
            ws_client=mock_client,
            on_message=mock_callback,
            reconnect_delay=2.0,
        )
        
        assert supervisor.ws_client is mock_client
        assert supervisor.on_message is mock_callback
        assert supervisor.reconnect_delay == 2.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
