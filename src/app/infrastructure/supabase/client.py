"""
Supabase client factory.
"""
import logging
from typing import Optional

from supabase import Client, create_client

from .config import SupabaseSettings, supabase_settings

logger = logging.getLogger(__name__)


class SupabaseClient:
    """Lazy Supabase client initializer shared by repositories."""

    def __init__(self, settings: SupabaseSettings = supabase_settings) -> None:
        self.settings = settings
        self._client: Optional[Client] = None

    @property
    def is_configured(self) -> bool:
        """Return True when URL and key are present."""
        return self.settings.configured

    @property
    def client(self) -> Client:
        """Return an initialized Supabase client, raising if configuration is missing."""
        if self._client is None:
            self._client = self._connect()
        return self._client

    def _connect(self) -> Client:
        url = self.settings.url
        api_key = self.settings.api_key
        if not url or not api_key:
            raise ValueError("Supabase settings are missing SUPABASE_URL or SUPABASE_KEY.")
        logger.info("Initializing Supabase client for schema '%s'", self.settings.schema)
        return create_client(url, api_key)

    def get_client(self) -> Optional[Client]:
        """
        Attempt to return an initialized client, swallowing errors and logging them.

        Useful for optional code paths where Supabase may be disabled.
        """
        try:
            return self.client
        except Exception as exc:  # pragma: no cover - defensive guard
            logger.error("Supabase client initialization failed: %s", exc)
            return None


supabase_client = SupabaseClient()

__all__ = ["SupabaseClient", "supabase_client"]
