"""
Account management API routes
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging

router = APIRouter(prefix="/account", tags=["Account"])
logger = logging.getLogger(__name__)


@router.get("/balance")
async def get_account_balance():
    """
    Get account balance (real-time from MEXC API)
    
    Returns:
        Account balance with QRL and USDT totals
    """
    from infrastructure.external.mexc_client from infrastructure.external import mexc_client
    
    try:
        async with mexc_client:
            # Get account info from MEXC
            account_info = await mexc_client.get_account_info()
            
            # Extract balances
            balances = account_info.get("balances", [])
            
            # Find QRL and USDT balances
            qrl_balance = {"asset": "QRL", "free": "0", "locked": "0"}
            usdt_balance = {"asset": "USDT", "free": "0", "locked": "0"}
            
            for balance in balances:
                if balance.get("asset") == "QRL":
                    qrl_balance = balance
                elif balance.get("asset") == "USDT":
                    usdt_balance = balance
            
            # Calculate totals
            qrl_total = float(qrl_balance.get("free", 0)) + float(qrl_balance.get("locked", 0))
            usdt_total = float(usdt_balance.get("free", 0)) + float(usdt_balance.get("locked", 0))
            
            logger.info(
                f"Account balance fetched - QRL: {qrl_total:.4f}, USDT: {usdt_total:.2f}"
            )
            
            return {
                "success": True,
                "source": "api",
                "balances": {
                    "QRL": {
                        "free": qrl_balance.get("free"),
                        "locked": qrl_balance.get("locked"),
                        "total": qrl_total
                    },
                    "USDT": {
                        "free": usdt_balance.get("free"),
                        "locked": usdt_balance.get("locked"),
                        "total": usdt_total
                    }
                },
                "account_type": account_info.get("accountType"),
                "can_trade": account_info.get("canTrade"),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get account balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/balance/redis")
async def get_account_balance_from_redis():
    """
    Get account balance from Redis cache (may be stale)
    
    Returns:
        Cached position data from Redis
    """
    from infrastructure.external.redis_client from infrastructure.external import redis_client
    
    try:
        position = await redis_client.get_position()
        
        if not position:
            raise HTTPException(
                status_code=404,
                detail="No position data in Redis - run /tasks/sync-balance first"
            )
        
        logger.info("Position data retrieved from Redis")
        
        return {
            "success": True,
            "source": "redis",
            "position": position,
            "warning": "This data may be stale - use /account/balance for real-time data",
            "timestamp": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get position from Redis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
