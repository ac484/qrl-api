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


@router.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint - Trading Dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Render trading dashboard (alias for root)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/api/info", response_model=Dict[str, Any])
async def api_info():
    """API information endpoint"""
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


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint
    
    Returns:
        Service health status
    """
    from infrastructure.config import config
    
    # Check MEXC API configuration
    mexc_api_configured = bool(config.MEXC_API_KEY and config.MEXC_SECRET_KEY)
    
    # Determine overall status
    if mexc_api_configured:
        status = "healthy"
    else:
        status = "degraded"  # API not configured
    
    logger.info(f"Health check: {status} (MEXC: {mexc_api_configured})")
    
    return HealthResponse(
        status=status,
        redis_connected=False,  # No longer using Redis
        mexc_api_configured=mexc_api_configured,
        timestamp=datetime.now().isoformat()
    )


@router.get("/status", response_model=StatusResponse)
async def get_status():
    """
    Get trading bot status
    
    Returns:
        Current bot status (simplified without Redis)
    """
    logger.info("Status retrieved - Direct API mode (no Redis)")
    
    return StatusResponse(
        bot_status="running",  # Simplified: always running when API is up
        daily_trades=0,  # Not tracked without Redis
        position=None,  # Would need to fetch from MEXC if needed
        position_layers=None,  # Not available without Redis
        timestamp=datetime.now().isoformat()
    )
