"""Account endpoints wrapper."""
from src.app.infrastructure.external.mexc.repos.account_repo import AccountRepoMixin

AccountEndpoints = AccountRepoMixin

__all__ = ["AccountEndpoints"]
