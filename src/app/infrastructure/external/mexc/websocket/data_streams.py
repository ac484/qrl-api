"""
Channel builders for MEXC user data streams (private WebSocket channels).
"""
from __future__ import annotations

DEFAULT_USER_STREAM_CHANNELS = [
    "spot@private.account.v3.api.pb",
    "spot@private.deals.v3.api.pb",
    "spot@private.orders.v3.api.pb",
]


def account_update_stream() -> str:
    """Account balance and position updates."""
    return "spot@private.account.v3.api.pb"


def user_deals_stream() -> str:
    """Filled trade events for the account."""
    return "spot@private.deals.v3.api.pb"


def user_orders_stream() -> str:
    """Order lifecycle updates for the account."""
    return "spot@private.orders.v3.api.pb"


__all__ = [
    "DEFAULT_USER_STREAM_CHANNELS",
    "account_update_stream",
    "user_deals_stream",
    "user_orders_stream",
]
