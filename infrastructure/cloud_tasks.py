"""
Cloud Scheduler Tasks for Google Cloud Run
HTTP endpoints triggered by Google Cloud Scheduler
"""
import json
import logging
from datetime import datetime
from fastapi import APIRouter, Header, HTTPException

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client
from infrastructure.external.redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["Cloud Tasks"])


@router.post("/sync-balance")
async def task_sync_balance(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None)
):
    """
    Cloud Scheduler Task: Sync MEXC account balance to Redis
    Triggered by: Cloud Scheduler (every 1-5 minutes)
    
    Stores:
    1. Raw MEXC API response (permanent)
    2. Processed position data (permanent)
    3. All balance fields from API
    
    Authentication:
    - Accepts X-CloudScheduler header (legacy)
    - Accepts Authorization header with Bearer token (OIDC)
    """
    # Verify request is from Cloud Scheduler (support both auth methods)
    # OIDC sends Authorization: Bearer <token>, legacy sends X-CloudScheduler
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] sync-balance authenticated via {auth_method}")
    
    try:
        if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
            logger.warning("[Cloud Task] API keys not configured, skipping balance sync")
            return {"status": "skipped", "reason": "API keys not configured"}
        
        async with mexc_client:
            # Get account info from MEXC
            account_info = await mexc_client.get_account_info()
            
            # Store raw MEXC API response permanently
            await redis_client.set_mexc_raw_response(
                endpoint="account_info",
                response_data=account_info
            )
            logger.info(f"[Cloud Task] Stored raw account_info response")
            
            # Extract balances
            qrl_balance = 0.0
            usdt_balance = 0.0
            all_balances = {}
            
            for balance in account_info.get("balances", []):
                asset = balance.get("asset")
                free = float(balance.get("free", 0))
                locked = float(balance.get("locked", 0))
                
                # Store all non-zero balances
                if free > 0 or locked > 0:
                    all_balances[asset] = {
                        "free": str(free),
                        "locked": str(locked),
                        "total": str(free + locked)
                    }
                
                # Track QRL and USDT specifically
                if asset == "QRL":
                    qrl_balance = free
                elif asset == "USDT":
                    usdt_balance = free
            
            # Update Redis with complete position data
            position_data = {
                "qrl_balance": str(qrl_balance),
                "usdt_balance": str(usdt_balance),
                "qrl_locked": str(all_balances.get("QRL", {}).get("locked", "0")),
                "usdt_locked": str(all_balances.get("USDT", {}).get("locked", "0")),
                "all_balances": json.dumps(all_balances),
                "account_type": account_info.get("accountType", "SPOT"),
                "can_trade": str(account_info.get("canTrade", False)),
                "can_withdraw": str(account_info.get("canWithdraw", False)),
                "can_deposit": str(account_info.get("canDeposit", False)),
                "update_time": str(account_info.get("updateTime", 0)),
                "permissions": json.dumps(account_info.get("permissions", [])),
                "maker_commission": str(account_info.get("makerCommission", 0)),
                "taker_commission": str(account_info.get("takerCommission", 0)),
                "updated_at": datetime.now().isoformat()
            }
            
            await redis_client.set_position(position_data)
            
            logger.info(
                f"[Cloud Task] Balance synced - "
                f"QRL: {qrl_balance:.2f} (locked: {all_balances.get('QRL', {}).get('locked', 0)}), "
                f"USDT: {usdt_balance:.2f} (locked: {all_balances.get('USDT', {}).get('locked', 0)}), "
                f"Total assets: {len(all_balances)}, "
                f"Account type: {account_info.get('accountType')}, "
                f"canTrade: {account_info.get('canTrade')}, "
                f"Maker/Taker: {account_info.get('makerCommission')}/{account_info.get('takerCommission')}, "
                f"Permissions: {account_info.get('permissions')}, "
                f"Update time: {account_info.get('updateTime')}"
            )
            
            return {
                "status": "success",
                "task": "sync-balance",
                "data": {
                    "qrl_balance": qrl_balance,
                    "usdt_balance": usdt_balance,
                    "qrl_locked": float(all_balances.get("QRL", {}).get("locked", 0)),
                    "usdt_locked": float(all_balances.get("USDT", {}).get("locked", 0)),
                    "total_assets": len(all_balances),
                    "account_type": account_info.get("accountType", "SPOT")
                },
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Balance sync failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-price")
async def task_update_price(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None)
):
    """
    Cloud Scheduler Task: Update QRL/USDT price
    Triggered by: Cloud Scheduler (every 1 minute)
    
    Stores:
    1. Raw MEXC ticker response (permanent)
    2. Latest price data (permanent)
    3. Cached price data (with TTL)
    4. Price history for charts
    
    Authentication:
    - Accepts X-CloudScheduler header (legacy)
    - Accepts Authorization header with Bearer token (OIDC)
    """
    # Verify request is from Cloud Scheduler (support both auth methods)
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] update-price authenticated via {auth_method}")
    
    try:
        async with mexc_client:
            # Get ticker from MEXC
            ticker = await mexc_client.get_ticker_24hr("QRLUSDT")
            
            # Store raw MEXC API response permanently
            await redis_client.set_mexc_raw_response(
                endpoint="ticker_24hr",
                response_data=ticker
            )
            logger.info(f"[Cloud Task] Stored raw ticker_24hr response")
            
            # Extract data from ticker
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            price_change = float(ticker.get("priceChange", 0))
            price_change_pct = float(ticker.get("priceChangePercent", 0))
            high_24h = float(ticker.get("highPrice", 0))
            low_24h = float(ticker.get("lowPrice", 0))
            quote_volume = float(ticker.get("quoteVolume", 0))
            open_price = float(ticker.get("openPrice", 0))
            weighted_avg_price = float(ticker.get("weightedAvgPrice", 0))
            prev_close_price = float(ticker.get("prevClosePrice", 0))
            bid_price = float(ticker.get("bidPrice", 0))
            ask_price = float(ticker.get("askPrice", 0))
            spread = ask_price - bid_price if (ask_price > 0 and bid_price > 0) else 0.0
            
            # Update permanent price storage (no TTL)
            await redis_client.set_latest_price(price, volume_24h)
            
            # Update cached price storage (with TTL for API queries)
            await redis_client.set_cached_price(price, volume_24h)
            
            # Add to price history
            await redis_client.add_price_to_history(price)
            
            # Store complete ticker data in Redis cache
            await redis_client.set_ticker_24hr("QRLUSDT", ticker)
            
            logger.info(
                f"[Cloud Task] Price updated - "
                f"Price: {price:.5f}, "
                f"Change: {price_change_pct:.2f}%, "
                f"Volume: {volume_24h:.2f}, "
                f"24h High/Low: {high_24h:.5f}/{low_24h:.5f}, "
                f"Bid/Ask: {bid_price:.5f}/{ask_price:.5f} (spread: {spread:.8f})"
            )
            
            return {
                "status": "success",
                "task": "update-price",
                "data": {
                    "price": price,
                    "volume_24h": volume_24h,
                    "price_change": price_change,
                    "price_change_percent": price_change_pct,
                    "high_24h": high_24h,
                    "low_24h": low_24h,
                    "quote_volume": quote_volume,
                    "open_price": open_price,
                    "weighted_avg_price": weighted_avg_price,
                    "prev_close_price": prev_close_price,
                    "bid_price": bid_price,
                    "ask_price": ask_price,
                    "spread": spread
                },
                "timestamp": datetime.now().isoformat()
            }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Price update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-cost")
async def task_update_cost(
    x_cloudscheduler: str = Header(None, alias="X-CloudScheduler"),
    authorization: str = Header(None)
):
    """
    Cloud Scheduler Task: Update cost and PnL data
    Triggered by: Cloud Scheduler (every 5 minutes)
    
    Calculates and stores:
    1. Current position value
    2. Unrealized P&L
    3. Total invested amount
    4. Realized P&L
    
    Authentication:
    - Accepts X-CloudScheduler header (legacy)
    - Accepts Authorization header with Bearer token (OIDC)
    """
    # Verify request is from Cloud Scheduler (support both auth methods)
    if not x_cloudscheduler and not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized - Cloud Scheduler only")
    
    auth_method = "OIDC" if authorization else "X-CloudScheduler"
    logger.info(f"[Cloud Task] update-cost authenticated via {auth_method}")
    
    try:
        # Get current position and cost data
        position = await redis_client.get_position()
        cost_data = await redis_client.get_cost_data()
        
        qrl_balance = float(position.get("qrl_balance", 0))
        avg_cost = float(cost_data.get("avg_cost", 0))
        
        if qrl_balance > 0 and avg_cost > 0:
            async with mexc_client:
                # Get current price
                ticker = await mexc_client.get_ticker_price("QRLUSDT")
                current_price = float(ticker.get("price", 0))
                
                # Store raw ticker response
                await redis_client.set_mexc_raw_response(
                    endpoint="ticker_price",
                    response_data=ticker
                )
            
            # Calculate metrics
            unrealized_pnl = (current_price - avg_cost) * qrl_balance
            total_invested = avg_cost * qrl_balance
            current_value = current_price * qrl_balance
            realized_pnl = float(cost_data.get("realized_pnl", 0))
            total_pnl = unrealized_pnl + realized_pnl
            roi_pct = (unrealized_pnl / total_invested * 100) if total_invested > 0 else 0
            
            # Update cost data
            await redis_client.set_cost_data(
                avg_cost=avg_cost,
                total_invested=total_invested,
                unrealized_pnl=unrealized_pnl,
                realized_pnl=realized_pnl
            )
            
            logger.info(
                f"[Cloud Task] Cost updated - "
                f"Position: {qrl_balance:.2f} QRL @ ${avg_cost:.5f}, "
                f"Current: ${current_price:.5f}, "
                f"Value: ${current_value:.2f}, "
                f"Unrealized P&L: ${unrealized_pnl:.2f} ({roi_pct:.2f}%), "
                f"Realized P&L: ${realized_pnl:.2f}, "
                f"Total P&L: ${total_pnl:.2f}"
            )
            
            return {
                "status": "success",
                "task": "update-cost",
                "data": {
                    "qrl_balance": qrl_balance,
                    "avg_cost": avg_cost,
                    "current_price": current_price,
                    "total_invested": total_invested,
                    "current_value": current_value,
                    "unrealized_pnl": unrealized_pnl,
                    "realized_pnl": realized_pnl,
                    "total_pnl": total_pnl,
                    "roi_percent": roi_pct
                },
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info("[Cloud Task] Cost update skipped - No position or cost data")
        return {
            "status": "skipped",
            "reason": "No position or cost data",
            "timestamp": datetime.now().isoformat()
        }
    
    except Exception as e:
        logger.error(f"[Cloud Task] Cost update failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
