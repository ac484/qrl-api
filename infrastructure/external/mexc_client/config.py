"""Configuration helpers for MEXC client."""
from dataclasses import dataclass
from typing import Optional

from infrastructure.config.config import config


@dataclass
class MexcSettings:
    api_key: Optional[str]
    secret_key: Optional[str]
    base_url: str
    timeout: float


def load_settings(api_key: Optional[str] = None, secret_key: Optional[str] = None) -> MexcSettings:
    """Load settings while preserving whitespace stripping behaviour."""
    key = api_key or config.MEXC_API_KEY
    secret = secret_key or config.MEXC_SECRET_KEY
    return MexcSettings(
        api_key=key.strip() if key else None,
        secret_key=secret.strip() if secret else None,
        base_url=config.MEXC_BASE_URL,
        timeout=config.MEXC_TIMEOUT,
    )


__all__ = ["MexcSettings", "load_settings"]
