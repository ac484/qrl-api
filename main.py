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
from fastapi.staticfiles import StaticFiles

from src.app.infrastructure.config import config
from src.app.infrastructure.external import mexc_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    if config.LOG_FORMAT == "text"
    else '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}',
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


# ===== Lifespan Context Manager =====


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info(
        "Starting QRL Trading API (Cloud Run mode - Direct MEXC API, No Redis)..."
    )
    logger.info(f"Listening on port: {config.PORT}")
    logger.info(f"Host: {config.HOST}")

    # CRITICAL: Minimal startup - don't block on external API checks
    # Cloud Run requires fast startup to listen on PORT within timeout
    logger.info(
        "QRL Trading API started successfully (Cloud Run - Direct API mode, No Redis)"
    )
    logger.info(f"Server is ready to accept requests on port {config.PORT}")

    # Test MEXC API in background (non-blocking, fire-and-forget)
    import asyncio

    async def test_mexc_api():
        try:
            logger.info("Testing MEXC API connection...")
            await asyncio.wait_for(mexc_client.ping(), timeout=3.0)
            logger.info("MEXC API connection successful")
        except asyncio.TimeoutError:
            logger.warning("MEXC API connection timeout - continuing anyway")
        except Exception as e:
            logger.warning(f"MEXC API connection test failed: {e} - continuing anyway")

    # Schedule background task without awaiting
    asyncio.create_task(test_mexc_api())

    yield

    # Shutdown
    logger.info("Shutting down QRL Trading API...")

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
    lifespan=lifespan,
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static assets for the dashboard (src/app/interfaces/templates/static -> /static)
try:
    app.mount(
        "/static",
        StaticFiles(directory="src/app/interfaces/templates/static"),
        name="static",
    )
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.warning(
        f"Failed to mount static files: {e} - continuing without static files"
    )


# ===== Include Routers =====

# Phase 1: Centralized Router Registration
# Using new router_registry module for cleaner router management
from src.app.interfaces import register_all_routers  # noqa: E402

# Register all routers via centralized registry
register_all_routers(app)


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
            "timestamp": datetime.now().isoformat(),
        },
    )


# ===== Entry Point =====

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
        log_level=config.LOG_LEVEL.lower(),
    )
