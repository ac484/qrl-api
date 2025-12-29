"""
Trading strategy domain logic
Pure business logic without infrastructure dependencies
"""
from typing import Dict, Any
from infrastructure.config.config import config


class TradingStrategy:
    """
    Moving Average Crossover Strategy with Cost-Based Filtering
    """
    
    def __init__(self, ma_short_period: int = None, ma_long_period: int = None):
        """
        Initialize trading strategy
        
        Args:
            ma_short_period: Short-term MA period (default from config)
            ma_long_period: Long-term MA period (default from config)
        """
        self.ma_short_period = ma_short_period or config.config.MA_SHORT_PERIOD
        self.ma_long_period = ma_long_period or config.config.MA_LONG_PERIOD
    
    def calculate_moving_average(self, prices: list) -> float:
        """Calculate simple moving average"""
        if not prices:
            return 0.0
        return sum(prices) / len(prices)
    
    def generate_signal(
        self,
        price: float,
        short_prices: list,
        long_prices: list,
        avg_cost: float
    ) -> str:
        """
        Generate trading signal based on MA crossover and cost
        
        Args:
            price: Current market price
            short_prices: Prices for short MA calculation
            long_prices: Prices for long MA calculation
            avg_cost: Average cost basis
            
        Returns:
            Signal: "BUY", "SELL", or "HOLD"
        """
        # Calculate moving averages
        ma_short = self.calculate_moving_average(short_prices)
        ma_long = self.calculate_moving_average(long_prices)
        
        # Validate inputs
        if ma_short == 0 or ma_long == 0 or avg_cost == 0:
            return "HOLD"
        
        # BUY signal: MA short crosses above MA long AND price below avg cost
        if ma_short > ma_long and price < avg_cost * 1.0:  # Only buy below or at cost
            return "BUY"
        
        # SELL signal: MA short crosses below MA long AND price above avg cost
        elif ma_short < ma_long and price > avg_cost * 1.03:  # Sell at 3%+ profit
            return "SELL"
        
        else:
            return "HOLD"
    
    def calculate_signal_strength(self, ma_short: float, ma_long: float) -> float:
        """
        Calculate strength of signal based on MA spread
        
        Returns:
            Percentage spread between short and long MA
        """
        if ma_long == 0:
            return 0.0
        return ((ma_short / ma_long) - 1) * 100
