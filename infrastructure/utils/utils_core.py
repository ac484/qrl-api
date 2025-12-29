"""
Compatibility layer aggregating utility helpers.
Logic is split across dedicated modules for clarity and reuse.
"""
import logging

from .decorators import handle_redis_errors, handle_api_errors, log_execution
from .keys import RedisKeyBuilder, validate_symbol
from .type_safety import safe_float, safe_int

logger = logging.getLogger(__name__)

__all__ = [
    "handle_redis_errors",
    "handle_api_errors",
    "log_execution",
    "RedisKeyBuilder",
    "validate_symbol",
    "safe_float",
    "safe_int",
]
