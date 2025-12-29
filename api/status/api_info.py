"""API info route."""
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter

router = APIRouter(tags=["Status"])


@router.get("/api/info", response_model=Dict[str, Any])
async def api_info():
    return {
        "name": "QRL Trading API",
        "version": "1.0.0",
        "status": "running",
        "environment": "production",
        "endpoints": {
            "health": "/health",
            "dashboard": "/dashboard",
            "status": "/status",
            "market": "/market/*",
            "account": "/account/*",
            "bot": "/bot/*",
            "tasks": "/tasks/*",
        },
        "timestamp": datetime.now().isoformat(),
    }
