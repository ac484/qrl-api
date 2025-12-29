"""Sub-account list route."""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account/sub-account", tags=["Sub-Accounts"])
logger = logging.getLogger(__name__)


@router.get("/list")
async def get_sub_accounts():
    from infrastructure.external import mexc_client
    from infrastructure.config import config

    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "API keys not configured",
                    "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                },
            )

        async with mexc_client:
            sub_accounts = await mexc_client.get_sub_accounts()
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            logger.info(f"Retrieved {len(sub_accounts)} sub-accounts using {mode} API")
            return {
                "success": True,
                "mode": mode,
                "sub_accounts": sub_accounts,
                "count": len(sub_accounts),
                "timestamp": datetime.now().isoformat(),
            }
    except Exception as e:
        logger.error(f"Failed to get sub-accounts: {e}")
        error_msg = str(e).lower()
        if "403" in error_msg or "permission" in error_msg or "forbidden" in error_msg:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Insufficient permissions",
                    "message": "Sub-account access requires proper API permissions",
                    "help": "Ensure your MEXC account has the required API access enabled",
                },
            )
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to fetch sub-accounts", "message": str(e)},
        )
