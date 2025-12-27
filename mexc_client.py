"""
MEXC API Client for Spot Trading (v3)
Based on official MEXC API documentation
"""
import hashlib
import hmac
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config

logger = logging.getLogger(__name__)


class MEXCClient:
    """MEXC Spot API v3 Client"""
    
    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        """
        Initialize MEXC API client
        
        Args:
            api_key: MEXC API key
            secret_key: MEXC secret key
        """
        self.api_key = api_key or config.MEXC_API_KEY
        self.secret_key = secret_key or config.MEXC_SECRET_KEY
        self.base_url = config.MEXC_BASE_URL
        self.timeout = config.MEXC_TIMEOUT
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=1,
            allowed_methods=["GET", "POST", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Set default headers
        if self.api_key:
            self.session.headers.update({
                "X-MEXC-APIKEY": self.api_key,
                "Content-Type": "application/json"
            })
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for authenticated requests
        
        Args:
            params: Request parameters
            
        Returns:
            HMAC SHA256 signature
        """
        query_string = urlencode(sorted(params.items()))
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False
    ) -> Dict[str, Any]:
        """
        Make HTTP request to MEXC API
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request requires signature
            
        Returns:
            API response as dictionary
        """
        url = f"{self.base_url}{endpoint}"
        params = params or {}
        
        # Add timestamp and signature for authenticated requests
        if signed:
            if not self.api_key or not self.secret_key:
                raise ValueError("API key and secret key required for authenticated requests")
            
            params["timestamp"] = int(time.time() * 1000)
            params["signature"] = self._generate_signature(params)
        
        try:
            if method == "GET":
                response = self.session.get(url, params=params, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(url, params=params, timeout=self.timeout)
            elif method == "DELETE":
                response = self.session.delete(url, params=params, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"MEXC API request failed: {e}")
            raise
    
    # ===== Public Market Data Endpoints =====
    
    def ping(self) -> Dict[str, Any]:
        """Test connectivity to MEXC API"""
        return self._request("GET", "/api/v3/ping")
    
    def get_server_time(self) -> Dict[str, Any]:
        """Get current server time"""
        return self._request("GET", "/api/v3/time")
    
    def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/api/v3/exchangeInfo", params=params)
    
    def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
        """
        params = {"symbol": symbol}
        return self._request("GET", "/api/v3/ticker/24hr", params=params)
    
    def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get latest price for a symbol
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
        """
        params = {"symbol": symbol}
        return self._request("GET", "/api/v3/ticker/price", params=params)
    
    def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get order book depth
        
        Args:
            symbol: Trading symbol
            limit: Depth limit (default 100, max 5000)
        """
        params = {"symbol": symbol, "limit": limit}
        return self._request("GET", "/api/v3/depth", params=params)
    
    def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get recent trades
        
        Args:
            symbol: Trading symbol
            limit: Number of trades (default 500, max 1000)
        """
        params = {"symbol": symbol, "limit": limit}
        return self._request("GET", "/api/v3/trades", params=params)
    
    def get_klines(
        self,
        symbol: str,
        interval: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        limit: int = 500
    ) -> List[List]:
        """
        Get candlestick data
        
        Args:
            symbol: Trading symbol
            interval: Kline interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M)
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of klines (default 500, max 1000)
        """
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        return self._request("GET", "/api/v3/klines", params=params)
    
    # ===== Account Endpoints (Authenticated) =====
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get current account information"""
        return self._request("GET", "/api/v3/account", signed=True)
    
    def get_asset_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account asset balance
        
        Args:
            asset: Specific asset (e.g., "QRL", "USDT"). If None, returns all balances.
        """
        account_info = self.get_account_info()
        
        if asset:
            for balance in account_info.get("balances", []):
                if balance.get("asset") == asset:
                    return balance
            return {"asset": asset, "free": "0", "locked": "0"}
        
        return account_info
    
    # ===== Trading Endpoints (Authenticated) =====
    
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
        price: Optional[float] = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            symbol: Trading symbol
            side: Order side (BUY or SELL)
            order_type: Order type (LIMIT, MARKET, LIMIT_MAKER)
            quantity: Order quantity (base asset)
            quote_order_qty: Quote order quantity (for MARKET orders)
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force (GTC, IOC, FOK)
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
        }
        
        if quantity:
            params["quantity"] = quantity
        if quote_order_qty:
            params["quoteOrderQty"] = quote_order_qty
        if price:
            params["price"] = price
        if order_type == "LIMIT":
            params["timeInForce"] = time_in_force
        
        return self._request("POST", "/api/v3/order", params=params, signed=True)
    
    def cancel_order(self, symbol: str, order_id: Optional[str] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an active order
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            orig_client_order_id: Original client order ID
        """
        params = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        if orig_client_order_id:
            params["origClientOrderId"] = orig_client_order_id
        
        return self._request("DELETE", "/api/v3/order", params=params, signed=True)
    
    def get_order(self, symbol: str, order_id: Optional[str] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check an order's status
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            orig_client_order_id: Original client order ID
        """
        params = {"symbol": symbol}
        if order_id:
            params["orderId"] = order_id
        if orig_client_order_id:
            params["origClientOrderId"] = orig_client_order_id
        
        return self._request("GET", "/api/v3/order", params=params, signed=True)
    
    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders
        
        Args:
            symbol: Trading symbol (optional, returns all if not specified)
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        return self._request("GET", "/api/v3/openOrders", params=params, signed=True)
    
    def get_all_orders(self, symbol: str, order_id: Optional[str] = None, start_time: Optional[int] = None, end_time: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get all account orders (active, canceled, or filled)
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of orders (default 500, max 1000)
        """
        params = {"symbol": symbol, "limit": limit}
        if order_id:
            params["orderId"] = order_id
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return self._request("GET", "/api/v3/allOrders", params=params, signed=True)
    
    def get_my_trades(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get account trade list
        
        Args:
            symbol: Trading symbol
            start_time: Start time in milliseconds
            end_time: End time in milliseconds
            limit: Number of trades (default 500, max 1000)
        """
        params = {"symbol": symbol, "limit": limit}
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return self._request("GET", "/api/v3/myTrades", params=params, signed=True)


# Singleton instance
mexc_client = MEXCClient()
