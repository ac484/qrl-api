"""Market endpoints wrapper."""
from infrastructure.external.mexc_client.market_endpoints import MarketEndpointsMixin

MarketEndpoints = MarketEndpointsMixin

__all__ = ["MarketEndpoints"]
