"""HTTP connection management with retry helpers."""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from .exceptions import MexcAPIError, MexcRequestError
from .session import build_async_client

logger = logging.getLogger(__name__)


class MexcConnection:
    """Thin wrapper around httpx.AsyncClient with retry/backoff."""

    def __init__(self, base_url: str, headers: Dict[str, str], timeout: float):
        self.base_url = base_url
        self.headers = headers
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "MexcConnection":
        self._client = build_async_client(self.headers, self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _ensure_client(self) -> httpx.AsyncClient:
        if not self._client:
            self._client = build_async_client(self.headers, self.timeout)
        return self._client

    def _use_query_params(self, method: str, endpoint: str) -> bool:
        normalized = method.upper()
        if normalized in {"GET", "DELETE"}:
            return True
        if normalized == "PUT" and "userDataStream" in endpoint:
            return True
        return False

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        payload = params or {}
        last_error: Optional[Exception] = None
        normalized_method = method.upper()
        use_query = self._use_query_params(normalized_method, endpoint)
        request_kwargs = {"params": payload} if use_query else {"json": payload}

        for attempt in range(max_retries):
            try:
                client = await self._ensure_client()
                response = await client.request(normalized_method, url, **request_kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                last_error = exc
                status = exc.response.status_code
                if status in (429, 503, 504) and attempt < max_retries - 1:
                    wait = 2**attempt
                    logger.warning(
                        "MEXC API error %s, retrying in %ss (attempt %s/%s)",
                        status,
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise
            except httpx.RequestError as exc:
                last_error = exc
                if attempt < max_retries - 1:
                    wait = 2**attempt
                    logger.warning(
                        "MEXC API network error: %s, retrying in %ss (attempt %s/%s)",
                        exc,
                        wait,
                        attempt + 1,
                        max_retries,
                    )
                    await asyncio.sleep(wait)
                    continue
                raise

        if last_error:
            raise last_error
        raise MexcRequestError("Unknown request failure")


__all__ = ["MexcConnection"]
