"""Core MEXC v3 API client (async)."""
from __future__ import annotations

import logging
import time
from typing import Any, Dict, Optional

from .config import load_settings
from .connection import MexcConnection
from .endpoints import (
    AccountEndpoints,
    MarketEndpoints,
    OrderEndpoints,
    SubAccountEndpoints,
    TradingHelpersMixin,
    UserStreamMixin,
)
from .utils.signature import generate_signature

logger = logging.getLogger(__name__)


class MEXCClient(
    AccountEndpoints,
    MarketEndpoints,
    SubAccountEndpoints,
    TradingHelpersMixin,
    UserStreamMixin,
):
    """Async MEXC client composed from endpoint mixins."""

    def __init__(self, api_key: Optional[str] = None, secret_key: Optional[str] = None):
        self.settings = load_settings(api_key, secret_key)
        self.headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.settings.api_key:
            self.headers["X-MEXC-APIKEY"] = self.settings.api_key
        self._conn = MexcConnection(
            self.settings.base_url, self.headers, self.settings.timeout
        )

    async def __aenter__(self) -> "MEXCClient":
        await self._conn.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._conn.__aexit__(exc_type, exc_val, exc_tb)

    def _require_credentials(self) -> None:
        if not self.settings.api_key or not self.settings.secret_key:
            raise ValueError("API key and secret key required for authenticated requests")

    def _generate_signature(self, params: Dict[str, Any]) -> str:
        if not self.settings.secret_key:
            raise ValueError("Secret key required for authenticated requests")
        return generate_signature(self.settings.secret_key, params)

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        payload = params.copy() if params else {}
        if signed:
            self._require_credentials()
            payload["timestamp"] = int(time.time() * 1000)
            payload["signature"] = self._generate_signature(payload)
        return await self._conn.request(
            method, endpoint, params=payload, max_retries=max_retries
        )

    async def close(self) -> None:
        await self._conn.close()


# Singleton instance
mexc_client = MEXCClient()

__all__ = ["MEXCClient", "mexc_client"]
