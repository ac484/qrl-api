"""
MEXC API Client using Official MEXC SDK
Handles market data and account information retrieval with WebSocket support
"""
import logging
from typing import Dict, Optional, List, Any
from mexc_sdk import Spot, WebSocket
from config import config

logger = logging.getLogger(__name__)


class MEXCClient:
    """
    MEXC API Client using Official MEXC SDK
    Provides reliable exchange connectivity with WebSocket support
    """
    
    def __init__(self):
        """Initialize MEXC client with official SDK"""
        try:
            # Initialize Spot API client
            self.spot = Spot(
                api_key=config.MEXC_API_KEY,
                api_secret=config.MEXC_API_SECRET
            )
            
            self.symbol = 'QRLUSDT'  # MEXC format (no slash)
            logger.info("MEXC client initialized successfully with official SDK")
            
        except Exception as e:
            logger.error(f"Failed to initialize MEXC client: {e}")
            self.spot = None
    
    def health_check(self) -> bool:
        """
        Health check for MEXC API connectivity
        
        Returns:
            bool: True if API is accessible
        """
        try:
            if not self.spot:
                return False
            
            # Test connection with server time
            response = self.spot.time()
            return response.get('serverTime') is not None
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def get_ticker_price(self, symbol: str = None) -> Optional[float]:
        """
        Get current ticker price for a symbol
        
        Args:
            symbol: Trading pair symbol (default: QRL/USDT)
            
        Returns:
            float: Current price or None if error
        """
        try:
            if not self.spot:
                logger.error("MEXC client not initialized")
                return None
            
            ticker_symbol = self.symbol if symbol is None else symbol.replace('/', '')
            
            # Get ticker price using official SDK
            response = self.spot.ticker_price(symbol=ticker_symbol)
            
            if response and 'price' in response:
                price = float(response['price'])
                logger.info(f"Fetched {ticker_symbol} price: {price}")
                return price
            
            logger.warning(f"No price data in response for {ticker_symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching ticker price: {e}")
            return None
    
    def get_account_balance(self) -> Optional[Dict[str, float]]:
        """
        Get account balance for all assets
        
        Returns:
            Dict with asset balances or None if error
        """
        try:
            if not self.spot:
                logger.error("MEXC client not initialized")
                return None
            
            # Get account information
            response = self.spot.account()
            
            if not response or 'balances' not in response:
                logger.warning("No balance data in response")
                return None
            
            balances = {}
            for balance in response['balances']:
                asset = balance['asset']
                free = float(balance['free'])
                locked = float(balance['locked'])
                total = free + locked
                
                if total > 0:
                    balances[asset] = total
            
            logger.info(f"Fetched account balances: {len(balances)} assets with balance")
            return balances
            
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            return None
    
    def get_klines(self, symbol: str = None, interval: str = '1h', limit: int = 100) -> Optional[List[List]]:
        """
        Get candlestick data (klines)
        
        Args:
            symbol: Trading pair symbol
            interval: Kline interval (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of klines to fetch
            
        Returns:
            List of klines or None if error
        """
        try:
            if not self.spot:
                logger.error("MEXC client not initialized")
                return None
            
            ticker_symbol = self.symbol if symbol is None else symbol.replace('/', '')
            
            response = self.spot.klines(
                symbol=ticker_symbol,
                interval=interval,
                limit=limit
            )
            
            if response:
                logger.info(f"Fetched {len(response)} klines for {ticker_symbol}")
                return response
            
            logger.warning(f"No kline data for {ticker_symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            return None
    
    def get_24h_ticker(self, symbol: str = None) -> Optional[Dict[str, Any]]:
        """
        Get 24-hour ticker statistics
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Dict with 24h statistics or None if error
        """
        try:
            if not self.spot:
                logger.error("MEXC client not initialized")
                return None
            
            ticker_symbol = self.symbol if symbol is None else symbol.replace('/', '')
            
            response = self.spot.ticker_24hr(symbol=ticker_symbol)
            
            if response:
                logger.info(f"Fetched 24h ticker for {ticker_symbol}")
                return response
            
            logger.warning(f"No 24h ticker data for {ticker_symbol}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching 24h ticker: {e}")
            return None
    
    def create_order(self, side: str, quantity: float, price: Optional[float] = None) -> Optional[Dict]:
        """
        Create a new order
        
        Args:
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price (None for market order)
            
        Returns:
            Order response dict or None if error
        """
        try:
            if not self.spot:
                logger.error("MEXC client not initialized")
                return None
            
            order_type = 'LIMIT' if price else 'MARKET'
            
            params = {
                'symbol': self.symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity
            }
            
            if order_type == 'LIMIT':
                params['price'] = price
                params['timeInForce'] = 'GTC'
            
            response = self.spot.new_order(**params)
            
            if response:
                logger.info(f"Order created: {side} {quantity} {self.symbol} at {price or 'MARKET'}")
                return response
            
            logger.warning("Order creation failed")
            return None
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    def get_open_orders(self, symbol: str = None) -> Optional[List[Dict]]:
        """
        Get all open orders
        
        Args:
            symbol: Trading pair symbol (optional)
            
        Returns:
            List of open orders or None if error
        """
        try:
            if not self.spot:
                logger.error("MEXC client not initialized")
                return None
            
            ticker_symbol = self.symbol if symbol is None else symbol.replace('/', '')
            
            response = self.spot.open_orders(symbol=ticker_symbol)
            
            if response is not None:
                logger.info(f"Fetched {len(response)} open orders")
                return response
            
            return []
            
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return None


# Create singleton instance
mexc_client = MEXCClient()
