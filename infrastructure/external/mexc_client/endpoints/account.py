"""Account endpoints wrapper."""
from infrastructure.external.mexc_client.account_repo import AccountRepoMixin

AccountEndpoints = AccountRepoMixin

__all__ = ["AccountEndpoints"]
