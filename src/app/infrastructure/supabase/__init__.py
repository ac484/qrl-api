"""
Supabase infrastructure package exposing the configured client and settings.
"""
from .client import SupabaseClient, supabase_client
from .config import SupabaseSettings, supabase_settings

__all__ = [
    "SupabaseClient",
    "supabase_client",
    "SupabaseSettings",
    "supabase_settings",
]
