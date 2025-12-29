"""
Utility functions and decorators for QRL Trading API
Provides common patterns like error handling, logging, and caching
"""
import functools
import logging
from typing import Any, Callable, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar('T')


def handle_redis_errors(
    default_return: Any = None,
    log_prefix: str = "Redis operation"
) -> Callable:
    """
    Decorator for consistent Redis error handling
    
    Args:
        default_return: Value to return on error (None, False, {}, etc.)
        log_prefix: Prefix for error log messages
        
    Usage:
        @handle_redis_errors(default_return=False, log_prefix="Set operation")
        async def set_value(self, key, value):
            # ... Redis operations ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{log_prefix} failed in {func.__name__}: {e}")
                return default_return
        return wrapper
    return decorator


def handle_api_errors(
    log_prefix: str = "API operation"
) -> Callable:
    """
    Decorator for consistent API error handling
    
    Args:
        log_prefix: Prefix for error log messages
        
    Usage:
        @handle_api_errors(log_prefix="MEXC API call")
        async def get_ticker(self, symbol):
            # ... API operations ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"{log_prefix} failed in {func.__name__}: {e}")
                raise
        return wrapper
    return decorator


def log_execution(
    log_level: int = logging.INFO,
    log_args: bool = False,
    log_result: bool = False
) -> Callable:
    """
    Decorator for logging function execution
    
    Args:
        log_level: Logging level (INFO, DEBUG, etc.)
        log_args: Whether to log function arguments
        log_result: Whether to log function result
        
    Usage:
        @log_execution(log_level=logging.DEBUG, log_args=True)
        async def process_data(self, data):
            # ... processing ...
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = func.__name__
            
            if log_args:
                logger.log(log_level, f"Calling {func_name} with args={args[1:]}, kwargs={kwargs}")
            else:
                logger.log(log_level, f"Calling {func_name}")
            
            result = await func(*args, **kwargs)
            
            if log_result:
                logger.log(log_level, f"{func_name} returned: {result}")
            
            return result
        return wrapper
    return decorator


class RedisKeyBuilder:
    """
    Centralized Redis key management
    Ensures consistent key naming across the application
    """
    
    # Key prefixes
    BOT_PREFIX = "bot"
    MEXC_PREFIX = "mexc"
    CACHE_PREFIX = "cache"
    
    @staticmethod
    def bot_status() -> str:
        """Bot status key"""
        return f"{RedisKeyBuilder.BOT_PREFIX}:status"
    
    @staticmethod
    def bot_position(symbol: str) -> str:
        """Bot position key for a symbol"""
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:position"
    
    @staticmethod
    def bot_layers(symbol: str) -> str:
        """Position layers key for a symbol"""
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:layers"
    
    @staticmethod
    def bot_trades_history(symbol: str) -> str:
        """Trade history key for a symbol"""
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:trades:history"
    
    @staticmethod
    def bot_cost(symbol: str) -> str:
        """Cost tracking key for a symbol"""
        return f"{RedisKeyBuilder.BOT_PREFIX}:{symbol}:cost"
    
    @staticmethod
    def mexc_raw_response(endpoint: str) -> str:
        """MEXC raw API response key"""
        return f"{RedisKeyBuilder.MEXC_PREFIX}:raw_response:{endpoint}"
    
    @staticmethod
    def mexc_data(data_type: str) -> str:
        """MEXC processed data key"""
        return f"{RedisKeyBuilder.MEXC_PREFIX}:{data_type}"
    
    @staticmethod
    def cache_data(category: str, symbol: str) -> str:
        """Cache data key"""
        return f"{RedisKeyBuilder.CACHE_PREFIX}:{category}:{symbol}"
    
    @staticmethod
    def price_history() -> str:
        """Price history key"""
        return f"{RedisKeyBuilder.CACHE_PREFIX}:price_history"


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize trading symbol
    
    Args:
        symbol: Trading symbol (e.g., "QRLUSDT", "qrl/usdt")
        
    Returns:
        Normalized symbol in uppercase without separators
        
    Raises:
        ValueError: If symbol is invalid
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")
    
    # Remove common separators and convert to uppercase
    normalized = symbol.upper().replace('/', '').replace('-', '').replace('_', '')
    
    # Basic validation
    if len(normalized) < 3:
        raise ValueError(f"Invalid symbol: {symbol}")
    
    return normalized


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert value to float
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Float value or default
    """
    try:
        return float(value) if value is not None else default
    except (ValueError, TypeError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert value to int
    
    Args:
        value: Value to convert
        default: Default value if conversion fails
        
    Returns:
        Int value or default
    """
    try:
        return int(value) if value is not None else default
    except (ValueError, TypeError):
        return default

__all__ = [
    "handle_redis_errors",
    "handle_api_errors",
    "log_execution",
    "RedisKeyBuilder",
    "validate_symbol",
    "safe_float",
    "safe_int",
]
