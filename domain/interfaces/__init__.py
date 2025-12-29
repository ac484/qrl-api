"""Domain interfaces package"""
from .account import IAccountDataProvider
from .cost import ICostRepository
from .market import IMarketDataProvider
from .position import IPositionRepository
from .price import IPriceRepository
from .trade import ITradeRepository

__all__ = [
    "IAccountDataProvider",
    "ICostRepository",
    "IMarketDataProvider",
    "IPositionRepository",
    "IPriceRepository",
    "ITradeRepository",
]
