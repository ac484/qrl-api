"""Signing utilities for MEXC client."""
import hashlib
import hmac
from urllib.parse import urlencode
from typing import Dict, Any


def generate_signature(secret_key: str, params: Dict[str, Any]) -> str:
    query_string = urlencode(sorted(params.items()))
    return hmac.new(secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()

__all__ = ["generate_signature"]
