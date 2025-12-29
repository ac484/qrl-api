"""
Cloud Scheduler Tasks for Google Cloud Run
HTTP endpoints triggered by Google Cloud Scheduler
(Simplified - Direct MEXC API calls, no Redis storage)
"""
import json
import logging
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/01-min-job")
async def task_sync_balance(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None)
):
    """
    Cloud Scheduler Task: Get MEXC account balance (No Redis storage)
    Triggered by: Cloud Scheduler (every 1 minute)
    
    Simply validates API connection and returns balance data
    
    Authentication:
    - Accepts X-CloudScheduler header (legacy)
    - Accepts Authorization header with Bearer token (OIDC)
    """
    # Verify request is from Cloud Scheduler (support both auth methods)
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] 01-min-job authenticated via {auth_method}")
    
    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            logger.warning("[Cloud Task] API keys not configured, skipping balance sync")
            return {"status": "skipped", "reason": "API keys not configured"}
        
        async with mexc_client:
            # Get account info from MEXC
            account_info = await mexc_client.get_account_info()
            
            # Extract balances (no storage, just validation)
            qrl_balance = 0.0
            usdt_balance = 0.0
            all_balances = {}
            
            for balance in account_info.get("balances", []):
                asset = balance.get("asset")
                free = float(balance.get("free", 0))
                locked = float(balance.get("locked", 0))
                
                if free > 0 or locked > 0:
                    all_balances[asset] = {
                        "free": str(free),
                        "locked": str(locked),
                        "total": str(free + locked)
                    }
                
                if asset == "QRL":
                    qrl_balance = free
                elif asset == "USDT":
                    usdt_balance = free
            
            logger.info(
                f"[Cloud Task] Balance synced (Direct API) - "
                f"QRL: {qrl_balance:.2f}, USDT: {usdt_balance:.2f}, Total assets: {len(all_balances)}"
            )
            
            return {
                "status": "success",
                "task": "01-min-job",
                "data": {
                    "qrl_balance": qrl_balance,
                    "usdt_balance": usdt_balance,
                    "total_assets": len(all_balances)
                },
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Balance sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/05-min-job")
async def task_update_price(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None)
):
    """
    Cloud Scheduler Task: Get QRL/USDT price (No Redis storage)
    Triggered by: Cloud Scheduler (every 5 minutes)
    
    Simply validates API connection and returns price data
    
    Authentication:
    - Accepts X-CloudScheduler header (legacy)
    - Accepts Authorization header with Bearer token (OIDC)
    """
    # Verify request is from Cloud Scheduler (support both auth methods)
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] 05-min-job authenticated via {auth_method}")
    
    try:
        async with mexc_client:
            # Get ticker from MEXC (no storage)
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            
            # Extract data from ticker
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            price_change_pct = float(ticker.get("priceChangePercent", 0))
            high_24h = float(ticker.get("highPrice", 0))
            low_24h = float(ticker.get("lowPrice", 0))
            
            logger.info(
                f"[Cloud Task] Price fetched (Direct API) - "
                f"Price: {price:.5f}, Change: {price_change_pct:.2f}%, Volume: {volume_24h:.2f}"
            )
            
            return {
                "status": "success",
                "task": "05-min-job",
                "data": {
                    "price": price,
                    "volume_24h": volume_24h,
                    "price_change_percent": price_change_pct,
                    "high_24h": high_24h,
                    "low_24h": low_24h
                },
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Price update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/15-min-job")
async def task_update_cost(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None)
):
    """
    Cloud Scheduler Task: Get current price (Simplified - No cost tracking without Redis)
    Triggered by: Cloud Scheduler (every 15 minutes)
    
    Simply validates API connection
    
    Authentication:
    - Accepts X-CloudScheduler header (legacy)
    - Accepts Authorization header with Bearer token (OIDC)
    """
    # Verify request is from Cloud Scheduler (support both auth methods)
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] 15-min-job authenticated via {auth_method}")
    
    try:
        async with mexc_client:
            # Just get current price (no cost calculation without Redis)
            ticker = await mexc_client.get_ticker_price("QRLUSDT")
            current_price = float(ticker.get("price", 0))
        
        logger.info(f"[Cloud Task] Price check (Direct API) - Current: ${current_price:.5f}")
        
        return {
            "status": "success",
            "task": "15-min-job",
            "data": {
                "current_price": current_price
            },
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Cost update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
