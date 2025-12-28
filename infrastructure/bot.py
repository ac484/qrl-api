"""
QRL Trading Bot - Core Logic (Async)
6-Phase Trading Execution System
"""
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime

from config import config

logger = logging.getLogger(__name__)


class TradingBot:
    """QRL/USDT Trading Bot with MEXC API Integration (Async)"""
    
    def __init__(self, mexc_client, redis_client, symbol: str, dry_run: bool = False):
        """
        Initialize trading bot
        
        Args:
            mexc_client: MEXC API client instance
            redis_client: Redis client instance
            symbol: Trading symbol (e.g., "QRLUSDT")
            dry_run: Dry run mode (no actual trades)
        """
        self.mexc = mexc_client
        self.redis = redis_client
        self.symbol = symbol
        self.dry_run = dry_run
        
        self.execution_log: List[str] = []
    
    def _log(self, message: str, level: str = "info"):
        """Log message and store in execution log"""
        self.execution_log.append(f"[{level.upper()}] {message}")
        getattr(logger, level)(message)
    
    async def execute_cycle(self) -> Dict[str, Any]:
        """
        Execute complete trading cycle (6 phases)
        
        Returns:
            Execution result dictionary
        """
        self._log(f"Starting trading cycle for {self.symbol} (dry_run={self.dry_run})")
        
        start_time = time.time()
        result = {
            "success": False,
            "action": None,
            "phases": {},
            "message": "",
            "execution_log": []
        }
        
        try:
            # Phase 1: Startup & Validation
            if not await self._phase_1_startup():
                result["message"] = "Startup phase failed"
                result["execution_log"] = self.execution_log
                return result
            
            # Phase 2: Data Collection
            market_data = await self._phase_2_data_collection()
            if not market_data:
                result["message"] = "Data collection phase failed"
                result["execution_log"] = self.execution_log
                return result
            
            # Phase 3: Strategy Execution
            signal = await self._phase_3_strategy(market_data)
            result["phases"]["strategy"] = {"signal": signal}
            
            # Phase 4: Risk Control
            risk_check = await self._phase_4_risk_control(signal, market_data)
            result["phases"]["risk_control"] = risk_check
            
            if not risk_check["allowed"]:
                result["success"] = True
                result["action"] = "HOLD"
                result["message"] = risk_check["reason"]
                result["execution_log"] = self.execution_log
                return result
            
            # Phase 5: Execution
            if signal in ["BUY", "SELL"]:
                execution_result = await self._phase_5_execution(signal, market_data, risk_check)
                result["phases"]["execution"] = execution_result
                result["action"] = signal
                result["success"] = execution_result.get("success", False)
            else:
                result["success"] = True
                result["action"] = "HOLD"
            
            # Phase 6: Cleanup & Reporting
            await self._phase_6_cleanup(result)
            
            elapsed = time.time() - start_time
            result["message"] = f"Trading cycle completed in {elapsed:.2f}s"
            result["execution_log"] = self.execution_log
            
            self._log(f"Trading cycle completed: {result['action']}")
            return result
        
        except Exception as e:
            self._log(f"Trading cycle error: {e}", "error")
            result["message"] = f"Error: {str(e)}"
            result["execution_log"] = self.execution_log
            return result
    
    async def _phase_1_startup(self) -> bool:
        """Phase 1: Startup & Validation"""
        self._log("Phase 1: Startup & Validation")
        
        # Check Redis connection
        if not self.redis.connected:
            self._log("Redis not connected", "error")
            return False
        
        # Load position data
        position = await self.redis.get_position()
        self._log(f"Current position loaded: {len(position)} fields")
        
        # Load position layers
        layers = await self.redis.get_position_layers()
        if layers:
            self._log(f"Position layers: core={layers.get('core_qrl', '0')} QRL")
        
        return True
    
    async def _phase_2_data_collection(self) -> Optional[Dict[str, Any]]:
        """Phase 2: Data Collection"""
        self._log("Phase 2: Data Collection")
        
        try:
            # Get current price
            ticker = await self.mexc.get_ticker_24hr(self.symbol)
            price = float(ticker.get("lastPrice", 0))
            volume_24h = float(ticker.get("volume", 0))
            price_change_pct = float(ticker.get("priceChangePercent", 0))
            
            self._log(f"Price: {price}, Volume 24h: {volume_24h}, Change: {price_change_pct}%")
            
            # Store in Redis
            await self.redis.set_latest_price(price, volume_24h)
            await self.redis.add_price_to_history(price)
            
            # Get price history for strategy calculation
            price_history = await self.redis.get_price_history(limit=config.MA_LONG_PERIOD)
            
            # Get account balance (if API keys configured)
            qrl_balance = 0
            usdt_balance = 0
            
            if config.MEXC_API_KEY and config.MEXC_SECRET_KEY:
                try:
                    account_info = await self.mexc.get_account_info()
                    for balance in account_info.get("balances", []):
                        asset = balance.get("asset")
                        if asset == "QRL":
                            qrl_balance = float(balance.get("free", 0))
                        elif asset == "USDT":
                            usdt_balance = float(balance.get("free", 0))
                    
                    self._log(f"Balance: {qrl_balance} QRL, {usdt_balance} USDT")
                    
                    # Update position data in Redis
                    position_data = {
                        "qrl_balance": str(qrl_balance),
                        "usdt_balance": str(usdt_balance),
                    }
                    await self.redis.set_position(position_data)
                    
                    # Calculate and update cost data
                    position = await self.redis.get_position()
                    cost_data = await self.redis.get_cost_data()
                    
                    # Get or calculate average cost
                    avg_cost = float(cost_data.get("avg_cost", 0)) if cost_data.get("avg_cost") else price
                    total_invested = qrl_balance * avg_cost
                    unrealized_pnl = (price - avg_cost) * qrl_balance if avg_cost > 0 else 0
                    
                    await self.redis.set_cost_data(
                        avg_cost=avg_cost,
                        total_invested=total_invested,
                        unrealized_pnl=unrealized_pnl
                    )
                    
                except Exception as e:
                    self._log(f"Failed to get account balance: {e}", "warning")
            
            market_data = {
                "price": price,
                "volume_24h": volume_24h,
                "price_change_pct": price_change_pct,
                "price_history": price_history,
                "qrl_balance": qrl_balance,
                "usdt_balance": usdt_balance,
                "ticker": ticker
            }
            
            return market_data
        
        except Exception as e:
            self._log(f"Data collection failed: {e}", "error")
            return None
    
    async def _phase_3_strategy(self, market_data: Dict[str, Any]) -> str:
        """Phase 3: Strategy Execution"""
        self._log("Phase 3: Strategy Execution")
        
        price = market_data["price"]
        price_history = market_data["price_history"]
        
        # Calculate Moving Averages
        if len(price_history) < config.MA_LONG_PERIOD:
            self._log(f"Insufficient price history ({len(price_history)} < {config.MA_LONG_PERIOD})")
            return "HOLD"
        
        # Extract prices from history
        prices = [p["price"] for p in price_history]
        prices.append(price)  # Add current price
        
        # Calculate MA
        ma_short = sum(prices[-config.MA_SHORT_PERIOD:]) / config.MA_SHORT_PERIOD
        ma_long = sum(prices[-config.MA_LONG_PERIOD:]) / config.MA_LONG_PERIOD
        
        self._log(f"MA Short ({config.MA_SHORT_PERIOD}): {ma_short:.6f}")
        self._log(f"MA Long ({config.MA_LONG_PERIOD}): {ma_long:.6f}")
        
        # Get position data for cost-based decisions
        position = await self.redis.get_position()
        avg_cost = float(position.get("avg_cost", 0)) if position.get("avg_cost") else price
        
        # MA Crossover Strategy with Cost Consideration
        signal = "HOLD"
        
        # Buy signal: MA short crosses above MA long AND price below avg cost
        if ma_short > ma_long and price < avg_cost * 1.0:  # Only buy below or at cost
            signal = "BUY"
            self._log(f"BUY signal: MA crossover (price {price:.6f} < cost {avg_cost:.6f})")
        
        # Sell signal: MA short crosses below MA long AND price above avg cost
        elif ma_short < ma_long and price > avg_cost * 1.03:  # Sell at 3%+ profit
            signal = "SELL"
            self._log(f"SELL signal: MA crossover (price {price:.6f} > cost*1.03 {avg_cost*1.03:.6f})")
        
        else:
            self._log(f"HOLD: No clear signal (MA spread: {((ma_short/ma_long-1)*100):.2f}%)")
        
        return signal
    
    async def _phase_4_risk_control(self, signal: str, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 4: Risk Control"""
        self._log("Phase 4: Risk Control")
        
        # Check daily trade limit
        daily_trades = await self.redis.get_daily_trades()
        if daily_trades >= config.MAX_DAILY_TRADES:
            self._log(f"Daily trade limit reached: {daily_trades}/{config.MAX_DAILY_TRADES}")
            return {
                "allowed": False,
                "reason": f"Daily trade limit reached ({daily_trades}/{config.MAX_DAILY_TRADES})"
            }
        
        # Check minimum trade interval
        last_trade_time = await self.redis.get_last_trade_time()
        if last_trade_time:
            elapsed = int(time.time()) - last_trade_time
            if elapsed < config.MIN_TRADE_INTERVAL:
                self._log(f"Trade interval too short: {elapsed}s < {config.MIN_TRADE_INTERVAL}s")
                return {
                    "allowed": False,
                    "reason": f"Trade interval too short ({elapsed}s < {config.MIN_TRADE_INTERVAL}s)"
                }
        
        # Check position layers for SELL protection
        if signal == "SELL":
            layers = await self.redis.get_position_layers()
            if layers:
                total_qrl = float(layers.get("total_qrl", 0))
                core_qrl = float(layers.get("core_qrl", 0))
                tradeable_qrl = total_qrl - core_qrl
                
                if tradeable_qrl <= 0:
                    self._log("No tradeable QRL available (all in core position)")
                    return {
                        "allowed": False,
                        "reason": "No tradeable QRL (all in core position)"
                    }
        
        # Check USDT balance for BUY
        if signal == "BUY":
            usdt_balance = market_data.get("usdt_balance", 0)
            if usdt_balance <= 0:
                self._log("Insufficient USDT balance for BUY")
                return {
                    "allowed": False,
                    "reason": "Insufficient USDT balance"
                }
        
        self._log(f"Risk control passed for {signal}")
        return {
            "allowed": True,
            "reason": "Risk control passed",
            "daily_trades": daily_trades
        }
    
    async def _phase_5_execution(self, signal: str, market_data: Dict[str, Any], risk_check: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 5: Trade Execution"""
        self._log(f"Phase 5: Trade Execution ({signal})")
        
        price = market_data["price"]
        qrl_balance = market_data["qrl_balance"]
        usdt_balance = market_data["usdt_balance"]
        
        if self.dry_run:
            self._log("DRY RUN MODE - No actual trades will be executed")
        
        try:
            if signal == "BUY":
                # Calculate buy amount (use MAX_POSITION_SIZE of available USDT)
                usdt_to_use = usdt_balance * config.MAX_POSITION_SIZE
                qrl_quantity = usdt_to_use / price
                
                self._log(f"BUY: {qrl_quantity:.4f} QRL @ {price:.6f} (Total: {usdt_to_use:.2f} USDT)")
                
                if not self.dry_run:
                    order = await self.mexc.create_order(
                        symbol=self.symbol,
                        side="BUY",
                        order_type="MARKET",
                        quote_order_qty=usdt_to_use
                    )
                    self._log(f"Order created: {order.get('orderId')}")
                    
                    # Record trade
                    await self.redis.add_trade_record({
                        "action": "BUY",
                        "price": price,
                        "quantity": qrl_quantity,
                        "usdt_spent": usdt_to_use,
                        "order_id": order.get("orderId")
                    })
                else:
                    self._log("DRY RUN - Order not placed")
                
                # Update counters
                await self.redis.increment_daily_trades()
                await self.redis.set_last_trade_time()
                
                # Update average cost after BUY
                cost_data = await self.redis.get_cost_data()
                old_avg_cost = float(cost_data.get("avg_cost", 0)) if cost_data.get("avg_cost") else 0
                old_total_invested = float(cost_data.get("total_invested", 0)) if cost_data.get("total_invested") else 0
                
                # Calculate new weighted average cost
                new_total_invested = old_total_invested + usdt_to_use
                new_qrl_balance = qrl_balance + qrl_quantity
                new_avg_cost = new_total_invested / new_qrl_balance if new_qrl_balance > 0 else price
                
                await self.redis.set_cost_data(
                    avg_cost=new_avg_cost,
                    total_invested=new_total_invested,
                    unrealized_pnl=0  # Reset after buy
                )
                
                return {
                    "success": True,
                    "signal": "BUY",
                    "quantity": qrl_quantity,
                    "price": price,
                    "usdt_spent": usdt_to_use
                }
            
            elif signal == "SELL":
                # Calculate sell amount (use MAX_POSITION_SIZE of tradeable QRL)
                layers = await self.redis.get_position_layers()
                total_qrl = float(layers.get("total_qrl", qrl_balance))
                core_qrl = float(layers.get("core_qrl", total_qrl * config.CORE_POSITION_PCT))
                tradeable_qrl = total_qrl - core_qrl
                
                qrl_to_sell = tradeable_qrl * config.MAX_POSITION_SIZE
                usdt_expected = qrl_to_sell * price
                
                self._log(f"SELL: {qrl_to_sell:.4f} QRL @ {price:.6f} (Expected: {usdt_expected:.2f} USDT)")
                
                if not self.dry_run:
                    order = await self.mexc.create_order(
                        symbol=self.symbol,
                        side="SELL",
                        order_type="MARKET",
                        quantity=qrl_to_sell
                    )
                    self._log(f"Order created: {order.get('orderId')}")
                    
                    # Record trade
                    await self.redis.add_trade_record({
                        "action": "SELL",
                        "price": price,
                        "quantity": qrl_to_sell,
                        "usdt_received": usdt_expected,
                        "order_id": order.get("orderId")
                    })
                else:
                    self._log("DRY RUN - Order not placed")
                
                # Update counters
                await self.redis.increment_daily_trades()
                await self.redis.set_last_trade_time()
                
                # Update realized PnL after SELL
                cost_data = await self.redis.get_cost_data()
                avg_cost = float(cost_data.get("avg_cost", 0)) if cost_data.get("avg_cost") else price
                realized_pnl_from_trade = (price - avg_cost) * qrl_to_sell
                old_realized_pnl = float(cost_data.get("realized_pnl", 0)) if cost_data.get("realized_pnl") else 0
                
                # Update cost data
                new_realized_pnl = old_realized_pnl + realized_pnl_from_trade
                new_qrl_balance = qrl_balance - qrl_to_sell
                unrealized_pnl = (price - avg_cost) * new_qrl_balance if new_qrl_balance > 0 else 0
                
                await self.redis.set_cost_data(
                    avg_cost=avg_cost,  # Keep same average cost
                    total_invested=avg_cost * new_qrl_balance,
                    unrealized_pnl=unrealized_pnl,
                    realized_pnl=new_realized_pnl
                )
                
                return {
                    "success": True,
                    "signal": "SELL",
                    "quantity": qrl_to_sell,
                    "price": price,
                    "usdt_received": usdt_expected
                }
        
        except Exception as e:
            self._log(f"Execution failed: {e}", "error")
            return {
                "success": False,
                "signal": signal,
                "error": str(e)
            }
    
    async def _phase_6_cleanup(self, result: Dict[str, Any]):
        """Phase 6: Cleanup & Reporting"""
        self._log("Phase 6: Cleanup & Reporting")
        
        # Update execution statistics
        action = result.get("action", "HOLD")
        self._log(f"Execution completed with action: {action}")
        
        # Store execution result
        if self.redis.connected:
            await self.redis.add_trade_record({
                "cycle_action": action,
                "success": result.get("success", False),
                "timestamp": datetime.now().isoformat()
            })
        
        self._log("Cleanup completed")
