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
    from infrastructure.external.mexc_client import mexc_client
    
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
                f"Account balance fetched - QRL: {qrl_total:.2f}, USDT: {usdt_total:.2f}"
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


@router.get("/orders")
async def get_orders(symbol: str = "QRLUSDT", limit: int = 50):
    """
    Get user's open orders (real-time from MEXC API)
    
    Args:
        symbol: Trading symbol (default: QRLUSDT)
        limit: Number of orders to return
        
    Returns:
        List of open orders with details
    """
    from infrastructure.external.mexc_client import mexc_client
    
    try:
        async with mexc_client:
            # Get open orders from MEXC
            orders = await mexc_client.get_open_orders(symbol)
            
            logger.info(f"Retrieved {len(orders)} open orders for {symbol}")
            
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "orders": orders,
                "count": len(orders),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get orders for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trades")
async def get_trades(symbol: str = "QRLUSDT", limit: int = 50):
    """
    Get user's trade history (real-time from MEXC API)
    
    Args:
        symbol: Trading symbol (default: QRLUSDT)
        limit: Number of trades to return
        
    Returns:
        List of user's executed trades
    """
    from infrastructure.external.mexc_client import mexc_client
    
    try:
        async with mexc_client:
            # Get user's trades from MEXC
            trades = await mexc_client.get_my_trades(symbol, limit=limit)
            
            logger.info(f"Retrieved {len(trades)} trades for {symbol}")
            
            return {
                "success": True,
                "source": "api",
                "symbol": symbol,
                "trades": trades,
                "count": len(trades),
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"Failed to get trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sub-accounts")
async def get_sub_accounts():
    """
    Get list of sub-accounts (alias for /account/sub-account/list)
    
    Returns:
        List of sub-accounts with details
    """
    from infrastructure.external.mexc_client import mexc_client
    from infrastructure.config.config import config
    
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
        
        # Get configured sub-account identifier
        sub_account_id = config.active_sub_account_identifier
        
        if not sub_account_id:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Sub-account not configured",
                    "message": "Set SUB_ACCOUNT_ID or SUB_ACCOUNT_NAME environment variable",
                    "mode": config.SUB_ACCOUNT_MODE
                }
            )
        
        async with mexc_client:
            # Get sub-account balance using the configured identifier
            mode = "BROKER" if config.is_broker_mode else "SPOT"
            
            try:
                balance_data = await mexc_client.get_sub_account_balance(sub_account_id)
                
                logger.info(f"Retrieved balance for sub-account: {sub_account_id} using {mode} API")
                
                return {
                    "success": True,
                    "mode": mode,
                    "sub_account_id": sub_account_id,
                    "balance": balance_data,
                    "timestamp": datetime.now().isoformat()
                }
            except NotImplementedError as e:
                # Spot API limitation - try alternative approach
                logger.warning(f"Spot API limitation: {e}")
                
                # For SPOT mode, we can't query sub-account balance from main account
                # Return configured sub-account info instead
                return {
                    "success": True,
                    "mode": mode,
                    "sub_account_id": sub_account_id,
                    "message": "Sub-account configured in SPOT mode",
                    "note": "Use sub-account's own API key to query balance",
                    "timestamp": datetime.now().isoformat()
                }
    
    except HTTPException:
        raise
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
