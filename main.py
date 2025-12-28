"""
QRL Trading API - FastAPI Application (Async)
MEXC API Integration for QRL/USDT Trading Bot

This is the refactored main application file following clean architecture principles.
All route handlers have been extracted to separate modules in the api/ directory.
"""
import logging
import sys
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.config.config import config
from infrastructure.external.mexc_client import mexc_client
from infrastructure.external.redis_client import redis_client

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
    logger.info(f"Listening on port: {config.PORT}")
    logger.info(f"Host: {config.HOST}")
    
    # Connect to Redis with timeout
    redis_connected = False
    try:
        logger.info("Connecting to Redis...")
        # Add timeout to prevent blocking startup
        import asyncio
        redis_connected = await asyncio.wait_for(
            redis_client.connect(), 
            timeout=10.0  # 10 second timeout
        )
        if redis_connected:
            logger.info("Redis connection successful")
        else:
            logger.warning("Redis connection failed - some features may not work")
    except asyncio.TimeoutError:
        logger.warning("Redis connection timeout - continuing without Redis")
    except Exception as e:
        logger.warning(f"Redis connection error: {e} - continuing without Redis")
    
    # Test MEXC API (non-blocking)
    try:
        logger.info("Testing MEXC API connection...")
        import asyncio
        await asyncio.wait_for(mexc_client.ping(), timeout=5.0)
        logger.info("MEXC API connection successful")
    except asyncio.TimeoutError:
        logger.warning("MEXC API connection timeout - continuing anyway")
    except Exception as e:
        logger.warning(f"MEXC API connection test failed: {e} - continuing anyway")
    
    # Initialize bot status (if Redis is available)
    if redis_connected and redis_client.connected:
        try:
            await redis_client.set_bot_status("initialized", 
                {"startup_time": datetime.now().isoformat()})
        except Exception as e:
            logger.warning(f"Failed to set initial bot status: {e}")
    
    logger.info("QRL Trading API started successfully (Cloud Run - serverless mode)")
    logger.info(f"Server is ready to accept requests on port {config.PORT}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down QRL Trading API...")
    
    if redis_client.connected:
        try:
            await redis_client.set_bot_status("stopped", 
                {"shutdown_time": datetime.now().isoformat()})
        except Exception as e:
            logger.warning(f"Failed to set shutdown status: {e}")
        
        try:
            await redis_client.close()
        except Exception as e:
            logger.warning(f"Error closing Redis connection: {e}")
    
    try:
        await mexc_client.close()
    except Exception as e:
        logger.warning(f"Error closing MEXC client: {e}")
    
    logger.info("QRL Trading API shut down")


# ===== Initialize FastAPI App =====

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


# ===== Include Routers =====

# Import all route modules
from api.status_routes import router as status_router
from api.market_routes import router as market_router
from api.account_routes import router as account_router
from api.bot_routes import router as bot_router
from api.sub_account_routes import router as sub_account_router
from infrastructure.cloud_tasks import router as cloud_tasks_router

# Register all routers
app.include_router(status_router)          # /, /dashboard, /health, /status
app.include_router(market_router)          # /market/*
app.include_router(account_router)         # /account/balance, /account/balance/redis
app.include_router(bot_router)             # /bot/control, /bot/execute
app.include_router(sub_account_router)     # /account/sub-account/*
app.include_router(cloud_tasks_router)     # /tasks/*

logger.info("All routers registered successfully")


# ===== Global Exception Handler =====

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    from fastapi.responses import JSONResponse
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
