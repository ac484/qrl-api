"""Sub-account endpoints wrapper combining spot and broker APIs."""
from src.app.infrastructure.external.mexc.repos.sub_account_spot_repo import (
    SubAccountSpotRepoMixin,
)
from src.app.infrastructure.external.mexc.repos.sub_account_broker_repo import (
    SubAccountBrokerRepoMixin,
)
from src.app.infrastructure.external.mexc.facades.sub_account_facade import SubAccountFacadeMixin


class SubAccountEndpoints(
    SubAccountSpotRepoMixin, SubAccountBrokerRepoMixin, SubAccountFacadeMixin
):
    """Unified mixin for all sub-account endpoints."""


__all__ = ["SubAccountEndpoints"]
