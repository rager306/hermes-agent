"""Tests for tool result caching."""
import time
from tools.web_tools_cache import cache_tool_result, clear_tool_cache


class TestToolCache:
    def test_cache_returns_cached_result(self):
        """Second call with same args should return cached result."""
        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_operation(5)
        result2 = expensive_operation(5)

        assert result1 == result2 == 10
        assert call_count == 1

    def test_cache_different_args_not_cached(self):
        """Different args should not return cached result."""
        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive_operation(5)
        expensive_operation(10)

        assert call_count == 2

    def test_cache_expires_after_ttl(self):
        """Cache should expire after TTL."""
        call_count = 0

        @cache_tool_result(ttl_seconds=1)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive_operation(5)
        assert call_count == 1

        time.sleep(1.1)

        expensive_operation(5)
        assert call_count == 2

    def test_clear_cache(self):
        """clear_tool_cache should empty the cache."""
        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive_operation(5)
        assert call_count == 1

        clear_tool_cache(expensive_operation)

        expensive_operation(5)
        assert call_count == 2
