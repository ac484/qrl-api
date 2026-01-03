"""
Position calculation result types.

These immutable dataclasses replace Dict[str, Any] returns from PositionManager,
providing type safety and clear contracts.
"""

from dataclasses import dataclass
from decimal import Decimal

from src.app.domain.value_objects import Price, Quantity


@dataclass(frozen=True, slots=True)
class BuyCalculation:
    """Result of buy quantity calculation.
    
    Attributes:
        usdt_to_use: Amount of USDT to spend on purchase
        quantity_to_buy: Amount of asset to purchase
    """
    usdt_to_use: Quantity
    quantity_to_buy: Quantity


@dataclass(frozen=True, slots=True)
class SellCalculation:
    """Result of sell quantity calculation.
    
    Attributes:
        tradeable_quantity: Total amount available to sell
        quantity_to_sell: Amount to actually sell based on max_position_size
    """
    tradeable_quantity: Quantity
    quantity_to_sell: Quantity


@dataclass(frozen=True, slots=True)
class AverageCostCalculation:
    """Result of average cost calculation after buy.
    
    Attributes:
        new_average_cost: Weighted average cost after purchase
        new_total_invested: Total USDT invested after purchase
        new_balance: New asset balance after purchase
    """
    new_average_cost: Price
    new_total_invested: Quantity  # USDT
    new_balance: Quantity  # Asset


@dataclass(frozen=True, slots=True)
class PnLCalculation:
    """Result of PnL calculation after sell.
    
    Attributes:
        realized_pnl_from_trade: PnL realized from this specific sell
        new_realized_pnl: Total cumulative realized PnL
        new_balance: New asset balance after sell
        unrealized_pnl: Unrealized PnL on remaining position
        average_cost: Average cost basis (unchanged by sell)
        total_invested: Total USDT still invested
    """
    realized_pnl_from_trade: Decimal
    new_realized_pnl: Decimal
    new_balance: Quantity
    unrealized_pnl: Decimal
    average_cost: Price
    total_invested: Quantity  # USDT


__all__ = [
    "BuyCalculation",
    "SellCalculation",
    "AverageCostCalculation",
    "PnLCalculation",
]
