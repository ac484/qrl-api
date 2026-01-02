"""Trading Strategy - Policy definition (Domain layer)"""
from src.app.infrastructure.config import config
from src.app.domain.strategies.indicators import MASignalGenerator
from src.app.domain.strategies.filters import CostFilter


class TradingStrategy:
    """
    MA Crossover Strategy with Cost-Based Filtering
    
    Strategy: Combines MA crossover signals with cost-based filtering
    to generate buy/sell decisions for QRL accumulation.
    
    Components:
    - MASignalGenerator: Calculates MA and detects crossovers
    - CostFilter: Enforces cost-based trade rules
    
    Rules:
    - BUY: Golden cross + price ≤ avg_cost
    - SELL: Death cross + price ≥ avg_cost × 1.03
    - HOLD: Otherwise
    """

    def __init__(
        self,
        ma_short_period: int = None,
        ma_long_period: int = None,
        ma_generator: MASignalGenerator = None,
        cost_filter: CostFilter = None,
    ):
        self.ma_short_period = ma_short_period or config.config.MA_SHORT_PERIOD
        self.ma_long_period = ma_long_period or config.config.MA_LONG_PERIOD
        
        self.ma_generator = ma_generator or MASignalGenerator(
            self.ma_short_period, self.ma_long_period
        )
        self.cost_filter = cost_filter or CostFilter(
            buy_threshold=1.00, sell_threshold=1.03
        )

    def calculate_moving_average(self, prices: list) -> float:
        """Calculate MA (delegates to MASignalGenerator)"""
        return self.ma_generator.calculate_ma(prices)

    def generate_signal(
        self, price: float, short_prices: list, long_prices: list, avg_cost: float
    ) -> str:
        """
        Generate trading signal
        
        Process:
        1. Detect MA crossover (delegate to MASignalGenerator)
        2. Apply cost filter (delegate to CostFilter)
        
        Args:
            price: Current market price
            short_prices: Recent prices for short MA
            long_prices: Recent prices for long MA
            avg_cost: Average cost basis
        
        Returns:
            "BUY", "SELL", or "HOLD"
        """
        # Step 1: Get MA crossover signal (delegate)
        ma_signal = self.ma_generator.detect_crossover(short_prices, long_prices)
        
        # Step 2: Apply cost-based filter (delegate)
        return self.cost_filter.filter_signal(ma_signal, price, avg_cost)

    def calculate_signal_strength(self, ma_short: float, ma_long: float) -> float:
        """
        Calculate signal strength (delegates to MASignalGenerator)
        
        Formula: [(MA_short - MA_long) / MA_long] × 100%
        """
        if ma_long == 0:
            return 0.0
        return ((ma_short / ma_long) - 1) * 100

    def get_signal_details(
        self, price: float, short_prices: list, long_prices: list, avg_cost: float
    ) -> dict:
        """
        Get comprehensive signal analysis
        
        Returns signal with MA values, crossover type, and strength
        """
        ma_values = self.ma_generator.get_ma_values(short_prices, long_prices)
        signal = self.generate_signal(price, short_prices, long_prices, avg_cost)
        
        return {
            "signal": signal,
            "ma_short": ma_values["ma_short"],
            "ma_long": ma_values["ma_long"],
            "crossover": ma_values["signal"],
            "strength": ma_values["strength"],
            "price": price,
            "avg_cost": avg_cost,
        }
