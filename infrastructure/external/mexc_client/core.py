"""
MEXC API Client for Spot Trading (v3)
Async implementation using httpx
Based on official MEXC API documentation
"""
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any

import httpx

from infrastructure.config.config import config
from infrastructure.external.mexc_client.signer import generate_signature
from infrastructure.external.mexc_client.market_endpoints import MarketEndpointsMixin
from infrastructure.external.mexc_client.account_repo import AccountRepoMixin
from infrastructure.external.mexc_client.trade_repo import TradeRepoMixin
from infrastructure.external.mexc_client.sub_account_spot_repo import SubAccountSpotRepoMixin
from infrastructure.external.mexc_client.sub_account_broker_repo import SubAccountBrokerRepoMixin
from infrastructure.external.mexc_client.sub_account_facade import SubAccountFacadeMixin
from infrastructure.external.mexc_client.account import build_balance_map, fetch_balance_snapshot
from infrastructure.external.mexc_client.market_endpoints import MarketEndpointsMixin
from infrastructure.external.mexc_client.account import build_balance_map, fetch_balance_snapshot

logger = logging.getLogger(__name__)


class MEXCClient(
    MarketEndpointsMixin,
    AccountRepoMixin,
    TradeRepoMixin,
    SubAccountSpotRepoMixin,
    SubAccountBrokerRepoMixin,
    SubAccountFacadeMixin,
):
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
        Generate HMAC SHA256 signature for signed requests.
        
        Args:
            params: Request parameters including timestamp.
        """
        if not self.secret_key:
            raise ValueError("Secret key required for authenticated requests")
        return generate_signature(self.secret_key, params)
    

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
    
    # ===== Account Endpoints (Authenticated) =====

    async def create_listen_key(self) -> Dict[str, Any]:
        """Generate a listen key for user data streams."""
        return await self._request("POST", "/api/v3/userDataStream", signed=True)

    async def keepalive_listen_key(self, listen_key: str) -> Dict[str, Any]:
        """Extend listen key validity (recommended every 30 minutes)."""
        return await self._request(
            "PUT", "/api/v3/userDataStream", params={"listenKey": listen_key}, signed=True
        )

    async def get_listen_keys(self) -> Dict[str, Any]:
        """Fetch valid listen keys for the current API key."""
        return await self._request("GET", "/api/v3/userDataStream", signed=True)

    async def close_listen_key(self, listen_key: str) -> Dict[str, Any]:
        """Close a listen key explicitly."""
        return await self._request(
            "DELETE", "/api/v3/userDataStream", params={"listenKey": listen_key}, signed=True
        )

    async def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: Optional[float] = None,
        quote_order_qty: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Convenience helper for market orders.
        
        Args:
            symbol: Trading symbol (e.g., QRLUSDT)
            side: BUY or SELL
            quantity: Base asset quantity
            quote_order_qty: Quote asset quantity (mutually exclusive with quantity)
        """
        if quantity is None and quote_order_qty is None:
            raise ValueError("Either quantity or quote_order_qty is required for market orders")
        return await self.create_order(
            symbol=symbol,
            side=side.upper(),
            order_type="MARKET",
            quantity=quantity,
            quote_order_qty=quote_order_qty,
        )
    









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
    








    async def close(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None


# Singleton instance
mexc_client = MEXCClient()
