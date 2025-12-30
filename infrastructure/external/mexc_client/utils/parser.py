"""Lightweight helpers for normalising API payloads."""
from typing import Any, Dict


def ensure_dict(payload: Any) -> Dict[str, Any]:
    """Return payload if dict else wrap for uniform handling."""
    if isinstance(payload, dict):
        return payload
    return {"raw": payload}


__all__ = ["ensure_dict"]
