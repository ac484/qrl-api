"""Cost Filter - Business rule enforcement (Domain layer)"""


class CostFilter:
    """
    Cost-based trade filtering
    
    BUY Rule: Price ≤ Cost × buy_threshold (default 1.00)
    SELL Rule: Price ≥ Cost × sell_threshold (default 1.03, min 3% profit)
    """

    def __init__(self, buy_threshold: float = 1.00, sell_threshold: float = 1.03):
        self.buy_threshold = buy_threshold
        self.sell_threshold = sell_threshold

    def should_buy(self, current_price: float, avg_cost: float) -> bool:
        """
        Check if price is favorable for buying
        
        Returns True if price ≤ avg_cost × buy_threshold
        Default: Buy when price at or below cost (accumulation)
        """
        if avg_cost == 0:
            return False
        return current_price <= avg_cost * self.buy_threshold

    def should_sell(self, current_price: float, avg_cost: float) -> bool:
        """
        Check if price is favorable for selling
        
        Returns True if price ≥ avg_cost × sell_threshold
        Default: Sell when price ≥ 103% of cost (min 3% profit)
        """
        if avg_cost == 0:
            return False
        return current_price >= avg_cost * self.sell_threshold

    def filter_signal(self, ma_signal: str, current_price: float, avg_cost: float) -> str:
        """
        Apply cost filter to MA crossover signal
        
        Args:
            ma_signal: "GOLDEN_CROSS", "DEATH_CROSS", or "NEUTRAL"
            current_price: Current market price
            avg_cost: Average cost basis
        
        Returns:
            "BUY" if golden cross + favorable buy price
            "SELL" if death cross + favorable sell price
            "HOLD" otherwise
        """
        if ma_signal == "GOLDEN_CROSS" and self.should_buy(current_price, avg_cost):
            return "BUY"
        elif ma_signal == "DEATH_CROSS" and self.should_sell(current_price, avg_cost):
            return "SELL"
        else:
            return "HOLD"
