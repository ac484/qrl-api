"""Sub-account endpoints wrapper combining spot and broker APIs."""
from infrastructure.external.mexc_client.sub_account_spot_repo import SubAccountSpotRepoMixin
from infrastructure.external.mexc_client.sub_account_broker_repo import SubAccountBrokerRepoMixin
from infrastructure.external.mexc_client.sub_account_facade import SubAccountFacadeMixin


class SubAccountEndpoints(
    SubAccountSpotRepoMixin, SubAccountBrokerRepoMixin, SubAccountFacadeMixin
):
    """Unified mixin for all sub-account endpoints."""


__all__ = ["SubAccountEndpoints"]
