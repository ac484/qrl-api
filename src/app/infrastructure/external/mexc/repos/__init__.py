"""MEXC repository adapters."""
from src.app.infrastructure.external.mexc.repos.account_repo import (
    AccountRepoMixin,
    AccountRepository,
)
from src.app.infrastructure.external.mexc.repos.trade_repo import TradeRepoMixin
from src.app.infrastructure.external.mexc.repos.sub_account_broker_repo import (
    SubAccountBrokerRepoMixin,
)
from src.app.infrastructure.external.mexc.repos.sub_account_spot_repo import (
    SubAccountSpotRepoMixin,
)

# Backward-compatible aliases expected by legacy imports
TradeRepository = TradeRepoMixin
SubAccountBrokerRepository = SubAccountBrokerRepoMixin
SubAccountSpotRepository = SubAccountSpotRepoMixin

__all__ = [
    "AccountRepoMixin",
    "AccountRepository",
    "TradeRepoMixin",
    "TradeRepository",
    "SubAccountBrokerRepoMixin",
    "SubAccountBrokerRepository",
    "SubAccountSpotRepoMixin",
    "SubAccountSpotRepository",
]
