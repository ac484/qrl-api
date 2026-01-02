"""
Moving Average calculator for technical analysis.

Calculates simple moving averages from price data and detects crossover signals.
"""

from typing import Any, Dict, List

from src.app.infrastructure.utils import safe_float


class MACalculator:
    """
    Calculate moving averages and detect trading signals.

    Supports short-term and long-term MA calculations with signal detection
    for golden cross (bullish) and death cross (bearish) patterns.
    """

    def __init__(self, short_period: int = 7, long_period: int = 25) -> None:
        """
        Initialize MA calculator with periods.

        Args:
            short_period: Number of periods for short MA (default: 7)
            long_period: Number of periods for long MA (default: 25)
        """
        self.short_period = short_period
        self.long_period = long_period

    async def calculate_from_klines(
        self, klines: List[List], mexc_client=None, symbol: str = ""
    ) -> Dict[str, Any]:
        """
        Calculate MA indicators from kline data.

        Args:
            klines: List of kline data from MEXC API
            mexc_client: MEXC client (unused, for compatibility)
            symbol: Trading symbol (unused, for compatibility)

        Returns:
            Dict containing:
            - ma_short: Short-term moving average
            - ma_long: Long-term moving average
            - signal: Trading signal (GOLDEN_CROSS, DEATH_CROSS, NEUTRAL)
            - signal_strength: Percentage difference between MAs
            - prices_count: Number of prices used
            - error: Error message if calculation fails (optional)
        """
        try:
            if not klines or len(klines) < self.long_period:
                return {
                    "ma_short": 0.0,
                    "ma_long": 0.0,
                    "signal": "UNKNOWN",
                    "signal_strength": 0.0,
                    "error": "Insufficient price data",
                }

            # Extract closing prices (index 4 in kline data)
            # Kline format: [timestamp, open, high, low, close, volume, ...]
            prices = [safe_float(k[4]) for k in klines]

            # Calculate MA_short (most recent N candles)
            recent_prices_short = prices[-self.short_period :]
            ma_short = sum(recent_prices_short) / len(recent_prices_short)

            # Calculate MA_long (most recent N candles)
            recent_prices_long = prices[-self.long_period :]
            ma_long = sum(recent_prices_long) / len(recent_prices_long)

            # Calculate signal strength (percentage difference)
            signal_strength = (
                (ma_short - ma_long) / ma_long * 100 if ma_long > 0 else 0.0
            )

            # Determine signal direction
            if ma_short > ma_long:
                signal = "GOLDEN_CROSS"  # Bullish
            elif ma_short < ma_long:
                signal = "DEATH_CROSS"  # Bearish
            else:
                signal = "NEUTRAL"

            return {
                "ma_short": ma_short,
                "ma_long": ma_long,
                "signal": signal,
                "signal_strength": signal_strength,
                "prices_count": len(prices),
            }

        except Exception as e:
            return {
                "ma_short": 0.0,
                "ma_long": 0.0,
                "signal": "ERROR",
                "signal_strength": 0.0,
                "error": str(e),
            }


__all__ = ["MACalculator"]
