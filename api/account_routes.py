"""
Account management API routes (aggregated).
Delegates to api.account.* modules to match README structure.
"""
from fastapi import APIRouter

from api.account.balance import router as balance_router, get_account_balance
from api.account.orders import router as orders_router, get_orders
from api.account.trades import router as trades_router, get_trades
from api.account.sub_accounts import router as sub_accounts_router, get_sub_accounts

router = APIRouter()
router.include_router(balance_router)
router.include_router(orders_router)
router.include_router(trades_router)
router.include_router(sub_accounts_router)

__all__ = [
    "router",
    "get_account_balance",
    "get_orders",
    "get_trades",
    "get_sub_accounts",
]
