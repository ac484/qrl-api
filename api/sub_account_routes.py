"""
Sub-account management API routes
"""
from fastapi import APIRouter, HTTPException
from typing import Optional
from datetime import datetime
import logging

router = APIRouter(prefix="/account/sub-account", tags=["Sub-Accounts"])
logger = logging.getLogger(__name__)


@router.get("/list")
async def get_sub_accounts():
    """
    Get list of sub-accounts
    
    Returns:
        List of sub-accounts with details
    """
    from infrastructure.external import mexc_client
    from infrastructure.config import config
    
    try:
        # Check if API keys are configured
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "API keys not configured",
                    "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables"
                }
            )
        
        async with mexc_client:
            # Get sub-accounts list using unified interface
            sub_accounts = await mexc_client.get_sub_accounts()
            
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            logger.info(f"Retrieved {len(sub_accounts)} sub-accounts using {mode} API")
            
            return {
                "success": True,
                "mode": mode,
                "sub_accounts": sub_accounts,
                "count": len(sub_accounts),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get sub-accounts: {e}")
        
        # Check for permission errors
        error_msg = str(e).lower()
        if "403" in error_msg or "permission" in error_msg or "forbidden" in error_msg:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Insufficient permissions",
                    "message": "Sub-account access requires proper API permissions",
                    "help": "Ensure your MEXC account has the required API access enabled"
                }
            )
        
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch sub-accounts",
                "message": str(e)
            }
        )


@router.get("/balance")
async def get_sub_account_balance(
    identifier: Optional[str] = None,
    email: Optional[str] = None,
    sub_account_id: Optional[str] = None
):
    """
    Get sub-account balance
    
    Query parameters:
        identifier: Sub-account identifier (subAccountId for SPOT, subAccount name for BROKER)
        email: Sub-account email (alternative for SPOT API)
        sub_account_id: Sub-account ID (alternative parameter name)
        
    Returns:
        Sub-account balance information
    """
    from infrastructure.external import mexc_client
    from infrastructure.config import config
    
    # Determine identifier (support multiple parameter names)
    sub_account_identifier = identifier or email or sub_account_id
    
    # Validate identifier is provided
    if not sub_account_identifier:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing identifier",
                "message": "Sub-account identifier must be provided",
                "help": "Add ?identifier=xxx to the request (subAccountId for SPOT, subAccount name for BROKER)"
            }
        )
    
    try:
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        logger.info(f"Fetching balance for sub-account: {sub_account_identifier} using {mode} API")
        
        # Get sub-account balance from MEXC API
        balance_data = await mexc_client.get_sub_account_balance(sub_account_identifier)
        
        logger.info(f"Successfully retrieved balance for sub-account: {sub_account_identifier}")
        
        return {
            "success": True,
            "mode": mode,
            "sub_account_identifier": sub_account_identifier,
            "balance": balance_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except NotImplementedError as e:
        # Spot API limitation
        logger.warning(f"Spot API limitation: {e}")
        raise HTTPException(
            status_code=501,
            detail={
                "error": "Not supported in SPOT mode",
                "message": str(e),
                "help": "Use sub-account's own API key to query balance, or switch to BROKER mode if available"
            }
        )
    except ValueError as e:
        # Validation error
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Validation error",
                "message": str(e)
            }
        )
    except Exception as e:
        logger.error(f"Failed to get sub-account balance: {e}")
        
        # Check if it's a permission error
        error_msg = str(e).lower()
        if "403" in error_msg or "permission" in error_msg or "forbidden" in error_msg:
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Insufficient permissions",
                    "message": "Sub-account access requires proper API permissions",
                    "help": "Ensure your MEXC account has the required API access enabled"
                }
            )
        
        # Generic error
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch sub-account balance",
                "message": str(e)
            }
        )


@router.post("/transfer")
async def transfer_between_sub_accounts(
    from_account: str,
    to_account: str,
    asset: str,
    amount: str,
    from_type: str = "SPOT",
    to_type: str = "SPOT"
):
    """
    Transfer between sub-accounts or main account ↔ sub-account
    
    Request body:
        from_account: Source account identifier (empty string for main account in SPOT mode)
        to_account: Destination account identifier (empty string for main account in SPOT mode)
        asset: Asset symbol (e.g., "USDT", "BTC")
        amount: Transfer amount (string)
        from_type: Source account type for SPOT API (SPOT, MARGIN, ETF, CONTRACT)
        to_type: Destination account type for SPOT API (SPOT, MARGIN, ETF, CONTRACT)
    
    Returns:
        dict: Transfer result with transaction ID
    """
    from infrastructure.external import mexc_client
    from infrastructure.config import config
    
    # Validate API keys
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables"
            }
        )
    
    try:
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        
        if mode == "BROKER":
            # Broker API transfer
            result = await mexc_client.broker_transfer_between_sub_accounts(
                from_account, to_account, asset, amount
            )
        else:
            # Spot API universal transfer
            # Empty string means main account
            from_acc = from_account if from_account else None
            to_acc = to_account if to_account else None
            
            result = await mexc_client.transfer_between_sub_accounts(
                from_type, to_type, asset, amount, from_acc, to_acc
            )
        
        logger.info(f"Transfer successful: {from_account} -> {to_account}, {amount} {asset}")
        
        return {
            "success": True,
            "mode": mode,
            "transfer": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Transfer failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Transfer failed",
                "message": str(e)
            }
        )


@router.post("/api-key")
async def create_sub_account_api_key(
    sub_account_identifier: str,
    note: str,
    permissions: str
):
    """
    Create API key for sub-account
    
    Request body:
        sub_account_identifier: Sub-account ID (SPOT) or name (BROKER)
        note: API key description
        permissions: Permissions string
            - SPOT API: JSON array string (e.g., '["SPOT"]')
            - BROKER API: Comma-separated string (e.g., "SPOT_ACCOUNT_READ,SPOT_ACCOUNT_WRITE")
    
    Returns:
        dict: API key details including secretKey (STORE SECURELY!)
    """
    from infrastructure.external import mexc_client
    from infrastructure.config import config
    
    # Validate API keys
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables"
            }
        )
    
    try:
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        
        if mode == "BROKER":
            # Broker API
            result = await mexc_client.create_broker_sub_account_api_key(
                sub_account_identifier, permissions, note
            )
        else:
            # Spot API - permissions should be a list
            import json
            try:
                perms_list = json.loads(permissions) if isinstance(permissions, str) else permissions
            except json.JSONDecodeError:
                perms_list = [permissions]  # Single permission
            
            result = await mexc_client.create_sub_account_api_key(
                sub_account_identifier, note, perms_list
            )
        
        logger.info(f"API key created for sub-account: {sub_account_identifier}")
        
        return {
            "success": True,
            "mode": mode,
            "api_key_data": result,
            "warning": "Store the secretKey securely - it will not be shown again!",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to create API key",
                "message": str(e)
            }
        )


@router.delete("/api-key")
async def delete_sub_account_api_key(
    sub_account_id: str,
    api_key: str
):
    """
    Delete sub-account API key (SPOT API only)
    
    Query parameters:
        sub_account_id: Sub-account ID
        api_key: API key to delete
    
    Returns:
        dict: Deletion confirmation
    """
    from infrastructure.external import mexc_client
    from infrastructure.config import config
    
    # Validate API keys
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables"
            }
        )
    
    # Check mode
    mode = "BROKER" if config.is_broker_mode else "SPOT"
    if mode == "BROKER":
        raise HTTPException(
            status_code=501,
            detail={
                "error": "Not supported in BROKER mode",
                "message": "BROKER API does not support API key deletion via this endpoint"
            }
        )
    
    try:
        result = await mexc_client.delete_sub_account_api_key(sub_account_id, api_key)
        
        logger.info(f"API key deleted for sub-account: {sub_account_id}")
        
        return {
            "success": True,
            "mode": mode,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to delete API key: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete API key",
                "message": str(e)
            }
        )
