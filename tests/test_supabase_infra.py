import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.app.infrastructure.supabase.client import SupabaseClient, supabase_client
from src.app.infrastructure.supabase.config import SupabaseSettings
from src.app.infrastructure.supabase.repositories.account_repo import AccountRepository


def test_supabase_settings_not_configured_by_default(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    settings = SupabaseSettings()
    assert not settings.configured
    assert settings.api_key is None


def test_supabase_settings_reads_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    refreshed = SupabaseSettings()
    assert refreshed.configured
    assert refreshed.api_key == "test-key"


def test_account_repo_returns_empty_when_no_supabase(monkeypatch):
    # Ensure the shared client is not configured for this test
    monkeypatch.setattr(supabase_client, "settings", SupabaseSettings())
    supabase_client._client = None
    repo = AccountRepository()
    assert repo.fetch_balances("user-1") == []


def test_supabase_client_handles_missing_config(monkeypatch):
    monkeypatch.setattr(supabase_client, "settings", SupabaseSettings())
    supabase_client._client = None
    client = SupabaseClient(supabase_client.settings)
    assert client.get_client() is None
