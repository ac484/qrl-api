"""
Status and health check API routes
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging

router = APIRouter(tags=["Status"])
logger = logging.getLogger(__name__)

# Templates for dashboard
templates = Jinja2Templates(directory="templates")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    redis_connected: bool
    mexc_api_configured: bool
    timestamp: str


class StatusResponse(BaseModel):
    """Trading status response"""
    bot_status: str
    daily_trades: int
    position: Optional[Dict[str, Any]] = None
    position_layers: Optional[Dict[str, Any]] = None
    timestamp: str


@router.get("/", response_model=Dict[str, Any])
async def root():
    """Root endpoint - API information"""
    return {
        "name": "QRL Trading API",
        "version": "1.0.0",
        "status": "running",
        "environment": "production",  # Hardcoded - only production deployment
        "endpoints": {
            "health": "/health",
            "dashboard": "/dashboard",
            "status": "/status",
            "market": "/market/*",
            "account": "/account/*",
            "bot": "/bot/*",
            "tasks": "/tasks/*"
        },
        "timestamp": datetime.now().isoformat()
    }


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render trading dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Service health status
    """
    from infrastructure.external import redis_client
    from infrastructure.config import config
    
    # Check Redis connection
    redis_connected = redis_client.connected
    
    # Check MEXC API configuration
    mexc_api_configured = bool(config.MEXC_API_KEY and config.MEXC_SECRET_KEY)
    
    # Determine overall status
    if redis_connected and mexc_api_configured:
        status = "healthy"
    elif redis_connected:
        status = "degraded"  # Redis OK but API not configured
    else:
        status = "unhealthy"  # Redis connection failed
    
    logger.info(f"Health check: {status} (Redis: {redis_connected}, MEXC: {mexc_api_configured})")
    
    return HealthResponse(
        status=status,
        redis_connected=redis_connected,
        mexc_api_configured=mexc_api_configured,
        timestamp=datetime.now().isoformat()
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get trading bot status
    
    Returns:
        Current bot status, daily trades, and position information
    """
    from infrastructure.external import redis_client
    
    try:
        # Get bot status from Redis
        bot_status = await redis_client.client.get("bot:status") or "stopped"
        
        # Get daily trades count
        daily_trades = await redis_client.get_daily_trades()
        
        # Get position data
        position = await redis_client.get_position()
        
        # Get position layers
        position_layers = await redis_client.get_position_layers()
        
        logger.info(f"Status retrieved - Bot: {bot_status}, Trades: {daily_trades}")
        
        return StatusResponse(
            bot_status=bot_status,
            daily_trades=daily_trades,
            position=position if position else None,
            position_layers=position_layers if position_layers else None,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        
        # Return partial status on error
        return StatusResponse(
            bot_status="unknown",
            daily_trades=0,
            position=None,
            position_layers=None,
            timestamp=datetime.now().isoformat()
        )
