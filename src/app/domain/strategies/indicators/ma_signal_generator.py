"""MA Signal Generator - Pure mathematical computation (Domain layer)"""


class MASignalGenerator:
    """
    Moving Average calculation and crossover detection
    
    Formula: MA(n) = Σ(P_i) / n
    - Golden Cross: MA_short > MA_long (bullish)
    - Death Cross: MA_short < MA_long (bearish)
    """

    def __init__(self, short_period: int = 7, long_period: int = 25):
        self.short_period = short_period
        self.long_period = long_period

    def calculate_ma(self, prices: list) -> float:
        """Calculate Simple Moving Average. Returns 0.0 if no prices."""
        return sum(prices) / len(prices) if prices else 0.0

    def detect_crossover(self, short_prices: list, long_prices: list) -> str:
        """
        Detect MA crossover signal
        
        Returns:
            "GOLDEN_CROSS" if MA_short > MA_long
            "DEATH_CROSS" if MA_short < MA_long
            "NEUTRAL" otherwise
        """
        ma_short = self.calculate_ma(short_prices)
        ma_long = self.calculate_ma(long_prices)

        if ma_short == 0 or ma_long == 0:
            return "NEUTRAL"

        if ma_short > ma_long:
            return "GOLDEN_CROSS"
        elif ma_short < ma_long:
            return "DEATH_CROSS"
        else:
            return "NEUTRAL"

    def calculate_signal_strength(self, short_prices: list, long_prices: list) -> float:
        """
        Calculate MA crossover strength
        
        Formula: [(MA_short - MA_long) / MA_long] × 100%
        - Positive: Bullish (short > long)
        - Negative: Bearish (short < long)
        """
        ma_short = self.calculate_ma(short_prices)
        ma_long = self.calculate_ma(long_prices)

        if ma_long == 0:
            return 0.0
        
        return ((ma_short / ma_long) - 1) * 100

    def get_ma_values(self, short_prices: list, long_prices: list) -> dict:
        """Get calculated MA values for both periods"""
        return {
            "ma_short": self.calculate_ma(short_prices),
            "ma_long": self.calculate_ma(long_prices),
            "signal": self.detect_crossover(short_prices, long_prices),
            "strength": self.calculate_signal_strength(short_prices, long_prices),
        }
