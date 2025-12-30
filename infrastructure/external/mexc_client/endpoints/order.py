"""Order endpoints wrapper."""
from infrastructure.external.mexc_client.trade_repo import TradeRepoMixin

OrderEndpoints = TradeRepoMixin

__all__ = ["OrderEndpoints"]
