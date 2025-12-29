"""Sub-account balance route."""
from datetime import datetime
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account/sub-account", tags=["Sub-Accounts"])
logger = logging.getLogger(__name__)


@router.get("/balance")
async def get_sub_account_balance(
    identifier: Optional[str] = None,
    email: Optional[str] = None,
    sub_account_id: Optional[str] = None,
):
    from infrastructure.external import mexc_client
    from infrastructure.config import config

    sub_account_identifier = identifier or email or sub_account_id
    if not sub_account_identifier:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing identifier",
                "message": "Sub-account identifier must be provided",
                "help": "Add ?identifier=xxx to the request (subAccountId for SPOT, subAccount name for BROKER)",
            },
        )

    try:
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        logger.info(f"Fetching balance for sub-account: {sub_account_identifier} using {mode} API")
        balance_data = await mexc_client.get_sub_account_balance(sub_account_identifier)
        return {
            "success": True,
            "mode": mode,
            "sub_account_identifier": sub_account_identifier,
            "balance": balance_data,
            "timestamp": datetime.now().isoformat(),
        }
    except NotImplementedError as e:
        logger.warning(f"Spot API limitation: {e}")
        raise HTTPException(
            status_code=501,
            detail={
                "error": "Not supported in SPOT mode",
                "message": str(e),
                "help": "Use sub-account's own API key to query balance, or switch to BROKER mode if available",
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail={"error": "Validation error", "message": str(e)})
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
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
            detail={"error": "Failed to fetch sub-account balance", "message": str(e)},
        )
