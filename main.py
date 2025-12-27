"""
QRL Trading API - FastAPI Application (Async)
MEXC API Integration for QRL/USDT Trading Bot
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from config import config
from mexc_client import mexc_client
from redis_client import redis_client

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
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include Cloud Tasks router
from cloud_tasks import router as cloud_tasks_router
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
    
    # Import bot module to execute trading
    from bot import TradingBot
    
    bot = TradingBot(
        mexc_client=mexc_client,
        redis_client=redis_client,
        symbol=config.TRADING_SYMBOL,
        dry_run=request.dry_run
    )
    
    # Execute trading cycle
    try:
        result = await bot.execute_cycle()
        
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
        ticker = await mexc_client.get_ticker_24hr(symbol)
        return {
            "symbol": symbol,
            "data": ticker,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get ticker for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get ticker: {str(e)}")


@app.get("/market/price/{symbol}")
async def get_price(symbol: str):
    """Get current price for a symbol"""
    try:
        price_data = await mexc_client.get_ticker_price(symbol)
        
        # Cache in Redis if connected
        if redis_client.connected and symbol == config.TRADING_SYMBOL:
            price = float(price_data.get("price", 0))
            await redis_client.set_latest_price(price)
            await redis_client.add_price_to_history(price)
        
        return {
            "symbol": symbol,
            "price": price_data.get("price"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get price: {str(e)}")


@app.get("/account/balance")
async def get_account_balance():
    """
    Get account balance (requires API keys)
    
    This endpoint fetches real-time balance from MEXC API.
    Requires valid MEXC_API_KEY and MEXC_SECRET_KEY with spot trading permissions.
    
    Returns:
        dict: Account balances for QRL and USDT with free/locked amounts
        
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
        account_info = await mexc_client.get_account_info()
        
        # Extract QRL and USDT balances
        balances = {}
        all_assets = []
        
        for balance in account_info.get("balances", []):
            asset = balance.get("asset")
            all_assets.append(asset)
            
            if asset in ["QRL", "USDT"]:
                balances[asset] = {
                    "free": balance.get("free", "0"),
                    "locked": balance.get("locked", "0")
                }
        
        # Log available assets for debugging
        logger.info(f"Account has {len(all_assets)} assets, QRL/USDT found: {list(balances.keys())}")
        
        # Ensure QRL and USDT are always in response (even if zero)
        if "QRL" not in balances:
            balances["QRL"] = {"free": "0", "locked": "0"}
        if "USDT" not in balances:
            balances["USDT"] = {"free": "0", "locked": "0"}
        
        return {
            "success": True,
            "balances": balances,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get account balance: {e}", exc_info=True)
        
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


@app.get("/account/sub-accounts")
async def get_sub_accounts():
    """
    Get sub-accounts list (requires API keys with broker permissions)
    
    This endpoint fetches sub-account list from MEXC broker API.
    Note: Regular spot trading accounts may not have access to this endpoint.
    Broker account permissions are required.
    
    Returns:
        dict: List of sub-accounts with their details
        
    Raises:
        HTTPException: 401 if API keys not configured, 403 if insufficient permissions
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
        logger.info("Fetching sub-accounts from MEXC broker API")
        # Get sub-accounts from MEXC API
        sub_accounts = await mexc_client.get_sub_accounts()
        
        logger.info(f"Successfully retrieved {len(sub_accounts)} sub-accounts")
        
        return {
            "success": True,
            "sub_accounts": sub_accounts,
            "count": len(sub_accounts) if sub_accounts else 0,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.warning(f"Failed to get sub-accounts: {e}")
        
        # Check if it's a permission error
        error_msg = str(e).lower()
        if "403" in error_msg or "permission" in error_msg or "forbidden" in error_msg:
            return {
                "success": False,
                "sub_accounts": [],
                "count": 0,
                "message": "Sub-account access requires broker permissions",
                "help": "This feature is only available for MEXC broker accounts",
                "timestamp": datetime.now().isoformat()
            }
        
        # Return empty list for other errors (maintain API compatibility)
        return {
            "success": False,
            "sub_accounts": [],
            "count": 0,
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.get("/account/sub-account/balance")
async def get_sub_account_balance(
    email: Optional[str] = None,
    sub_account_id: Optional[str] = None
):
    """
    Get specific sub-account balance (requires API keys with broker permissions)
    
    Query parameters:
        email: Sub-account email address (optional)
        sub_account_id: Sub-account ID (optional)
        
    Note: At least one of email or sub_account_id must be provided.
    Different sub-accounts may use email or ID as identifier.
    
    Returns:
        dict: Sub-account balance details
        
    Raises:
        HTTPException: 400 if no identifier provided, 401 if API keys missing
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
    
    # Validate at least one identifier is provided
    if not email and not sub_account_id:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing identifier",
                "message": "Either email or sub_account_id must be provided",
                "help": "Add ?email=xxx@example.com or ?sub_account_id=123456 to the request"
            }
        )
    
    try:
        identifier = email or sub_account_id
        logger.info(f"Fetching balance for sub-account: {identifier}")
        
        # Get sub-account balance from MEXC API
        balance_data = await mexc_client.get_sub_account_balance(
            email=email,
            sub_account_id=sub_account_id
        )
        
        logger.info(f"Successfully retrieved balance for sub-account: {identifier}")
        
        return {
            "success": True,
            "sub_account": {
                "email": email,
                "id": sub_account_id
            },
            "balance": balance_data,
            "timestamp": datetime.now().isoformat()
        }
        
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
                    "message": "Sub-account access requires broker permissions",
                    "help": "This feature is only available for MEXC broker accounts"
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
