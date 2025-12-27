"""
Main application entry point for QRL Trading Bot
FastAPI web server with WebSocket support for Cloud Run deployment
"""
import logging
import sys
import time
import asyncio
from datetime import datetime
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pythonjsonlogger import jsonlogger

from config import config
from redis_client import redis_client
from bot import trading_bot
from mexc_client import mexc_client

# Configure logging
def setup_logging():
    """Configure JSON logging for Cloud Run"""
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    log_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(logging.INFO if not config.DEBUG else logging.DEBUG)
    
    return root_logger

logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="QRL Trading Bot API",
    description="Automated QRL/USDT trading bot with real-time WebSocket updates",
    version="2.0.0"
)

# Mount static files (create directory if it doesn't exist)
import os
if not os.path.exists("static"):
    os.makedirs("static", exist_ok=True)
    
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Setup templates
templates = Jinja2Templates(directory="templates")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")

manager = ConnectionManager()

# Initialize services with error handling
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    try:
        redis_client.get_bot_status()
        logger.info("Redis connection successful")
    except Exception as e:
        logger.warning(f"Redis connection failed (will continue with limited functionality): {e}")

    try:
        mexc_client.health_check()
        logger.info("MEXC client initialized successfully")
    except Exception as e:
        logger.warning(f"MEXC client initialization failed (will use fallback data): {e}")
    
    logger.info(f"QRL Trading Bot started")
    logger.info(f"Trading pair: {config.TRADING_PAIR}")
    logger.info(f"Redis: {config.REDIS_URL}")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Root endpoint - serves the main dashboard
    """
    return await dashboard(request)


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """
    Web dashboard - shows balance, positions, and trading stats
    Real-time updates via WebSocket
    """
    try:
        # Get all data with fallbacks
        try:
            bot_status = redis_client.get_bot_status() or 'unknown'
            latest_price = redis_client.get_latest_price() or 0
            daily_trades = redis_client.get_daily_trades()
        except Exception as e:
            logger.warning(f"Dashboard: Redis connection failed, using defaults: {e}")
            bot_status = 'unknown'
            latest_price = 0
            daily_trades = 0
        
        # Get position data
        try:
            position = redis_client.get_position() or {}
            qrl_balance = position.get('size', 0)
        except Exception as e:
            logger.warning(f"Dashboard: Cannot get position from Redis: {e}")
            position = {}
            qrl_balance = 0
        
        # Get position layers
        try:
            layers_data = redis_client.get_position_layers()
        except Exception as e:
            logger.warning(f"Dashboard: Cannot get position layers from Redis: {e}")
            layers_data = None
        
        # Calculate position distribution
        total_qrl = qrl_balance
        if layers_data:
            core_qrl = layers_data.get('core', 0)
            swing_qrl = layers_data.get('swing', 0)
            active_qrl = layers_data.get('active', 0)
            total_qrl = core_qrl + swing_qrl + active_qrl
        else:
            core_qrl = total_qrl * 0.7
            swing_qrl = total_qrl * 0.2
            active_qrl = total_qrl * 0.1
        
        core_percent = (core_qrl / total_qrl * 100) if total_qrl > 0 else 70
        swing_percent = (swing_qrl / total_qrl * 100) if total_qrl > 0 else 20
        active_percent = (active_qrl / total_qrl * 100) if total_qrl > 0 else 10
        
        # Get cost tracking
        try:
            cost_data = redis_client.get_cost_tracking()
        except Exception as e:
            logger.warning(f"Dashboard: Cannot get cost tracking from Redis: {e}")
            cost_data = None
            
        if cost_data:
            avg_cost = float(cost_data.get('avg_cost', 0))
            realized_pnl = float(cost_data.get('realized_pnl', 0))
            unrealized_pnl = float(cost_data.get('unrealized_pnl', 0))
        else:
            avg_cost = 0
            realized_pnl = 0
            unrealized_pnl = 0
        
        # Calculate P&L percentage
        pnl_percent = None
        if avg_cost > 0 and latest_price > 0:
            pnl_percent = ((latest_price / avg_cost) - 1) * 100
        
        # Get real balance from MEXC API
        usdt_balance = 0
        try:
            mexc_balance = mexc_client.get_account_balance()
            if mexc_balance and mexc_balance.get('QRL', 0) > 0:
                qrl_balance_from_api = mexc_balance.get('QRL', 0)
                usdt_balance = mexc_balance.get('USDT', 0)
                
                # Update total_qrl with real data from API
                total_qrl = qrl_balance_from_api
                # Recalculate position layers based on actual balance
                if not layers_data:
                    core_qrl = total_qrl * 0.7
                    swing_qrl = total_qrl * 0.2
                    active_qrl = total_qrl * 0.1
                    core_percent = 70
                    swing_percent = 20
                    active_percent = 10
                logger.info(f"Dashboard: Using real MEXC balance - QRL: {qrl_balance_from_api}, USDT: {usdt_balance}")
            else:
                usdt_balance = 500
                logger.warning("Dashboard: Using fallback mock data for balance")
        except Exception as e:
            logger.error(f"Dashboard: Error fetching MEXC balance: {e}")
            usdt_balance = 500
        
        # Get real price from MEXC API
        try:
            mexc_price = mexc_client.get_ticker_price('QRL/USDT')
            if mexc_price and mexc_price > 0:
                latest_price = mexc_price
                try:
                    redis_client.set_latest_price(latest_price)
                except Exception as e:
                    logger.warning(f"Dashboard: Cannot update price in Redis: {e}")
                logger.info(f"Dashboard: Using real MEXC price: {latest_price}")
            else:
                logger.warning(f"Dashboard: MEXC price not available, using Redis price: {latest_price}")
        except Exception as e:
            logger.error(f"Dashboard: Error fetching MEXC price: {e}")
            logger.warning(f"Dashboard: Using Redis price: {latest_price}")
        
        # If still no price data, use a demo price for display purposes
        if latest_price == 0:
            latest_price = 0.000850  # Demo price for QRL/USDT
            logger.info("Dashboard: Using demo price for display")
        
        # If no cost data, use demo cost slightly below current price
        if avg_cost == 0 and latest_price > 0:
            avg_cost = latest_price * 0.95  # Demo cost 5% below current price
            logger.info("Dashboard: Using demo average cost for display")
        
        total_value = (total_qrl * latest_price) + usdt_balance if latest_price > 0 else usdt_balance
        usdt_reserve_percent = (usdt_balance / total_value * 100) if total_value > 0 else 0
        
        # Prepare template data
        template_data = {
            'request': request,
            'bot_status': bot_status,
            'balance': {
                'qrl': total_qrl,
                'usdt': usdt_balance,
                'total_value': total_value
            },
            'price': {
                'current': latest_price,
                'avg_cost': avg_cost,
                'pnl_percent': pnl_percent
            },
            'layers': {
                'core_qrl': core_qrl,
                'swing_qrl': swing_qrl,
                'active_qrl': active_qrl,
                'core_percent': core_percent,
                'swing_percent': swing_percent,
                'active_percent': active_percent
            },
            'daily_trades': daily_trades,
            'max_daily_trades': config.MAX_DAILY_TRADES,
            'realized_pnl': realized_pnl,
            'unrealized_pnl': unrealized_pnl,
            'usdt_reserve_percent': usdt_reserve_percent,
            'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return templates.TemplateResponse('index.html', template_data)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>QRL Trading Bot - Error</title>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .error {{ background: white; padding: 30px; border-radius: 10px; max-width: 600px; }}
                h1 {{ color: #d32f2f; }}
                pre {{ background: #f5f5f5; padding: 15px; border-radius: 5px; overflow-x: auto; }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>⚠️ 服務暫時無法使用</h1>
                <p>儀表板載入失敗，可能原因：</p>
                <ul>
                    <li>Redis 連接失敗</li>
                    <li>MEXC API 連接失敗</li>
                    <li>環境變數未正確配置</li>
                </ul>
                <h3>錯誤詳情：</h3>
                <pre>{str(e)}</pre>
                <p><a href="/">← 返回首頁</a></p>
            </div>
        </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=503)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time dashboard updates
    Broadcasts trading updates, price changes, and bot status
    """
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates every 5 seconds
            await asyncio.sleep(5)
            
            try:
                # Gather current data
                bot_status = redis_client.get_bot_status() or 'unknown'
                latest_price = redis_client.get_latest_price() or 0
                daily_trades = redis_client.get_daily_trades()
                position = redis_client.get_position() or {}
                
                # Prepare update message
                update = {
                    'type': 'update',
                    'timestamp': datetime.now().isoformat(),
                    'bot_status': bot_status,
                    'price': latest_price,
                    'daily_trades': daily_trades,
                    'position': position
                }
                
                await websocket.send_json(update)
                
            except Exception as e:
                logger.error(f"Error sending WebSocket update: {e}")
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    """
    Favicon endpoint - serves the favicon file
    """
    import os
    favicon_path = os.path.join("static", "favicon.ico")
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path, media_type="image/x-icon")
    return Response(status_code=204)


@app.get("/health")
async def health():
    """
    Health check endpoint for Cloud Run
    Verifies Redis connection and bot status
    """
    try:
        redis_healthy = redis_client.health_check()
        bot_status = redis_client.get_bot_status()
        
        health_status = {
            'status': 'healthy' if redis_healthy else 'unhealthy',
            'redis': 'connected' if redis_healthy else 'disconnected',
            'bot_status': bot_status or 'unknown',
            'timestamp': int(time.time())
        }
        
        status_code = 200 if redis_healthy else 503
        return JSONResponse(content=health_status, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            content={'status': 'unhealthy', 'error': str(e)},
            status_code=503
        )


@app.post("/execute")
async def execute_trading():
    """
    Main trading execution endpoint
    Triggered by Cloud Scheduler
    """
    try:
        logger.info("Trading execution triggered")
        
        # Execute trading bot
        result = trading_bot.run()
        
        response = {
            'success': result['success'],
            'message': result['message'],
            'phase': result['phase'],
            'execution_time': result['execution_time']
        }
        
        status_code = 200 if result['success'] else 500
        logger.info(f"Trading execution completed: {response}")
        
        # Broadcast update to connected WebSocket clients
        await manager.broadcast({
            'type': 'trade_executed',
            'timestamp': datetime.now().isoformat(),
            'result': response
        })
        
        return JSONResponse(content=response, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Trading execution failed: {e}", exc_info=True)
        return JSONResponse(
            content={'success': False, 'error': str(e)},
            status_code=500
        )


@app.get("/status")
async def get_status():
    """
    Get current bot status and statistics
    """
    try:
        status = redis_client.get_bot_status()
        position = redis_client.get_position()
        latest_price = redis_client.get_latest_price()
        daily_trades = redis_client.get_daily_trades()
        last_trade_time = redis_client.get_last_trade_time()
        
        return {
            'bot_status': status or 'unknown',
            'position': position,
            'latest_price': latest_price,
            'daily_trades': daily_trades,
            'last_trade_time': last_trade_time,
            'max_daily_trades': config.MAX_DAILY_TRADES
        }
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/control")
async def control_bot(request: Request):
    """
    Control bot status (start/pause/stop)
    """
    try:
        data = await request.json()
        action = data.get('action', '').lower()
        
        if action not in ['start', 'pause', 'stop']:
            raise HTTPException(
                status_code=400,
                detail='Invalid action. Use: start, pause, or stop'
            )
        
        # Map actions to status
        status_map = {
            'start': 'running',
            'pause': 'paused',
            'stop': 'stopped'
        }
        
        new_status = status_map[action]
        redis_client.set_bot_status(new_status)
        
        logger.info(f"Bot status changed to: {new_status}")
        
        # Broadcast status change to WebSocket clients
        await manager.broadcast({
            'type': 'status_change',
            'timestamp': datetime.now().isoformat(),
            'new_status': new_status
        })
        
        return {
            'success': True,
            'status': new_status,
            'message': f'Bot {action}ed successfully'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Control action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        "main:app",
        host='0.0.0.0',
        port=config.PORT,
        reload=config.DEBUG,
        log_level="info"
    )
