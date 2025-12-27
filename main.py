"""
QRL Trading API - FastAPI Application (Async)
MEXC API Integration for QRL/USDT Trading Bot
"""
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

# Initialize FastAPI app
app = FastAPI(
    title="QRL Trading API",
    description="MEXC API Integration for QRL/USDT Automated Trading",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Setup templates and static files
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")
    description="MEXC API Integration for QRL/USDT Automated Trading",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


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


# ===== Startup & Shutdown Events =====

@app.on_event("startup")
async def startup_event():
    """Initialize connections on startup"""
    logger.info("Starting QRL Trading API...")
    
    # Connect to Redis
    if not await redis_client.connect():
        logger.warning("Redis connection failed - some features may not work")
    
    # Test MEXC API
    try:
        await mexc_client.ping()
        logger.info("MEXC API connection successful")
    except Exception as e:
        logger.warning(f"MEXC API connection test failed: {e}")
    
    # Initialize bot status
    if redis_client.connected:
        await redis_client.set_bot_status("initialized", {"startup_time": datetime.now().isoformat()})
    
    logger.info("QRL Trading API started successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down QRL Trading API...")
    
    if redis_client.connected:
        await redis_client.set_bot_status("stopped", {"shutdown_time": datetime.now().isoformat()})
        await redis_client.close()
    
    await mexc_client.close()
    
    logger.info("QRL Trading API shut down")


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
    latest_price = await redis_client.get_latest_price()
    daily_trades = await redis_client.get_daily_trades()
    
    return StatusResponse(
        bot_status=bot_status.get("status", "unknown"),
        position=position,
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
    """Get account balance (requires API keys)"""
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail="API keys not configured. Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables."
        )
    
    try:
        account_info = await mexc_client.get_account_info()
        
        # Extract QRL and USDT balances
        balances = {}
        for balance in account_info.get("balances", []):
            asset = balance.get("asset")
            if asset in ["QRL", "USDT"]:
                balances[asset] = {
                    "free": balance.get("free"),
                    "locked": balance.get("locked")
                }
        
        return {
            "balances": balances,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get account balance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get account balance: {str(e)}")


@app.get("/account/sub-accounts")
async def get_sub_accounts():
    """Get sub-accounts list (requires API keys)"""
    if not config.MEXC_API_KEY or not config.MEXC_SECRET_KEY:
        raise HTTPException(
            status_code=401,
            detail="API keys not configured. Set MEXC_API_KEY and MEXC_SECRET_KEY environment variables."
        )
    
    try:
        # Get sub-accounts from MEXC API
        sub_accounts = await mexc_client.get_sub_accounts()
        
        return {
            "sub_accounts": sub_accounts,
            "count": len(sub_accounts) if sub_accounts else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get sub-accounts: {e}")
        # Return empty list if not supported or error
        return {
            "sub_accounts": [],
            "count": 0,
            "timestamp": datetime.now().isoformat()
        }


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
