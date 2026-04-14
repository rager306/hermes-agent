"""Caching layer for expensive tool calls."""
import functools
import hashlib
import json
import time
from collections.abc import Callable
from typing import Any


def cache_tool_result(ttl_seconds: int = 300):
    """Decorator to cache tool results by arguments.

    Args:
        ttl_seconds: Time-to-live for cache entries (default 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        cache: dict[str, tuple[Any, float]] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            key = json.dumps((args, sorted(kwargs.items())), sort_keys=True)
            args_hash = hashlib.sha256(key.encode()).hexdigest()[:16]
            current_time = time.time()

            if args_hash in cache:
                result, timestamp = cache[args_hash]
                if current_time - timestamp < ttl_seconds:
                    return result

            result = func(*args, **kwargs)
            cache[args_hash] = (result, current_time)
            return result

        wrapper._cache = cache
        return wrapper

    return decorator


def clear_tool_cache(func: Callable) -> None:
    """Clear cache for a decorated function."""
    if hasattr(func, '_cache'):
        func._cache.clear()
