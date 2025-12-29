"""
Redis key builder utilities extracted from utils_core.
"""
from __future__ import annotations


class RedisKeyBuilder:
    """Centralized Redis key management."""

    BOT_PREFIX = "bot"
    MEXC_PREFIX = "mexc"
    CACHE_PREFIX = "cache"

    @staticmethod
    def bot_status() -> str:
        return f"{RedisKeyBuilder.BOT_PREFIX}:status"

    @staticmethod
    def bot_position(symbol: str) -> str:
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:position"

    @staticmethod
    def bot_layers(symbol: str) -> str:
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:layers"

    @staticmethod
    def bot_trades_history(symbol: str) -> str:
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:trades:history"

    @staticmethod
    def bot_cost(symbol: str) -> str:
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:cost"

    @staticmethod
    def mexc_raw_response(endpoint: str) -> str:
        return f"{RedisKeyBuilder.MEXC_PREFIX}:raw_response:{endpoint}"

    @staticmethod
    def mexc_data(data_type: str) -> str:
        return f"{RedisKeyBuilder.MEXC_PREFIX}:{data_type}"

    @staticmethod
    def cache_data(category: str, symbol: str) -> str:
        return f"{RedisKeyBuilder.CACHE_PREFIX}:{category}:{symbol}"

    @staticmethod
    def price_history() -> str:
        return f"{RedisKeyBuilder.CACHE_PREFIX}:price_history"


def validate_symbol(symbol: str) -> str:
    """Validate and normalize trading symbol."""
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    normalized = symbol.upper().replace("/", "").replace("-", "").replace("_", "")
    if len(normalized) < 3:
        raise ValueError(f"Invalid symbol: {symbol}")
    return normalized

__all__ = ["RedisKeyBuilder", "validate_symbol"]
