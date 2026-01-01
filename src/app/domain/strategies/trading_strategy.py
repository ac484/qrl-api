"""
Trading strategy domain logic
Pure business logic without infrastructure dependencies

Mathematical Formulas:
    MA(n) = Σ(P_i) / n
        where P_i = price at period i, n = number of periods
    
    Signal_Strength = [(MA_short - MA_long) / MA_long] × 100%
    
    BUY_Condition = (MA_short > MA_long) AND (Price ≤ Avg_Cost × 1.00)
    SELL_Condition = (MA_short < MA_long) AND (Price ≥ Avg_Cost × 1.03)

Reference: docs/STRATEGY_DESIGN_FORMULAS.md
"""
from src.app.infrastructure.config import config


class TradingStrategy:
    """
    Moving Average Crossover Strategy with Cost-Based Filtering
    
    Strategy Overview:
    ==================
    Uses moving average crossover signals combined with cost-based filtering
    to generate buy/sell decisions. Implements the QRL accumulation strategy
    that prioritizes holding QRL long-term while trading around the position.
    
    Core Components:
    ---------------
    1. MA Calculation: Simple Moving Average (SMA) for trend detection
    2. Signal Generation: Crossover-based entry/exit signals
    3. Cost Filter: Ensures trades align with accumulation goals
    
    Mathematical Foundation:
    -----------------------
    - MA(n) = Σ(P_i) / n
    - Golden Cross (BUY): MA_short > MA_long AND Price ≤ Cost
    - Death Cross (SELL): MA_short < MA_long AND Price ≥ Cost × 1.03
    
    Configuration:
    -------------
    - MA_short: Default 7 periods (configurable)
    - MA_long: Default 25 periods (configurable)
    - Buy threshold: 100% of average cost (no premium)
    - Sell threshold: 103% of average cost (minimum 3% profit)
    
    For detailed formulas and examples, see:
    - docs/STRATEGY_DESIGN_FORMULAS.md
    - docs/STRATEGY_CALCULATION_EXAMPLES.md
    """

    def __init__(self, ma_short_period: int = None, ma_long_period: int = None):
        """
        Initialize trading strategy with MA periods
        
        Formula Reference:
        -----------------
        This class implements the MA crossover strategy where:
        - Short MA (MA_s) uses fewer periods for faster response
        - Long MA (MA_l) uses more periods for trend confirmation
        - Crossover occurs when MA_s crosses above/below MA_l

        Args:
            ma_short_period: Short-term MA period (default: 7 from config)
                           Faster response to price changes
            ma_long_period: Long-term MA period (default: 25 from config)
                          Slower, smoother trend indicator
        
        Example:
            >>> strategy = TradingStrategy(ma_short_period=7, ma_long_period=25)
            >>> # Uses 7-period and 25-period moving averages
        """
        self.ma_short_period = ma_short_period or config.config.MA_SHORT_PERIOD
        self.ma_long_period = ma_long_period or config.config.MA_LONG_PERIOD

    def calculate_moving_average(self, prices: list) -> float:
        """
        Calculate Simple Moving Average (SMA)
        
        Formula:
        -------
        MA(n) = Σ(P_i) / n
        
        Where:
        - P_i = price at period i
        - n = number of periods
        - Σ = sum from i=1 to n
        
        Example:
        -------
        prices = [0.0480, 0.0485, 0.0490, 0.0495, 0.0500, 0.0505, 0.0510]
        MA(7) = (0.0480 + 0.0485 + ... + 0.0510) / 7
              = 0.3465 / 7
              = 0.04950
        
        Args:
            prices: List of price values (most recent should be last)
        
        Returns:
            Moving average value, or 0.0 if no prices provided
        
        Note:
            - Requires at least 1 price
            - Uses all provided prices (caller should slice to period)
            - Returns 0.0 for empty list (safe default for validation)
        """
        if not prices:
            return 0.0
        # Formula: MA(n) = Σ(P_i) / n
        return sum(prices) / len(prices)

    def generate_signal(
        self, price: float, short_prices: list, long_prices: list, avg_cost: float
    ) -> str:
        """
        Generate trading signal based on MA crossover and cost-based filtering
        
        Signal Generation Formula:
        ========================
        
        BUY Signal:
        ----------
        BUY = (MA_Crossover_Condition) AND (Price_Condition)
        
        Where:
            MA_Crossover_Condition: MA_short > MA_long
            Price_Condition: Current_Price ≤ Average_Cost × 1.00
        
        Rationale: Only buy when:
        1. Short-term trend is bullish (golden cross)
        2. Price is at or below our average cost (accumulation opportunity)
        
        SELL Signal:
        -----------
        SELL = (MA_Crossover_Condition) AND (Profit_Condition)
        
        Where:
            MA_Crossover_Condition: MA_short < MA_long
            Profit_Condition: Current_Price ≥ Average_Cost × 1.03
        
        Rationale: Only sell when:
        1. Short-term trend is bearish (death cross)
        2. Price is at least 3% above our average cost (minimum profit)
        
        HOLD Signal:
        -----------
        Default signal when neither BUY nor SELL conditions are met
        
        Example Calculation:
        -------------------
        Given:
            MA_short = 0.0505
            MA_long = 0.0495
            Current_Price = 0.0490
            Average_Cost = 0.0500
        
        BUY Check:
            MA_Crossover: 0.0505 > 0.0495 = TRUE ✓
            Price_Threshold: 0.0500 × 1.00 = 0.0500
            Price_Condition: 0.0490 ≤ 0.0500 = TRUE ✓
            Result: BUY ✓
        
        SELL Check (different scenario):
            MA_short = 0.0495, MA_long = 0.0505
            Current_Price = 0.0520, Average_Cost = 0.0500
            
            MA_Crossover: 0.0495 < 0.0505 = TRUE ✓
            Profit_Threshold: 0.0500 × 1.03 = 0.0515
            Profit_Condition: 0.0520 ≥ 0.0515 = TRUE ✓
            Result: SELL ✓

        Args:
            price: Current market price (USDT/QRL)
            short_prices: Recent prices for short MA (must have ≥ ma_short_period items)
            long_prices: Recent prices for long MA (must have ≥ ma_long_period items)
            avg_cost: Average cost basis from previous purchases (USDT/QRL)

        Returns:
            Signal string: "BUY", "SELL", or "HOLD"
            
        Note:
            - Returns "HOLD" if any input validation fails (MA=0, cost=0)
            - MA calculations use the most recent prices in the provided lists
            - Risk management checks happen separately before trade execution
            
        See Also:
            - docs/STRATEGY_DESIGN_FORMULAS.md (Section 3: Signal Generation)
            - docs/STRATEGY_CALCULATION_EXAMPLES.md (Example 4 & 5)
        """
        # Step 1: Calculate moving averages
        # Formula: MA(n) = Σ(P_i) / n
        ma_short = self.calculate_moving_average(short_prices)
        ma_long = self.calculate_moving_average(long_prices)

        # Step 2: Validate inputs (safety check)
        # If any critical value is 0, cannot make decision
        if ma_short == 0 or ma_long == 0 or avg_cost == 0:
            return "HOLD"

        # Step 3: Check BUY conditions
        # Formula: BUY = (MA_short > MA_long) AND (Price ≤ Cost × 1.00)
        if ma_short > ma_long and price <= avg_cost * 1.0:
            # Golden cross + price at or below cost
            # = Good accumulation opportunity
            return "BUY"

        # Step 4: Check SELL conditions
        # Formula: SELL = (MA_short < MA_long) AND (Price ≥ Cost × 1.03)
        elif ma_short < ma_long and price >= avg_cost * 1.03:
            # Death cross + price with minimum 3% profit
            # = Take profit opportunity
            return "SELL"

        # Step 5: Default to HOLD
        # Neither condition met = wait for better opportunity
        else:
            return "HOLD"

    def calculate_signal_strength(self, ma_short: float, ma_long: float) -> float:
        """
        Calculate the strength of the MA crossover signal
        
        Formula:
        -------
        Signal_Strength = [(MA_short - MA_long) / MA_long] × 100%
        
        Interpretation:
        --------------
        - Positive value: Bullish (MA_short > MA_long)
        - Negative value: Bearish (MA_short < MA_long)
        - Magnitude: Strength of the signal
        
        Examples:
        --------
        Example 1 - Moderate Bullish:
            MA_short = 0.0505
            MA_long = 0.0495
            Strength = (0.0505 - 0.0495) / 0.0495 × 100%
                    = 0.0010 / 0.0495 × 100%
                    = 2.02%
            Interpretation: Moderate upward trend
        
        Example 2 - Strong Bearish:
            MA_short = 0.0480
            MA_long = 0.0500
            Strength = (0.0480 - 0.0500) / 0.0500 × 100%
                    = -0.0020 / 0.0500 × 100%
                    = -4.00%
            Interpretation: Strong downward trend
        
        Example 3 - Neutral:
            MA_short = 0.0500
            MA_long = 0.0500
            Strength = (0.0500 - 0.0500) / 0.0500 × 100%
                    = 0.00%
            Interpretation: No clear trend

        Args:
            ma_short: Short-term moving average value
            ma_long: Long-term moving average value

        Returns:
            Percentage difference between MAs
            - Positive: Short MA is above Long MA (bullish)
            - Negative: Short MA is below Long MA (bearish)
            - Zero: MAs are equal or long MA is zero
            
        Note:
            - Returns 0.0 if ma_long is zero (avoid division by zero)
            - Can be used to filter weak signals (e.g., only trade if |strength| > 1%)
            - Higher absolute values indicate stronger trends
            
        See Also:
            docs/STRATEGY_DESIGN_FORMULAS.md (Section 2.2: Signal Strength)
        """
        if ma_long == 0:
            return 0.0
        # Formula: Signal_Strength = [(MA_short - MA_long) / MA_long] × 100
        return ((ma_short / ma_long) - 1) * 100
