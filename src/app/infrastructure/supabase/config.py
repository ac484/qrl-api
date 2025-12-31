"""
Supabase configuration sourced from environment variables.
"""
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class SupabaseSettings(BaseSettings):
    """
    Lightweight Supabase configuration.

    Reads the project URL and API keys from the environment without failing import
    when values are missing so the application can still start in environments
    where Supabase is optional.
    """

    url: Optional[str] = None
    key: Optional[str] = None
    service_role_key: Optional[str] = None
    database_schema: str = "public"
    timeout: int = 10

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SUPABASE_",
        extra="ignore",
        protected_namespaces=(),
    )

    @property
    def api_key(self) -> Optional[str]:
        """Prefer the service role key when provided."""
        return self.service_role_key or self.key

    @property
    def configured(self) -> bool:
        """Check whether URL and an API key are both present."""
        return bool(self.url and self.api_key)

    @property
    def schema(self) -> str:
        """Expose the configured schema name (defaults to public)."""
        return self.database_schema


supabase_settings = SupabaseSettings()

__all__ = ["SupabaseSettings", "supabase_settings"]
