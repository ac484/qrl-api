"""
Position sizing and cost calculations using Value Objects.

Moved under src/app/domain to align with the target architecture.
All calculations use Value Objects (Percentage, Price, Quantity) for type safety.
"""

from decimal import Decimal

from src.app.infrastructure.config.env import config
from src.app.domain.value_objects import Percentage, Price, Quantity
from src.app.domain.position.results import (
    BuyCalculation,
    SellCalculation,
    AverageCostCalculation,
    PnLCalculation,
)


class PositionManager:
    """
    Manages position sizing and cost calculations.
    
    Uses Value Objects for type-safe calculations and clear domain semantics.
    """

    def __init__(
        self,
        max_position_size: Percentage | None = None,
        core_position_pct: Percentage | None = None
    ) -> None:
        """
        Args:
            max_position_size: Max percentage of balance to use per trade (Percentage VO).
            core_position_pct: Percentage to keep as core position (Percentage VO).
        """
        self.max_position_size = max_position_size or Percentage.from_float(
            config.config.MAX_POSITION_SIZE
        )
        self.core_position_pct = core_position_pct or Percentage.from_float(
            config.config.CORE_POSITION_PCT
        )

    def calculate_buy_quantity(
        self,
        usdt_balance: Quantity,
        price: Price
    ) -> BuyCalculation:
        """
        Calculate quantity to buy based on balance and price.
        
        Formula:
            usdt_to_use = usdt_balance × max_position_size
            quantity_to_buy = usdt_to_use / price
        
        Args:
            usdt_balance: Available USDT balance (Quantity VO)
            price: Current price (Price VO)
        
        Returns:
            BuyCalculation with usdt_to_use and quantity_to_buy
        
        Example:
            >>> manager = PositionManager(
            ...     max_position_size=Percentage.from_float(0.5),
            ...     core_position_pct=Percentage.from_float(0.7)
            ... )
            >>> usdt = Quantity(Decimal("1000"), "USDT")
            >>> price = Price(Decimal("100"), "USDT")
            >>> result = manager.calculate_buy_quantity(usdt, price)
            >>> result.usdt_to_use.value
            Decimal('500')
            >>> result.quantity_to_buy.value
            Decimal('5')
        """
        usdt_to_use_value = self.max_position_size.apply_to(usdt_balance.value)
        
        if price.value > Decimal("0"):
            quantity_value = usdt_to_use_value / price.value
        else:
            quantity_value = Decimal("0")
        
        # Extract asset symbol from price (e.g., "USDT" -> "QRL" for QRLUSDT)
        # Simplified: assume price is for the trading pair
        return BuyCalculation(
            usdt_to_use=Quantity(usdt_to_use_value, "USDT"),
            quantity_to_buy=Quantity(quantity_value),
        )

    def calculate_sell_quantity(
        self,
        total_quantity: Quantity,
        core_quantity: Quantity
    ) -> SellCalculation:
        """
        Calculate quantity to sell.
        
        Formula:
            tradeable = total - core
            to_sell = tradeable × max_position_size
        
        Args:
            total_quantity: Total holdings (Quantity VO)
            core_quantity: Core/protected holdings (Quantity VO)
        
        Returns:
            SellCalculation with tradeable and to_sell quantities
        
        Example:
            >>> manager = PositionManager(
            ...     max_position_size=Percentage.from_float(0.5),
            ...     core_position_pct=Percentage.from_float(0.7)
            ... )
            >>> total = Quantity(Decimal("100"))
            >>> core = Quantity(Decimal("70"))
            >>> result = manager.calculate_sell_quantity(total, core)
            >>> result.tradeable_quantity.value
            Decimal('30')
            >>> result.quantity_to_sell.value
            Decimal('15')
        """
        tradeable_value = total_quantity.value - core_quantity.value
        to_sell_value = self.max_position_size.apply_to(tradeable_value)
        
        return SellCalculation(
            tradeable_quantity=Quantity(tradeable_value),
            quantity_to_sell=Quantity(to_sell_value),
        )

    def calculate_new_average_cost(
        self,
        old_avg_cost: Price,
        old_total_invested: Quantity,
        current_balance: Quantity,
        buy_price: Price,
        buy_quantity: Quantity,
        usdt_spent: Quantity,
    ) -> AverageCostCalculation:
        """
        Calculate new weighted average cost after a buy.
        
        Formula:
            new_total_invested = old_total_invested + usdt_spent
            new_balance = current_balance + buy_quantity
            new_avg_cost = new_total_invested / new_balance
        
        Args:
            old_avg_cost: Previous average cost (Price VO)
            old_total_invested: Previous total invested USDT (Quantity VO)
            current_balance: Current holdings before buy (Quantity VO)
            buy_price: Price of this buy (Price VO)
            buy_quantity: Amount being bought (Quantity VO)
            usdt_spent: USDT spent on this buy (Quantity VO)
        
        Returns:
            AverageCostCalculation with new averages
        
        Example:
            >>> old_avg = Price(Decimal("100"), "USDT")
            >>> old_invested = Quantity(Decimal("10000"), "USDT")
            >>> balance = Quantity(Decimal("100"))
            >>> buy_price = Price(Decimal("110"), "USDT")
            >>> buy_qty = Quantity(Decimal("50"))
            >>> spent = Quantity(Decimal("5500"), "USDT")
            >>> result = manager.calculate_new_average_cost(
            ...     old_avg, old_invested, balance, buy_price, buy_qty, spent
            ... )
            >>> result.new_average_cost.value
            Decimal('103.333...')
        """
        new_total_invested_value = old_total_invested.value + usdt_spent.value
        new_balance_value = current_balance.value + buy_quantity.value

        if new_balance_value > Decimal("0"):
            new_avg_cost_value = new_total_invested_value / new_balance_value
        else:
            new_avg_cost_value = buy_price.value

        return AverageCostCalculation(
            new_average_cost=Price(new_avg_cost_value, "USDT"),
            new_total_invested=Quantity(new_total_invested_value, "USDT"),
            new_balance=Quantity(new_balance_value),
        )

    def calculate_pnl_after_sell(
        self,
        avg_cost: Price,
        sell_price: Price,
        sell_quantity: Quantity,
        current_balance: Quantity,
        old_realized_pnl: Decimal,
    ) -> PnLCalculation:
        """
        Calculate P&L after a sell.
        
        Formula:
            realized_from_trade = (sell_price - avg_cost) × sell_quantity
            new_realized = old_realized + realized_from_trade
            new_balance = current_balance - sell_quantity
            unrealized = (sell_price - avg_cost) × new_balance
        
        Args:
            avg_cost: Average cost basis (Price VO)
            sell_price: Sell execution price (Price VO)
            sell_quantity: Amount being sold (Quantity VO)
            current_balance: Current holdings before sell (Quantity VO)
            old_realized_pnl: Previous realized PnL (Decimal)
        
        Returns:
            PnLCalculation with all PnL components
        
        Example:
            >>> avg = Price(Decimal("100"), "USDT")
            >>> sell_price = Price(Decimal("120"), "USDT")
            >>> sell_qty = Quantity(Decimal("50"))
            >>> balance = Quantity(Decimal("100"))
            >>> old_pnl = Decimal("0")
            >>> result = manager.calculate_pnl_after_sell(
            ...     avg, sell_price, sell_qty, balance, old_pnl
            ... )
            >>> result.realized_pnl_from_trade
            Decimal('1000')
            >>> result.new_balance.value
            Decimal('50')
        """
        realized_pnl_from_trade = (sell_price.value - avg_cost.value) * sell_quantity.value
        new_realized_pnl = old_realized_pnl + realized_pnl_from_trade
        new_balance_value = current_balance.value - sell_quantity.value

        if new_balance_value > Decimal("0"):
            unrealized_pnl = (sell_price.value - avg_cost.value) * new_balance_value
        else:
            unrealized_pnl = Decimal("0")

        return PnLCalculation(
            realized_pnl_from_trade=realized_pnl_from_trade,
            new_realized_pnl=new_realized_pnl,
            new_balance=Quantity(new_balance_value),
            unrealized_pnl=unrealized_pnl,
            average_cost=avg_cost,
            total_invested=Quantity(avg_cost.value * new_balance_value, "USDT"),
        )


__all__ = ["PositionManager"]
