"""Sub-account transfer route."""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account/sub-account", tags=["Sub-Accounts"])
logger = logging.getLogger(__name__)


@router.post("/transfer")
async def transfer_between_sub_accounts(
    from_account: str,
    to_account: str,
    asset: str,
    amount: str,
    from_type: str = "SPOT",
    to_type: str = "SPOT",
):
    from infrastructure.external import mexc_client
    from infrastructure.config import config

    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
            },
        )

    try:
        result = await mexc_client.transfer_between_sub_accounts(
            from_account=from_account,
            to_account=to_account,
            asset=asset,
            amount=amount,
            from_type=from_type,
            to_type=to_type,
        )
        logger.info(
            f"Transfer executed: {amount} {asset} from {from_account} ({from_type}) to {to_account} ({to_type})"
        )
        return {
            "success": True,
            "transfer": {
                "from_account": from_account,
                "to_account": to_account,
                "asset": asset,
                "amount": amount,
                "from_type": from_type,
                "to_type": to_type,
            },
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Transfer failed", "message": str(e)},
        )
