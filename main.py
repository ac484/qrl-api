"""
QRL Trading API - FastAPI Application (Async)
MEXC API Integration for QRL/USDT Trading Bot
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from infrastructure.config.config import config
from infrastructure.external.mexc_client.client import mexc_client
from infrastructure.external.redis_client.client import redis_client
from repositories.market.price_repository import PriceRepository
from repositories.trade.trade_repository import TradeRepository
from services.market.market_service import MarketService
from services.trading.trading_service import TradingService

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s' if config.LOG_FORMAT == "text" 
           else '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout
)

logger = logging.getLogger(__name__)


# ===== Lifespan Context Manager =====

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting QRL Trading API (Cloud Run mode)...")
    
    # Connect to Redis
    if not await redis_client.connect():
        logger.warning("Redis connection failed - some features may not work")
    else:
        logger.info("Redis connection successful")
    
    # Test MEXC API
    try:
        await mexc_client.ping()
        logger.info("MEXC API connection successful")
    except Exception as e:
        logger.warning(f"MEXC API connection test failed: {e}")
    
    # Initialize bot status
    if redis_client.connected:
        await redis_client.set_bot_status("initialized", 
            {"startup_time": datetime.now().isoformat()})
    
    logger.info("QRL Trading API started successfully (Cloud Run - serverless mode)")
    
    yield
    
    # Shutdown
    logger.info("Shutting down QRL Trading API...")
    
    if redis_client.connected:
        await redis_client.set_bot_status("stopped", 
            {"shutdown_time": datetime.now().isoformat()})
        await redis_client.close()
    
    await mexc_client.close()
    
    logger.info("QRL Trading API shut down")


# Initialize FastAPI app
app = FastAPI(
    title="QRL Trading API",
    description="MEXC API Integration for QRL/USDT Automated Trading (Cloud Run)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")

# Structured layer singletons
price_repository = PriceRepository(redis_client)
trade_repository = TradeRepository(redis_client)
market_service = MarketService(price_repository, mexc_client)
trading_service = TradingService(
    mexc_client=mexc_client,
    redis_client=redis_client,
    trade_repository=trade_repository,
    price_repository=price_repository,
)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Cloud Tasks router
from infrastructure.tasks.mexc_tasks import router as cloud_tasks_router
app.include_router(cloud_tasks_router)


# ===== Pydantic Models =====

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    redis_connected: bool
    mexc_api_available: bool
    timestamp: str


class StatusResponse(BaseModel):
    """Bot status response"""
    bot_status: str
    position: Dict[str, Any]
    position_layers: Optional[Dict[str, Any]] = None  # Position layers (core/swing/active)
    latest_price: Optional[Dict[str, Any]]
    daily_trades: int
    timestamp: str


class ControlRequest(BaseModel):
    """Bot control request"""
    action: str = Field(..., description="Action: start, pause, stop")
    reason: Optional[str] = Field(None, description="Reason for action")


class ExecuteRequest(BaseModel):
    """Trading execution request"""
    pair: str = Field(default="QRL/USDT", description="Trading pair")
    strategy: str = Field(default="ma-crossover", description="Trading strategy")
    dry_run: bool = Field(default=False, description="Dry run mode (no actual trades)")


class ExecuteResponse(BaseModel):
    """Trading execution response"""
    success: bool
    action: Optional[str]
    message: str
    details: Dict[str, Any]
    timestamp: str


# ===== API Endpoints =====

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Dashboard page - visualize balances and QRL/USDT"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint - service information"""
    return {
        "service": "QRL Trading API",
        "version": "1.0.0",
        "description": "MEXC API Integration for QRL/USDT Trading (Async)",
        "framework": "FastAPI + Uvicorn + httpx + redis.asyncio",
        "endpoints": {
            "dashboard": "/dashboard",
            "health": "/health",
            "status": "/status",
            "execute": "/execute (POST)",
            "control": "/control (POST)",
            "docs": "/docs",
            "redoc": "/redoc"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    redis_ok = await redis_client.health_check() if redis_client.connected else False
    
    # Test MEXC API
    mexc_ok = False
    try:
        await mexc_client.ping()
        mexc_ok = True
    except Exception as e:
        logger.warning(f"MEXC API health check failed: {e}")
    
    status = "healthy" if (redis_ok and mexc_ok) else "degraded"
    
    return HealthResponse(
        status=status,
        redis_connected=redis_ok,
        mexc_api_available=mexc_ok,
        timestamp=datetime.now().isoformat()
    )


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get bot status and current state"""
    if not redis_client.connected:
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    bot_status = await redis_client.get_bot_status()
    position = await redis_client.get_position()
    cost_data = await redis_client.get_cost_data()
    position_layers = await redis_client.get_position_layers()
    latest_price = await redis_client.get_latest_price()
    daily_trades = await redis_client.get_daily_trades()
    
    # Merge position and cost data
    merged_position = dict(position)
    if cost_data:
        merged_position.update(cost_data)
    
    return StatusResponse(
        bot_status=bot_status.get("status", "unknown"),
        position=merged_position,
        position_layers=position_layers if position_layers else None,
        latest_price=latest_price,
        daily_trades=daily_trades,
        timestamp=datetime.now().isoformat()
    )


@app.post("/control", response_model=Dict[str, Any])
async def control_bot(request: ControlRequest):
    """Control bot operation (start/pause/stop)"""
    if not redis_client.connected:
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    valid_actions = ["start", "pause", "stop"]
    if request.action not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action. Must be one of: {', '.join(valid_actions)}"
        )
    
    # Map actions to statuses
    status_map = {
        "start": "running",
        "pause": "paused",
        "stop": "stopped"
    }
    
    metadata = {
        "action": request.action,
        "reason": request.reason,
        "controlled_at": datetime.now().isoformat()
    }
    
    success = await redis_client.set_bot_status(status_map[request.action], metadata)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to update bot status")
    
    return {
        "success": True,
        "action": request.action,
        "new_status": status_map[request.action],
        "message": f"Bot {request.action} successful",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/execute", response_model=ExecuteResponse)
async def execute_trading(request: ExecuteRequest, background_tasks: BackgroundTasks):
    """Execute trading strategy"""
    if not redis_client.connected:
        raise HTTPException(status_code=503, detail="Redis not connected")
    
    # Check bot status
    bot_status = await redis_client.get_bot_status()
    if bot_status.get("status") == "stopped":
        return ExecuteResponse(
            success=False,
            action=None,
            message="Bot is stopped. Use /control to start it.",
            details={"bot_status": bot_status},
            timestamp=datetime.now().isoformat()
        )
    
    if bot_status.get("status") == "paused":
        return ExecuteResponse(
            success=False,
            action=None,
            message="Bot is paused. Use /control to resume it.",
            details={"bot_status": bot_status},
            timestamp=datetime.now().isoformat()
        )
    
    # Execute trading cycle via service layer
    try:
        result = await trading_service.execute(dry_run=request.dry_run)

        return ExecuteResponse(
            success=result.get("success", False),
            action=result.get("action"),
            message=result.get("message", "Trading cycle completed"),
            details=result,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Trading execution failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Trading execution failed: {str(e)}")


@app.get("/market/ticker/{symbol}")
async def get_ticker(symbol: str):
    """Get market ticker for a symbol"""
    try:
        return await market_service.get_ticker(symbol)
    except Exception as e:
        logger.error(f"Failed to get ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticker: {str(e)}")


@app.get("/market/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for a symbol"""
    try:
        return await market_service.get_price(symbol)
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price: {str(e)}")


@app.get("/market/orderbook/{symbol}")
async def get_orderbook(symbol: str, limit: int = 100):
    """
    Get order book depth for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        limit: Depth limit (default 100, max 5000)
    """
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_orderbook = await redis_client.get_order_book(symbol)
            if cached_orderbook:
                logger.debug(f"Retrieved order book from cache for {symbol}")
                return {
                    "symbol": symbol,
                    "data": cached_orderbook,
                    "timestamp": cached_orderbook.get("cached_at"),
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        orderbook = await mexc_client.get_order_book(symbol, limit)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_order_book(symbol, orderbook)
        
        return {
            "symbol": symbol,
            "data": orderbook,
            "timestamp": datetime.now().isoformat(),
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get order book for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get order book: {str(e)}")


@app.get("/market/trades/{symbol}")
async def get_recent_trades_endpoint(symbol: str, limit: int = 500):
    """
    Get recent trades for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        limit: Number of trades (default 500, max 1000)
    """
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_trades = await redis_client.get_recent_trades(symbol)
            if cached_trades:
                logger.debug(f"Retrieved recent trades from cache for {symbol}")
                return {
                    "symbol": symbol,
                    "trades": cached_trades,
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        trades = await mexc_client.get_recent_trades(symbol, limit)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_recent_trades(symbol, trades)
        
        return {
            "symbol": symbol,
            "trades": trades,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get recent trades for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent trades: {str(e)}")


@app.get("/market/klines/{symbol}")
async def get_klines_endpoint(symbol: str, interval: str = "1m", limit: int = 500):
    """
    Get klines/candlestick data for a symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT")
        interval: Kline interval (e.g., "1m", "5m", "15m", "1h", "1d")
        limit: Number of klines (default 500, max 1000)
    """
    try:
        # Try to get from cache first
        if redis_client.connected:
            cached_klines = await redis_client.get_klines(symbol, interval)
            if cached_klines:
                logger.debug(f"Retrieved klines from cache for {symbol} ({interval})")
                return {
                    "symbol": symbol,
                    "interval": interval,
                    "klines": cached_klines,
                    "cached": True
                }
        
        # Fetch from MEXC API if not cached
        klines = await mexc_client.get_klines(symbol, interval, limit)
        
        # Cache the result
        if redis_client.connected:
            await redis_client.set_klines(symbol, interval, klines)
        
        return {
            "symbol": symbol,
            "interval": interval,
            "klines": klines,
            "cached": False
        }
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get klines: {str(e)}")


@app.get("/account/balance")
async def get_account_balance():
    """
    Get account balance (requires API keys)
    
    This endpoint fetches real-time balance from MEXC API and stores ALL data in Redis permanently.
    Requires valid MEXC_API_KEY and MEXC_SECRET_KEY with spot trading permissions.
    
    Stores in Redis:
    - mexc:raw_response:account_info - Complete API response
    - mexc:account_balance - Processed balance data
    - mexc:qrl_price - QRL price data
    - mexc:total_value - Total account value in USDT
    
    Returns:
        dict: Account balances for QRL and USDT with free/locked amounts, QRL price, and total value
        
    Raises:
        HTTPException: 401 if API keys not configured, 500 if API call fails
    """
    # Validate API keys are configured
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        logger.error("API keys not configured - cannot fetch account balance")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                "help": "Check Cloud Run environment variables or .env file"
            }
        )
    
    try:
        logger.info("Fetching account balance from MEXC API")
        
        # Step 1: Fetch account info from MEXC
        logger.info("Step 1: Fetching account info from MEXC API...")
        account_info = await mexc_client.get_account_info()
        logger.info(f"Received account info with {len(account_info.get('balances', []))} assets")
        
        # Step 2: Store raw response in Redis (PERMANENT - no expiration)
        logger.info("Step 2: Storing raw MEXC API response in Redis...")
        await redis_client.set_mexc_raw_response("account_info", account_info)
        logger.info("✓ Raw response stored in Redis: mexc:raw_response:account_info")
        
        # Step 3: Extract QRL and USDT balances
        logger.info("Step 3: Processing balance data...")
        balances = {}
        all_assets = []
        
        for balance in account_info.get("balances", []):
            asset = balance.get("asset")
            all_assets.append(asset)
            
            if asset in ["QRL", "USDT"]:
                balances[asset] = {
                    "free": balance.get("free", "0"),
                    "locked": balance.get("locked", "0"),
                    "total": str(float(balance.get("free", "0")) + float(balance.get("locked", "0")))
                }
                logger.info(f"  {asset}: free={balances[asset]['free']}, locked={balances[asset]['locked']}, total={balances[asset]['total']}")
        
        # Ensure QRL and USDT are always in response (even if zero)
        if "QRL" not in balances:
            balances["QRL"] = {"free": "0", "locked": "0", "total": "0"}
            logger.info("  QRL: Not found in account, using zero balance")
        if "USDT" not in balances:
            balances["USDT"] = {"free": "0", "locked": "0", "total": "0"}
            logger.info("  USDT: Not found in account, using zero balance")
        
        logger.info(f"Account has {len(all_assets)} total assets")
        
        # Step 4: Fetch QRL price
        logger.info("Step 4: Fetching QRL price from MEXC API...")
        try:
            price_data = await mexc_client.get_ticker_price(config.TRADING_SYMBOL)
            qrl_price = float(price_data.get("price", "0"))
            logger.info(f"✓ QRL Price: {qrl_price} USDT")
            
            # Store QRL price in Redis (PERMANENT)
            await redis_client.set_mexc_qrl_price(qrl_price, price_data)
            logger.info("✓ QRL price stored in Redis: mexc:qrl_price")
        except Exception as price_error:
            logger.warning(f"Failed to fetch QRL price: {price_error}")
            qrl_price = 0
            price_data = {}
        
        # Step 5: Calculate total value in USDT
        logger.info("Step 5: Calculating total account value in USDT...")
        qrl_total = float(balances["QRL"]["total"])
        usdt_total = float(balances["USDT"]["total"])
        
        qrl_value_usdt = qrl_total * qrl_price
        total_value_usdt = qrl_value_usdt + usdt_total
        
        value_breakdown = {
            "qrl_quantity": qrl_total,
            "qrl_price_usdt": qrl_price,
            "qrl_value_usdt": qrl_value_usdt,
            "usdt_balance": usdt_total,
            "total_value_usdt": total_value_usdt
        }
        
        logger.info(f"  QRL Quantity: {qrl_total}")
        logger.info(f"  QRL Price: {qrl_price} USDT")
        logger.info(f"  QRL Value: {qrl_value_usdt} USDT")
        logger.info(f"  USDT Balance: {usdt_total} USDT")
        logger.info(f"  TOTAL VALUE: {total_value_usdt} USDT")
        
        # Store total value in Redis (PERMANENT)
        await redis_client.set_mexc_total_value(total_value_usdt, value_breakdown)
        logger.info("✓ Total value stored in Redis: mexc:total_value")
        
        # Step 6: Store processed balance data in Redis (PERMANENT)
        logger.info("Step 6: Storing processed balance data in Redis...")
        balance_data = {
            "QRL": balances["QRL"],
            "USDT": balances["USDT"],
            "all_assets_count": len(all_assets)
        }
        await redis_client.set_mexc_account_balance(balance_data)
        logger.info("✓ Balance data stored in Redis: mexc:account_balance")
        
        logger.info("All MEXC data successfully stored in Redis (permanent storage)")
        logger.info("Redis keys: mexc:raw_response:account_info, mexc:account_balance, mexc:qrl_price, mexc:total_value")
        
        # Return comprehensive response
        return {
            "success": True,
            "balances": balances,
            "qrl_price": qrl_price,
            "total_value": {
                "usdt": total_value_usdt,
                "breakdown": value_breakdown
            },
            "timestamp": datetime.now().isoformat(),
            "redis_storage": {
                "raw_response": "mexc:raw_response:account_info",
                "account_balance": "mexc:account_balance",
                "qrl_price": "mexc:qrl_price",
                "total_value": "mexc:total_value"
            }
        }
        
        # Cache the complete result
        if redis_client.connected:
            await redis_client.set_account_balance(result)
            logger.info(
                f"Stored complete account balance - "
                f"Type: {result['accountType']}, "
                f"canTrade: {result['canTrade']}, "
                f"Maker/Taker: {result['makerCommission']}/{result['takerCommission']}, "
                f"Permissions: {result['permissions']}"
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching account balance: {e}", exc_info=True)
        
        # Check if it's an authentication error
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg or "invalid" in error_msg:
            raise HTTPException(
                status_code=401,
                detail={
                    "error": "Authentication failed",
                    "message": "API keys may be invalid or lack spot trading permissions",
                    "help": "Verify your MEXC API keys and ensure they have SPOT trading enabled",
                    "technical_details": str(e)
                }
            )
        
        # Generic error response
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to fetch account balance",
                "message": str(e),
                "help": "Check MEXC API status and your API key permissions"
            }
        )


@app.get("/account/balance/redis")
async def get_account_balance_from_redis():
    """
    Get stored account balance data from Redis
    
    This endpoint retrieves all MEXC API data that has been stored in Redis.
    Useful for debugging and verifying data persistence.
    
    Returns:
        dict: All stored MEXC data from Redis including:
            - raw_response: Complete MEXC API response
            - account_balance: Processed balance data
            - qrl_price: QRL price data
            - total_value: Total account value calculation
    """
    try:
        logger.info("Fetching MEXC data from Redis...")
        
        # Retrieve all stored data
        raw_response = await redis_client.get_mexc_raw_response("account_info")
        account_balance = await redis_client.get_mexc_account_balance()
        qrl_price = await redis_client.get_mexc_qrl_price()
        total_value = await redis_client.get_mexc_total_value()
        
        # Check what data is available
        available_data = {
            "raw_response": raw_response is not None,
            "account_balance": account_balance is not None,
            "qrl_price": qrl_price is not None,
            "total_value": total_value is not None
        }
        
        logger.info(f"Redis data availability: {available_data}")
        
        return {
            "success": True,
            "data_available": available_data,
            "raw_response": raw_response,
            "account_balance": account_balance,
            "qrl_price": qrl_price,
            "total_value": total_value,
            "retrieved_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get data from Redis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to retrieve data from Redis",
                "message": str(e)
            }
        )


@app.get("/account/sub-accounts")
async def get_sub_accounts_endpoint():
    """
    Get sub-accounts list (auto-detects API mode)
    
    Automatically uses:
    - Spot API for regular users (returns subAccountId)
    - Broker API for broker accounts (returns subAccount name)
    
    Mode is determined by SUB_ACCOUNT_MODE and IS_BROKER_ACCOUNT config.
    
    Returns:
        dict: List of sub-accounts with mode information
        {
            "success": true,
            "mode": "SPOT" or "BROKER",
            "sub_accounts": [...],
            "count": 0,
            "timestamp": "..."
        }
        
    Raises:
        HTTPException: 401 if API keys not configured
    """
    # Validate API keys are configured
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        logger.error("API keys not configured - cannot fetch sub-accounts")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                "help": "Check Cloud Run environment variables or .env file"
            }
        )
    
    try:
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        logger.info(f"Fetching sub-accounts using {mode} API")
        
        # Get sub-accounts from MEXC API (auto-selects API based on config)
        sub_accounts = await mexc_client.get_sub_accounts()
        
        logger.info(f"Successfully retrieved {len(sub_accounts)} sub-accounts using {mode} API")
        
        return {
            "success": True,
            "mode": mode,
            "sub_accounts": sub_accounts,
            "count": len(sub_accounts) if sub_accounts else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.warning(f"Failed to get sub-accounts: {e}")
        
        # Determine mode for error response
        mode = "BROKER" if config.is_broker_mode else "SPOT"
        
        # Check if it's a permission error
        error_msg = str(e).lower()
        if "403" in error_msg or "permission" in error_msg or "forbidden" in error_msg:
            return {
                "success": False,
                "mode": mode,
                "sub_accounts": [],
                "count": 0,
                "message": f"Sub-account access requires {mode} API permissions",
                "help": f"Ensure your MEXC account has {mode} API access enabled",
                "timestamp": datetime.now().isoformat()
            }
        
        # Return empty list for other errors (maintain API compatibility)
        return {
            "success": False,
            "mode": mode,
            "sub_accounts": [],
            "count": 0,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/account/sub-account/balance")
async def get_sub_account_balance_endpoint(
    identifier: Optional[str] = None,
    # Legacy parameters for backward compatibility
    email: Optional[str] = None,
    sub_account_id: Optional[str] = None
):
    """
    Get specific sub-account balance
    
    Query parameters:
        identifier: Sub-account identifier (subAccountId for SPOT, subAccount name for BROKER)
        email: (DEPRECATED) Legacy parameter, use identifier instead
        sub_account_id: (DEPRECATED) Legacy parameter, use identifier instead
        
    Note:
        - SPOT API: Does NOT support querying sub-account balance from main account.
                    You must use the sub-account's own API key.
        - BROKER API: Can query sub-account balance using sub-account name.
    
    Returns:
        dict: Sub-account balance details (BROKER API only)
        
    Raises:
        HTTPException: 400 if no identifier, 401 if API keys missing, 501 for SPOT API
    """
    # Validate API keys are configured
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        logger.error("API keys not configured - cannot fetch sub-account balance")
        raise HTTPException(
            status_code=401,
            detail={
                "error": "API keys not configured",
                "message": "Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables",
                "help": "Check Cloud Run environment variables or .env file"
            }
        )
    
    # Get identifier from new or legacy parameters
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


@app.post("/account/sub-account/transfer")
async def transfer_between_sub_accounts_endpoint(
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
        
    Raises:
        HTTPException: 400/401/500 on errors
    """
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


@app.post("/account/sub-account/api-key")
async def create_sub_account_api_key_endpoint(
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
        
    Raises:
        HTTPException: 400/401/500 on errors
    """
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


@app.delete("/account/sub-account/api-key")
async def delete_sub_account_api_key_endpoint(
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
        
    Raises:
        HTTPException: 400/401/501/500 on errors
    """
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


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


# ===== Entry Point =====

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower()
    )
