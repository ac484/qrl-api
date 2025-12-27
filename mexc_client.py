"""
MEXC API Client for Spot Trading (v3)
Async implementation using httpx
Based on official MEXC API documentation
"""
import asyncio
import hashlib
import hmac
import time
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

import httpx

from config import config

logger = logging.getLogger(__name__)


class MEXCClient:
    """MEXC Spot API v3 Client (Async)"""
    
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
        
        # Default headers
        self.headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            self.headers["X-MEXC-APIKEY"] = self.api_key
        
        # Client will be created per request or reused
        self._client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=self.timeout,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self._client:
            await self._client.aclose()
    
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
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Make async HTTP request to MEXC API with retry logic
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint
            params: Request parameters
            signed: Whether request requires signature
            max_retries: Maximum number of retry attempts
            
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
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                # Create client if not exists
                if not self._client:
                    self._client = httpx.AsyncClient(
                        headers=self.headers,
                        timeout=self.timeout
                    )
                
                if method == "GET":
                    response = await self._client.get(url, params=params)
                elif method == "POST":
                    response = await self._client.post(url, params=params)
                elif method == "DELETE":
                    response = await self._client.delete(url, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                response.raise_for_status()
                return response.json()
            
            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code in [429, 503, 504]:
                    # Rate limit or server error - retry with exponential backoff
                    wait_time = 2 ** attempt
                    logger.warning(f"MEXC API error {e.response.status_code}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(wait_time)
                        continue
                raise
            
            except httpx.RequestError as e:
                last_exception = e
                # Network error - retry with exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"MEXC API network error: {e}, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                    continue
                raise
        
        # If we get here, all retries failed
        logger.error(f"MEXC API request failed after {max_retries} attempts: {last_exception}")
        raise last_exception if last_exception else Exception("Unknown error")
    
    # ===== Public Market Data Endpoints =====
    
    async def ping(self) -> Dict[str, Any]:
        """Test connectivity to MEXC API"""
        return await self._request("GET", "/api/v3/ping")
    
    async def get_server_time(self) -> Dict[str, Any]:
        """Get current server time"""
        return await self._request("GET", "/api/v3/time")
    
    async def get_exchange_info(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get exchange trading rules and symbol information
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        return await self._request("GET", "/api/v3/exchangeInfo", params=params)
    
    async def get_ticker_24hr(self, symbol: str) -> Dict[str, Any]:
        """
        Get 24hr ticker price change statistics
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
        """
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/24hr", params=params)
    
    async def get_ticker_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get latest price for a symbol
        
        Args:
            symbol: Trading symbol (e.g., "QRLUSDT")
        """
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/price", params=params)
    
    async def get_order_book(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get order book depth
        
        Args:
            symbol: Trading symbol
            limit: Depth limit (default 100, max 5000)
        """
        params = {"symbol": symbol, "limit": limit}
        return await self._request("GET", "/api/v3/depth", params=params)
    
    async def get_recent_trades(self, symbol: str, limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get recent trades
        
        Args:
            symbol: Trading symbol
            limit: Number of trades (default 500, max 1000)
        """
        params = {"symbol": symbol, "limit": limit}
        return await self._request("GET", "/api/v3/trades", params=params)
    
    async def get_klines(
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
        return await self._request("GET", "/api/v3/klines", params=params)
    
    # ===== Account Endpoints (Authenticated) =====
    
    async def get_account_info(self) -> Dict[str, Any]:
        """Get current account information"""
        return await self._request("GET", "/api/v3/account", signed=True)
    
    async def get_asset_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """
        Get account asset balance
        
        Args:
            asset: Specific asset (e.g., "QRL", "USDT"). If None, returns all balances.
        """
        account_info = await self.get_account_info()
        
        if asset:
            for balance in account_info.get("balances", []):
                if balance.get("asset") == asset:
                    return balance
            return {"asset": asset, "free": "0", "locked": "0"}
        
        return account_info
    
    # ===== Trading Endpoints (Authenticated) =====
    
    async def create_order(
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
        
        return await self._request("POST", "/api/v3/order", params=params, signed=True)
    
    async def cancel_order(self, symbol: str, order_id: Optional[str] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
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
        
        return await self._request("DELETE", "/api/v3/order", params=params, signed=True)
    
    async def get_order(self, symbol: str, order_id: Optional[str] = None, orig_client_order_id: Optional[str] = None) -> Dict[str, Any]:
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
        
        return await self._request("GET", "/api/v3/order", params=params, signed=True)
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all open orders
        
        Args:
            symbol: Trading symbol (optional, returns all if not specified)
        """
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        return await self._request("GET", "/api/v3/openOrders", params=params, signed=True)
    
    async def get_all_orders(self, symbol: str, order_id: Optional[str] = None, start_time: Optional[int] = None, end_time: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
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
        
        return await self._request("GET", "/api/v3/allOrders", params=params, signed=True)
    
    async def get_my_trades(self, symbol: str, start_time: Optional[int] = None, end_time: Optional[int] = None, limit: int = 500) -> List[Dict[str, Any]]:
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
        
        return await self._request("GET", "/api/v3/myTrades", params=params, signed=True)
    
    # ===== Sub-Account Endpoints (Authenticated) =====
    
    async def get_sub_accounts(self) -> List[Dict[str, Any]]:
        """
        Get sub-accounts list
        
        Returns:
            List of sub-accounts
        """
        try:
            # MEXC sub-account API endpoint
            # Note: This endpoint may require special permissions
            return await self._request("GET", "/api/v3/sub-account/list", signed=True)
        except Exception as e:
            logger.warning(f"Failed to get sub-accounts (may not be supported): {e}")
            return []
    
    async def get_sub_account_balance(self, email: str) -> Dict[str, Any]:
        """
        Get sub-account balance
        
        Args:
            email: Sub-account email
            
        Returns:
            Sub-account balance information
        """
        params = {"email": email}
        return await self._request("GET", "/api/v3/sub-account/assets", params=params, signed=True)
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
mexc_client = MEXCClient()
