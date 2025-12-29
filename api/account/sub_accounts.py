"""
Account sub-accounts route.
"""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


@router.get("/sub-accounts")
async def get_sub_accounts():
    """Get list of sub-accounts (alias for /account/sub-account/list)."""
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.config.config import config

    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "API keys not configured",
                    "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                },
            )

        sub_account_id = config.active_sub_account_identifier
        if not sub_account_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Sub-account not configured",
                    "message": "Set SUB_ACCOUNT_ID or SUB_ACCOUNT_NAME environment variable",
                    "mode": config.SUB_ACCOUNT_MODE,
                },
            )

        async with mexc_client:
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            balance_data = await mexc_client.get_sub_account_balance(sub_account_id)
            logger.info(
                f"Retrieved sub-account balance for {sub_account_id} using {mode} API"
            )
            return {
                "success": True,
                "mode": mode,
                "sub_account_id": sub_account_id,
                "balance": balance_data,
                "timestamp": datetime.now().isoformat(),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))
