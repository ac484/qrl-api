"""Generic utility helpers for the structured modules."""
from datetime import datetime
from typing import Any, Optional


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.utcnow().isoformat()


__all__ = ["safe_float", "utc_now_iso"]
