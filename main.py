"""
Main application entry point for QRL Trading Bot
Flask web server for Cloud Run deployment
"""
import logging
import sys
import time
from flask import Flask, request, jsonify
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
    Root endpoint - basic info
    """
    return jsonify({
        'service': 'QRL Trading Bot',
        'version': '1.0.0',
        'status': 'running',
        'trading_pair': config.TRADING_PAIR
    })


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
    logger.info(f"Redis: {config.REDIS_HOST}:{config.REDIS_PORT}")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )
