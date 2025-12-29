"""
Sub-account management API routes (aggregated).
"""
from fastapi import APIRouter

from api.sub_account.list import router as list_router, get_sub_accounts
from api.sub_account.balance import router as balance_router, get_sub_account_balance
from api.sub_account.transfer import router as transfer_router, transfer_between_sub_accounts
from api.sub_account.api_key import (
    router as api_key_router,
    create_sub_account_api_key,
    delete_sub_account_api_key,
)

router = APIRouter()
router.include_router(list_router)
router.include_router(balance_router)
router.include_router(transfer_router)
router.include_router(api_key_router)

__all__ = [
    "router",
    "get_sub_accounts",
    "get_sub_account_balance",
    "transfer_between_sub_accounts",
    "create_sub_account_api_key",
    "delete_sub_account_api_key",
]
