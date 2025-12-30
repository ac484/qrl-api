"""Signature helpers for MEXC v3 requests."""
from typing import Any, Dict
import hashlib
import hmac
from urllib.parse import urlencode


def generate_signature(secret_key: str, params: Dict[str, Any]) -> str:
    """Generate HMAC SHA256 signature with sorted params."""
    if secret_key is None or not secret_key.strip():
        raise ValueError("Secret key must be a non-empty string")
    query_string = urlencode(sorted(params.items()))
    return hmac.new(
        secret_key.encode("utf-8"),
        query_string.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


__all__ = ["generate_signature"]
