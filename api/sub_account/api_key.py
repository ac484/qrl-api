"""Sub-account API key management routes."""
from datetime import datetime
import logging
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/account/sub-account", tags=["Sub-Accounts"])
logger = logging.getLogger(__name__)


@router.post("/api-key")
async def create_sub_account_api_key(
    sub_account: str,
    note: str = "QRL Trading API",
    permissions: str = "READ_ONLY",
):
    from infrastructure.external import mexc_client

    try:
        result = await mexc_client.create_sub_account_api_key(
            sub_account=sub_account,
            note=note,
            permissions=permissions,
        )
        logger.info(f"Sub-account API key created for {sub_account}")
        return {
            "success": True,
            "sub_account": sub_account,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to create sub-account API key: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "API key creation failed", "message": str(e)},
        )


@router.delete("/api-key")
async def delete_sub_account_api_key(sub_account: str, api_key: str):
    from infrastructure.external import mexc_client

    try:
        result = await mexc_client.delete_sub_account_api_key(
            sub_account=sub_account, api_key=api_key
        )
        logger.info(f"Sub-account API key deleted for {sub_account}")
        return {
            "success": True,
            "sub_account": sub_account,
            "result": result,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Failed to delete sub-account API key: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "API key deletion failed", "message": str(e)},
        )
