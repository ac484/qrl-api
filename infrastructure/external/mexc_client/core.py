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

from infrastructure.config.config import config
from infrastructure.external.mexc_client.account import build_balance_map, fetch_balance_snapshot

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
        # Strip whitespace and newlines from API credentials to prevent header errors
        self.api_key = (api_key or config.MEXC_API_KEY).strip() if (api_key or config.MEXC_API_KEY) else None
        self.secret_key = (secret_key or config.MEXC_SECRET_KEY).strip() if (secret_key or config.MEXC_SECRET_KEY) else None
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

    async def get_orderbook(self, symbol: str, limit: int = 100) -> Dict[str, Any]:
        """Alias for depth (compat)"""
        return await self.get_order_book(symbol, limit)

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

    async def get_aggregate_trades(
        self,
        symbol: str,
        limit: int = 500,
        from_id: Optional[int] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get compressed/aggregate trades list
        """
        params: Dict[str, Any] = {"symbol": symbol, "limit": limit}
        if from_id is not None:
            params["fromId"] = from_id
        if start_time is not None:
            params["startTime"] = start_time
        if end_time is not None:
            params["endTime"] = end_time
        return await self._request("GET", "/api/v3/aggTrades", params=params)

    async def get_book_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Best bid/ask for symbol (order book ticker)
        """
        params = {"symbol": symbol}
        return await self._request("GET", "/api/v3/ticker/bookTicker", params=params)

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

    async def get_balance(self, asset: Optional[str] = None) -> Dict[str, Any]:
        """Get balances as a simple asset map."""
        account_info = await self.get_account_info()
        balances = build_balance_map(account_info)
        if asset:
            return balances.get(asset, {"asset": asset, "free": "0", "locked": "0", "total": 0})
        return balances

    async def get_balance_snapshot(self, symbol: str = "QRLUSDT") -> Dict[str, Any]:
        """Get balances with current price snapshot for caching."""
        return await fetch_balance_snapshot(self, symbol=symbol)

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
    
    # ============ Spot API Sub-Account Methods (Regular Users) ============
    
    async def get_sub_accounts_spot(
        self, 
        sub_account_id: Optional[str] = None,
        page: int = 1, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get sub-account list using Spot API (for regular users)
        
        Args:
            sub_account_id: Optional sub-account ID filter
            page: Page number (default 1)
            limit: Results per page (default 10)
            
        Returns:
            {
                "subAccounts": [
                    {
                        "subAccountId": "123456",
                        "note": "Trading account",
                        "createTime": 1499865549590,
                        "status": "ACTIVE"
                    }
                ],
                "total": 1
            }
            
        Raises:
            Exception: If API request fails
        """
        params = {"page": page, "limit": limit}
        if sub_account_id:
            params["subAccountId"] = sub_account_id
        
        return await self._request("GET", "/api/v3/sub-account/list", 
                                  params=params, signed=True)
    
    async def transfer_between_sub_accounts(
        self,
        from_account_type: str,
        to_account_type: str,
        asset: str,
        amount: str,
        from_account: Optional[str] = None,
        to_account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Universal transfer between sub-accounts (Spot API)
        
        Supports transfers between:
        - Main account ↔ Sub-account
        - Sub-account ↔ Sub-account
        - Different account types: SPOT, MARGIN, ETF, CONTRACT
        
        Args:
            from_account_type: Source account type (SPOT, MARGIN, ETF, CONTRACT)
            to_account_type: Destination account type (SPOT, MARGIN, ETF, CONTRACT)
            asset: Asset symbol (e.g., "USDT", "BTC")
            amount: Transfer amount (string)
            from_account: Source sub-account ID (optional, omit for main account)
            to_account: Destination sub-account ID (optional, omit for main account)
            
        Returns:
            {
                "tranId": 123456789,
                "createTime": 1499865549590
            }
            
        Raises:
            Exception: If API request fails
        """
        params = {
            "fromAccountType": from_account_type,
            "toAccountType": to_account_type,
            "asset": asset,
            "amount": amount
        }
        if from_account:
            params["fromAccount"] = from_account
        if to_account:
            params["toAccount"] = to_account
            
        return await self._request("POST", "/api/v3/sub-account/universalTransfer",
                                  params=params, signed=True)
    
    async def create_sub_account_api_key(
        self,
        sub_account_id: str,
        note: str,
        permissions: List[str]
    ) -> Dict[str, Any]:
        """
        Create API key for sub-account (Spot API)
        
        Args:
            sub_account_id: Sub-account ID
            note: API key description/note
            permissions: Permission list (e.g., ["SPOT"])
            
        Returns:
            {
                "subAccountId": "123456",
                "apiKey": "...",
                "secretKey": "...",
                "permissions": ["SPOT"]
            }
            
        Raises:
            Exception: If API request fails
        """
        params = {
            "subAccountId": sub_account_id,
            "note": note,
            "permissions": permissions
        }
        return await self._request("POST", "/api/v3/sub-account/apiKey",
                                  params=params, signed=True)
    
    async def delete_sub_account_api_key(
        self,
        sub_account_id: str,
        api_key: str
    ) -> Dict[str, Any]:
        """
        Delete sub-account API key (Spot API)
        
        Args:
            sub_account_id: Sub-account ID
            api_key: API key to delete
            
        Returns:
            Success confirmation
            
        Raises:
            Exception: If API request fails
        """
        params = {
            "subAccountId": sub_account_id,
            "apiKey": api_key
        }
        return await self._request("DELETE", "/api/v3/sub-account/apiKey",
                                  params=params, signed=True)
    
    # ============ Broker API Sub-Account Methods (Broker Users) ============
    
    async def get_broker_sub_accounts(
        self,
        sub_account: Optional[str] = None,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get Broker sub-account list (Broker API)
        
        Args:
            sub_account: Optional sub-account name filter
            page: Page number (default 1)
            limit: Results per page (default 10)
            
        Returns:
            {
                "code": "0",
                "message": "",
                "data": [
                    {
                        "subAccount": "mexc1",
                        "note": "Trading account",
                        "timestamp": "1597026383085"
                    }
                ]
            }
            
        Raises:
            Exception: If API request fails or permissions insufficient
        """
        params = {
            "page": page,
            "limit": limit,
            "timestamp": int(time.time() * 1000)
        }
        if sub_account:
            params["subAccount"] = sub_account
        return await self._request("GET", "/api/v3/broker/sub-account/list",
                                  params=params, signed=True)
    
    async def get_broker_sub_account_assets(self, sub_account: str) -> Dict[str, Any]:
        """
        Query Broker sub-account assets (Broker API)
        
        Args:
            sub_account: Sub-account name
            
        Returns:
            {
                "balances": [
                    {
                        "asset": "BTC",
                        "free": "0.1",
                        "locked": "0.2"
                    }
                ]
            }
            
        Raises:
            Exception: If API request fails
        """
        params = {
            "subAccount": sub_account,
            "timestamp": int(time.time() * 1000)
        }
        return await self._request("GET", "/api/v3/broker/sub-account/assets",
                                  params=params, signed=True)
    
    async def broker_transfer_between_sub_accounts(
        self,
        from_account: str,
        to_account: str,
        asset: str,
        amount: str
    ) -> Dict[str, Any]:
        """
        Transfer between Broker sub-accounts (Broker API)
        
        Args:
            from_account: Source sub-account name
            to_account: Destination sub-account name
            asset: Asset symbol (e.g., "USDT", "BTC")
            amount: Transfer amount (string)
            
        Returns:
            {
                "tranId": 123456789,
                "fromAccount": "subaccount1",
                "toAccount": "subaccount2",
                "status": "SUCCESS"
            }
            
        Raises:
            Exception: If API request fails
        """
        params = {
            "fromAccount": from_account,
            "toAccount": to_account,
            "asset": asset,
            "amount": amount,
            "timestamp": int(time.time() * 1000)
        }
        return await self._request("POST", "/api/v3/broker/sub-account/transfer",
                                  params=params, signed=True)
    
    async def create_broker_sub_account_api_key(
        self,
        sub_account: str,
        permissions: str,
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create API key for Broker sub-account (Broker API)
        
        Args:
            sub_account: Sub-account name
            permissions: Permissions string (e.g., "SPOT_ACCOUNT_READ,SPOT_ACCOUNT_WRITE")
            note: Optional note/description
            
        Returns:
            {
                "subAccount": "...",
                "apikey": "...",
                "secretKey": "...",
                "permissions": "..."
            }
            
        Raises:
            Exception: If API request fails
        """
        params = {
            "subAccount": sub_account,
            "permissions": permissions,
            "timestamp": int(time.time() * 1000)
        }
        if note:
            params["note"] = note
        return await self._request("POST", "/api/v3/broker/sub-account/apiKey",
                                  params=params, signed=True)
    
    # ============ Unified Interface Methods ============
    
    async def get_sub_accounts(self) -> List[Dict[str, Any]]:
        """
        Unified sub-account list retrieval (auto-selects API based on configuration)
        
        Automatically chooses between:
        - Spot API (/api/v3/sub-account/list) for regular users
        - Broker API (/api/v3/broker/sub-account/list) for broker accounts
        
        Returns:
            List of sub-accounts with their details
            Format varies based on API mode:
            - Spot API: [{"subAccountId": "123", "note": "...", "status": "ACTIVE"}]
            - Broker API: [{"subAccount": "name", "note": "...", "timestamp": "..."}]
            
        Note:
            Returns empty list if API request fails or permissions are insufficient.
            Check logs for detailed error information.
        """
        from config import config
        
        try:
            if config.is_broker_mode:
                logger.info("Using Broker API for sub-accounts")
                result = await self.get_broker_sub_accounts()
                return result.get("data", [])
            else:
                logger.info("Using Spot API for sub-accounts")
                result = await self.get_sub_accounts_spot()
                return result.get("subAccounts", [])
        except Exception as e:
            logger.warning(f"Failed to get sub-accounts: {e}")
            return []
    
    async def get_sub_account_balance(self, identifier: str) -> Dict[str, Any]:
        """
        Unified sub-account balance retrieval
        
        Args:
            identifier: Sub-account identifier
                - Spot API: numeric subAccountId
                - Broker API: string subAccount name
                
        Returns:
            Balance information for the sub-account
            
        Raises:
            NotImplementedError: For Spot API (requires sub-account API key)
            Exception: If API request fails
            
        Note:
            Spot API does not support querying sub-account balance from main account.
            You must use the sub-account's own API key to query its balance.
        """
        from config import config
        
        if config.is_broker_mode:
            return await self.get_broker_sub_account_assets(identifier)
        else:
            raise NotImplementedError(
                "Spot API does not support querying sub-account balance from main account. "
                "You must use the sub-account's own API key to query its balance."
            )
    
    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
mexc_client = MEXCClient()
