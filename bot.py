"""
Trading Bot Logic Module
Implements the core trading strategy and execution flow
"""
import logging
import time
from typing import Dict, Any, Optional, Tuple
from enum import Enum

from config import config
from redis_client import redis_client
from mexc_client import mexc_client

logger = logging.getLogger(__name__)


class TradeSignal(Enum):
    """Trading signals"""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class TradingBot:
    """Main trading bot class implementing strategy and execution logic"""
    
    def __init__(self):
        """Initialize trading bot"""
        self.trading_pair = config.TRADING_PAIR
        logger.info(f"TradingBot initialized for {self.trading_pair}")
    
    def run(self) -> Dict[str, Any]:
        """
        Main execution flow for the trading bot
        
        Returns:
            dict: Execution result summary
        """
        start_time = time.time()
        result = {
            'success': False,
            'phase': None,
            'message': '',
            'execution_time': 0
        }
        
        try:
            # Phase 1: Startup (0-2 seconds)
            logger.info("Phase 1: Startup")
            result['phase'] = 'startup'
            if not self._startup_phase():
                result['message'] = 'Startup phase failed'
                return result
            
            # Phase 2: Data Collection (2-5 seconds)
            logger.info("Phase 2: Data Collection")
            result['phase'] = 'data_collection'
            market_data = self._data_collection_phase()
            if not market_data:
                result['message'] = 'Data collection failed'
                return result
            
            # Phase 3: Strategy判斷 (5-8 seconds)
            logger.info("Phase 3: Strategy Execution")
            result['phase'] = 'strategy'
            signal = self._strategy_phase(market_data)
            
            # Phase 4: Risk Control (8-10 seconds)
            logger.info("Phase 4: Risk Control")
            result['phase'] = 'risk_control'
            if not self._risk_control_phase(signal, market_data):
                result['message'] = 'Risk control check failed'
                result['success'] = True  # Not an error, just didn't pass risk checks
                return result
            
            # Phase 5: Execute Trade (10-15 seconds)
            logger.info("Phase 5: Trade Execution")
            result['phase'] = 'execution'
            trade_result = self._execution_phase(signal, market_data)
            
            # Phase 6: Cleanup & Report (15-20 seconds)
            logger.info("Phase 6: Cleanup & Report")
            result['phase'] = 'cleanup'
            self._cleanup_phase(trade_result)
            
            result['success'] = True
            result['message'] = f'Execution completed. Signal: {signal.value}'
            
        except Exception as e:
            logger.error(f"Error in bot execution: {e}", exc_info=True)
            result['message'] = f'Error: {str(e)}'
        
        finally:
            result['execution_time'] = time.time() - start_time
            logger.info(f"Bot execution completed in {result['execution_time']:.2f}s")
        
        return result
    
    def _startup_phase(self) -> bool:
        """
        Startup phase: Load state and verify connections
        
        Returns:
            bool: True if startup successful
        """
        try:
            # Check Redis connection
            if not redis_client.health_check():
                logger.error("Redis health check failed")
                return False
            
            # Load bot status
            status = redis_client.get_bot_status()
            if status == 'paused':
                logger.info("Bot is paused, skipping execution")
                return False
            
            # Initialize status if not set
            if not status:
                redis_client.set_bot_status('running')
            
            logger.info("Startup phase completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Startup phase error: {e}")
            return False
    
    def _data_collection_phase(self) -> Optional[Dict[str, Any]]:
        """
        Data collection phase: Fetch market data and account info from MEXC API
        
        Returns:
            dict: Market data or None if failed
        """
        try:
            # Fetch current price from MEXC (use correct symbol format with slash)
            current_price = mexc_client.get_ticker_price('QRL/USDT')
            if not current_price or current_price <= 0:
                logger.warning("Failed to fetch price from MEXC, using last known price")
                current_price = redis_client.get_latest_price() or 0.5
            
            # Store in Redis
            redis_client.set_latest_price(current_price)
            redis_client.add_price_to_history(current_price)
            
            # Fetch account balance from MEXC
            balance = mexc_client.get_account_balance()
            if not balance or (balance.get('USDT', 0) == 0 and balance.get('QRL', 0) == 0):
                logger.warning("Failed to fetch balance from MEXC, using mock data")
                balance = {'USDT': 1000.0, 'QRL': 0.0}
            
            market_data = {
                'price': current_price,
                'balance': balance,
                'position': redis_client.get_position() or {'size': 0, 'entry_price': 0}
            }
            
            logger.info(f"Market data collected: price={current_price}, "
                       f"USDT={balance.get('USDT', 0)}, QRL={balance.get('QRL', 0)}")
            return market_data
            
        except Exception as e:
            logger.error(f"Data collection error: {e}")
            return None
    
    def _strategy_phase(self, market_data: Dict[str, Any]) -> TradeSignal:
        """
        Strategy phase: Dynamic Layered Accumulation Strategy
        
        Implements dynamic position management with three layers:
        - Core position (70%): Never traded, long-term hold
        - Swing position (20%): Week-level trades on 10-20% moves
        - Active position (10%): Day-level trades on 3-8% moves
        
        Args:
            market_data: Current market data
            
        Returns:
            TradeSignal: Trading signal (BUY/SELL/HOLD)
        """
        try:
            # Get price history and calculate moving average
            price_history = redis_client.get_price_history(100)
            
            if len(price_history) < config.LONG_MA_PERIOD:
                logger.info("Insufficient price history for strategy")
                return TradeSignal.HOLD
            
            # Calculate moving average using MEXC client (more reliable with CCXT)
            long_ma = mexc_client.calculate_moving_average(period=config.LONG_MA_PERIOD)
            if not long_ma:
                # Fallback to manual calculation from Redis history
                long_ma = sum(price_history[:config.LONG_MA_PERIOD]) / config.LONG_MA_PERIOD
                logger.info(f"Using fallback MA calculation: {long_ma:.6f}")
            
            current_price = market_data['price']
            
            # Get cost tracking data
            cost_data = redis_client.get_cost_tracking()
            avg_cost = float(cost_data.get('avg_cost', current_price)) if cost_data else current_price
            
            # Get last sell price for buyback strategy
            last_sell_price = redis_client.get_latest_price() or current_price
            
            logger.info(f"Accumulation strategy - Price: {current_price:.6f}, "
                       f"MA({config.LONG_MA_PERIOD}): {long_ma:.6f}, "
                       f"Avg Cost: {avg_cost:.6f}")
            
            # ===== SELL SIGNALS (only active/swing positions, never core) =====
            
            # Check if we should sell active position (quick profit taking)
            if current_price >= avg_cost * config.ACTIVE_SELL_THRESHOLD:
                logger.info(f"Signal: SELL (Active position - price {((current_price/avg_cost-1)*100):.1f}% above cost)")
                return TradeSignal.SELL
            
            # Check if we should sell swing position (larger profit taking)
            if current_price >= avg_cost * config.SWING_SELL_THRESHOLD:
                logger.info(f"Signal: SELL (Swing position - price {((current_price/avg_cost-1)*100):.1f}% above cost)")
                return TradeSignal.SELL
            
            # ===== BUY SIGNALS (accumulation strategy) =====
            
            # Buy condition 1: Price dip below moving average
            if current_price < long_ma * config.DCA_DIP_THRESHOLD:
                if not config.ALLOW_BUY_ABOVE_COST and current_price > avg_cost:
                    logger.info(f"Price dip detected but above cost - HOLD (cost protection)")
                    return TradeSignal.HOLD
                
                logger.info(f"Signal: BUY (Price dip - {((1-current_price/long_ma)*100):.1f}% below MA)")
                return TradeSignal.BUY
            
            # Buy condition 2: Buyback after selling (price dropped from last sell)
            drop_percent = (1 - current_price / last_sell_price) * 100
            if drop_percent >= config.BUYBACK_DROP_PERCENT:
                logger.info(f"Signal: BUY (Buyback - price dropped {drop_percent:.1f}% from last sell)")
                return TradeSignal.BUY
            
            # Buy condition 3: Periodic accumulation (DCA)
            last_trade_time = redis_client.get_last_trade_time()
            if last_trade_time:
                import time
                hours_since_last = (time.time() - last_trade_time) / 3600
                if hours_since_last >= config.DCA_INTERVAL_HOURS:
                    if not config.ALLOW_BUY_ABOVE_COST and current_price > avg_cost:
                        logger.info(f"Periodic DCA due but price above cost - HOLD (cost protection)")
                        return TradeSignal.HOLD
                    
                    logger.info(f"Signal: BUY (Periodic DCA - {hours_since_last:.1f}h since last trade)")
                    return TradeSignal.BUY
            
            # Default: HOLD
            logger.info("Signal: HOLD (Waiting for better opportunity)")
            return TradeSignal.HOLD
                
        except Exception as e:
            logger.error(f"Strategy phase error: {e}")
            return TradeSignal.HOLD
    
    def _risk_control_phase(self, signal: TradeSignal, market_data: Dict[str, Any]) -> bool:
        """
        Risk control phase: Verify trading conditions with core position protection
        
        For accumulation strategy:
        - Protects core position (never sell below core threshold)
        - Ensures USDT reserve for future opportunities
        - Validates sell profit meets minimum threshold
        
        Args:
            signal: Trading signal
            market_data: Current market data
            
        Returns:
            bool: True if risk checks pass
        """
        try:
            if signal == TradeSignal.HOLD:
                return False
            
            # Check daily trade limit
            daily_trades = redis_client.get_daily_trades()
            if daily_trades >= config.MAX_DAILY_TRADES:
                logger.warning(f"Daily trade limit reached: {daily_trades}/{config.MAX_DAILY_TRADES}")
                return False
            
            balance = market_data['balance']
            current_price = market_data['price']
            
            # ===== BUY signal checks =====
            if signal == TradeSignal.BUY:
                # Check USDT balance
                if balance['USDT'] < config.MIN_USDT_FOR_TRADE:
                    logger.warning(f"Insufficient USDT balance: {balance['USDT']}")
                    return False
                
                # Check if we're maintaining minimum USDT reserve
                total_value = balance['QRL'] * current_price + balance['USDT']
                min_usdt_reserve = total_value * (config.MIN_USDT_RESERVE_PERCENT / 100)
                
                if balance['USDT'] < min_usdt_reserve:
                    logger.warning(f"USDT below minimum reserve: {balance['USDT']} < {min_usdt_reserve}")
                    return False
                
                logger.info("Risk control checks passed for BUY")
                return True
            
            # ===== SELL signal checks =====
            if signal == TradeSignal.SELL:
                # Get position layers to protect core position
                layers = redis_client.get_position_layers()
                if layers:
                    core_qrl = float(layers.get('core_qrl', 0))
                    total_qrl = balance['QRL']
                    
                    # Ensure we never sell below core position
                    if total_qrl <= core_qrl:
                        logger.warning(f"Cannot sell: at or below core position ({total_qrl} <= {core_qrl})")
                        return False
                
                # Check minimum tradeable QRL
                tradeable_qrl = redis_client.get_tradeable_qrl('all')
                if tradeable_qrl < 0.1:
                    logger.warning(f"Insufficient tradeable QRL: {tradeable_qrl}")
                    return False
                
                # Check if sell meets minimum profit requirement
                cost_data = redis_client.get_cost_tracking()
                if cost_data:
                    avg_cost = float(cost_data.get('avg_cost', 0))
                    if avg_cost > 0:
                        profit_percent = ((current_price / avg_cost) - 1) * 100
                        if profit_percent < config.MIN_SELL_PROFIT_PERCENT:
                            logger.warning(f"Profit {profit_percent:.2f}% below minimum {config.MIN_SELL_PROFIT_PERCENT}%")
                            return False
                
                logger.info("Risk control checks passed for SELL")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Risk control error: {e}")
            return False
    
    def _execution_phase(self, signal: TradeSignal, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execution phase: Execute the trade
        
        Args:
            signal: Trading signal
            market_data: Current market data
            
        Returns:
            dict: Trade execution result
        """
        try:
            # TODO: Implement actual MEXC API order execution
            # For now, simulate trade execution
            
            trade_result = {
                'executed': True,
                'signal': signal.value,
                'price': market_data['price'],
                'timestamp': int(time.time())
            }
            
            # Update Redis
            redis_client.increment_daily_trades()
            redis_client.set_last_trade_time(trade_result['timestamp'])
            
            logger.info(f"Trade executed: {signal.value} at {market_data['price']}")
            return trade_result
            
        except Exception as e:
            logger.error(f"Execution phase error: {e}")
            return {'executed': False, 'error': str(e)}
    
    def _cleanup_phase(self, trade_result: Dict[str, Any]) -> None:
        """
        Cleanup phase: Update statistics and send notifications
        
        Args:
            trade_result: Result from execution phase
        """
        try:
            # TODO: Calculate P&L, update statistics, send notifications
            logger.info("Cleanup phase completed")
            
        except Exception as e:
            logger.error(f"Cleanup phase error: {e}")


# Create singleton instance
trading_bot = TradingBot()
