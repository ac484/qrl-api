"""
Decorators for common cross-cutting concerns.
Extracted from utils_core to improve structure.
"""
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


def handle_redis_errors(default_return: Any = None, log_prefix: str = "Redis operation") -> Callable:
    """Decorator for consistent Redis error handling."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - thin wrapper
                logger.error(f"{log_prefix} failed in {func.__name__}: {exc}")
                return default_return

        return wrapper

    return decorator


def handle_api_errors(log_prefix: str = "API operation") -> Callable:
    """Decorator for consistent API error handling."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as exc:  # pragma: no cover - thin wrapper
                logger.error(f"{log_prefix} failed in {func.__name__}: {exc}")
                raise

        return wrapper

    return decorator


def log_execution(log_level: int = logging.INFO, log_args: bool = False, log_result: bool = False) -> Callable:
    """Decorator for logging function execution."""

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

__all__ = ["handle_redis_errors", "handle_api_errors", "log_execution"]
