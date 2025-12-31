"""
Base classes and helpers for Supabase repositories.
"""
import logging
from typing import Any, Dict, List, Optional

from supabase import Client

from src.app.infrastructure.supabase.client import supabase_client

logger = logging.getLogger(__name__)


class BaseSupabaseRepository:
    """Shared helpers for Supabase repositories."""

    def __init__(self, client: Optional[Client] = None) -> None:
        self._client = client

    def _resolve_client(self) -> Optional[Client]:
        if self._client is not None:
            return self._client
        self._client = supabase_client.get_client()
        return self._client

    def is_ready(self) -> bool:
        """Return True when a client is available."""
        return self._resolve_client() is not None

    def _execute(self, query) -> List[Dict[str, Any]]:
        client = self._resolve_client()
        if client is None:
            logger.warning("Supabase client unavailable, returning empty result.")
            return []
        response = query.execute()
        return response.data or []


__all__ = ["BaseSupabaseRepository"]
