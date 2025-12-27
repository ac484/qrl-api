"""
Main application entry point for QRL Trading Bot
Flask web server for Cloud Run deployment
"""
import logging
import sys
import time
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from pythonjsonlogger import jsonlogger

from config import config
from redis_client import redis_client
from bot import trading_bot

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

# Create Flask app
app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    """
    Root endpoint - redirect to dashboard or return JSON
    """
    # Check if request wants HTML (browser) or JSON (API)
    if request.accept_mimetypes.accept_html:
        return dashboard()
    
    return jsonify({
        'service': 'QRL Trading Bot',
        'version': '1.0.0',
        'status': 'running',
        'trading_pair': config.TRADING_PAIR
    })


@app.route('/dashboard', methods=['GET'])
def dashboard():
    """
    Web dashboard - shows balance, positions, and trading stats
    """
    try:
        # Get all data
        bot_status = redis_client.get_bot_status() or 'unknown'
        latest_price = redis_client.get_latest_price() or 0
        daily_trades = redis_client.get_daily_trades()
        
        # Get position data
        position = redis_client.get_position() or {}
        qrl_balance = position.get('size', 0)
        
        # Get position layers
        layers_data = redis_client.get_position_layers()
        if layers_data:
            core_qrl = float(layers_data.get('core_qrl', qrl_balance * 0.7))
            swing_qrl = float(layers_data.get('swing_qrl', qrl_balance * 0.2))
            active_qrl = float(layers_data.get('active_qrl', qrl_balance * 0.1))
        else:
            # Default distribution if not set
            core_qrl = qrl_balance * 0.7
            swing_qrl = qrl_balance * 0.2
            active_qrl = qrl_balance * 0.1
        
        total_qrl = core_qrl + swing_qrl + active_qrl
        
        # Calculate percentages for display
        core_percent = (core_qrl / total_qrl * 100) if total_qrl > 0 else 70
        swing_percent = (swing_qrl / total_qrl * 100) if total_qrl > 0 else 20
        active_percent = (active_qrl / total_qrl * 100) if total_qrl > 0 else 10
        
        # Get cost tracking
        cost_data = redis_client.get_cost_tracking()
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
        
        # Mock USDT balance (in production, get from MEXC API)
        usdt_balance = 500  # TODO: Get from MEXC API
        total_value = (total_qrl * latest_price) + usdt_balance if latest_price > 0 else usdt_balance
        usdt_reserve_percent = (usdt_balance / total_value * 100) if total_value > 0 else 0
        
        # Prepare template data
        template_data = {
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
        
        return render_template('dashboard.html', **template_data)
        
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        return f"<h1>Error loading dashboard</h1><p>{str(e)}</p>", 500


@app.route('/health', methods=['GET'])
def health():
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
            'timestamp': int(time.time()) if 'time' in dir() else 0
        }
        
        status_code = 200 if redis_healthy else 503
        return jsonify(health_status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@app.route('/execute', methods=['POST'])
def execute_trading():
    """
    Main trading execution endpoint
    Triggered by Cloud Scheduler
    """
    try:
        logger.info("Trading execution triggered")
        
        # Verify request (optional: check for Cloud Scheduler headers)
        # In production, validate the request comes from Cloud Scheduler
        
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
        
        return jsonify(response), status_code
        
    except Exception as e:
        logger.error(f"Trading execution failed: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Get current bot status and statistics
    """
    try:
        status = redis_client.get_bot_status()
        position = redis_client.get_position()
        latest_price = redis_client.get_latest_price()
        daily_trades = redis_client.get_daily_trades()
        last_trade_time = redis_client.get_last_trade_time()
        
        return jsonify({
            'bot_status': status or 'unknown',
            'position': position,
            'latest_price': latest_price,
            'daily_trades': daily_trades,
            'last_trade_time': last_trade_time,
            'max_daily_trades': config.MAX_DAILY_TRADES
        })
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/control', methods=['POST'])
def control_bot():
    """
    Control bot status (start/pause/stop)
    """
    try:
        data = request.get_json()
        action = data.get('action', '').lower()
        
        if action not in ['start', 'pause', 'stop']:
            return jsonify({
                'error': 'Invalid action. Use: start, pause, or stop'
            }), 400
        
        # Map actions to status
        status_map = {
            'start': 'running',
            'pause': 'paused',
            'stop': 'stopped'
        }
        
        new_status = status_map[action]
        redis_client.set_bot_status(new_status)
        
        logger.info(f"Bot status changed to: {new_status}")
        
        return jsonify({
            'success': True,
            'status': new_status,
            'message': f'Bot {action}ed successfully'
        })
        
    except Exception as e:
        logger.error(f"Control action failed: {e}")
        return jsonify({
            'error': str(e)
        }), 500


if __name__ == '__main__':
    logger.info(f"Starting QRL Trading Bot on port {config.PORT}")
    logger.info(f"Trading pair: {config.TRADING_PAIR}")
    logger.info(f"Redis: {config.REDIS_URL}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )
