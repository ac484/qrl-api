"""
Cache policy helpers for market service.
"""
from typing import Dict

_KLINE_TTL: Dict[str, int] = {
    "1m": 60,
    "5m": 300,
    "15m": 900,
    "1h": 3600,
    "4h": 14400,
    "1d": 86400,
}


def kline_ttl(interval: str) -> int:
    """Return TTL in seconds for given kline interval."""
    return _KLINE_TTL.get(interval, 60)

__all__ = ["kline_ttl"]
