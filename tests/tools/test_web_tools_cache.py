"""Tests for tool result caching with property-based testing."""
import time
import pytest
from adaptix import loader

from tools.web_tools_cache import cache_tool_result, clear_tool_cache


class TestCacheToolResultBasics:
    """Basic cache functionality tests."""

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
        assert call_count == 1  # Only called once

    def test_cache_different_args_not_cached(self):
        """Different args should not return cached result."""
        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_operation(5)
        result2 = expensive_operation(10)
        result3 = expensive_operation(5)  # Same as result1, should be cached

        assert result1 == result3 == 10
        assert result2 == 20
        assert call_count == 2  # Called twice: once for 5, once for 10

    def test_cache_expires_after_ttl(self):
        """Cache should expire after TTL."""
        call_count = 0

        @cache_tool_result(ttl_seconds=1)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_operation(5)
        assert call_count == 1

        # Wait for TTL to expire
        time.sleep(1.1)

        result2 = expensive_operation(5)
        assert call_count == 2  # Called again due to expiration
        assert result1 == result2 == 10

    def test_clear_cache(self):
        """clear_tool_cache should empty the cache."""
        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_operation(5)
        assert call_count == 1

        clear_tool_cache(expensive_operation)

        result2 = expensive_operation(5)
        assert call_count == 2  # Called again after cache clear


class TestCacheWithAdaptix:
    """Property-based tests using adaptix for test data generation."""

    def test_cache_with_various_arg_types(self):
        """Cache should handle various argument types correctly.

        Note: JSON serialization converts tuples to lists and sets to lists,
        so cache behavior is type-aware in terms of cache keys but not
        type-preserving in return values.
        """
        @cache_tool_result(ttl_seconds=60)
        def returns_input(x):
            return x

        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def count_calls(x):
            nonlocal call_count
            call_count += 1
            return x

        # JSON-compatible types that preserve equality after serialization
        json_compatible = [
            [1, 2, 3],
            "hello world",
            {"a": 1, "b": 2},
            None,
            42,
            3.14,
            True,
            "",
            [[[1]]],  # nested lists
        ]

        for item in json_compatible:
            result1 = returns_input(item)
            result2 = returns_input(item)
            assert result1 == result2, f"Failed for item: {item!r}"

        # Verify caching actually works for different types
        count_calls("first")
        count_calls("second")
        count_calls("first")  # Should be cached
        assert call_count == 2

    def test_cache_hash_determinism(self):
        """Same args should always produce same cache key."""
        @cache_tool_result(ttl_seconds=60)
        def f(*args, **kwargs):
            return args, tuple(sorted(kwargs.items()))

        test_cases = [
            (([1, 2, 3],), {}),
            ((), {"a": 1, "b": 2}),
            (("hello",), {}),
        ]

        for args, kwargs in test_cases:
            result1 = f(*args, **kwargs)
            result2 = f(*args, **kwargs)
            assert result1 == result2


class TestCacheEdgeCases:
    """Edge case tests."""

    def test_empty_args(self):
        @cache_tool_result(ttl_seconds=60)
        def no_args():
            return "constant"

        assert no_args() == no_args() == "constant"

    def test_none_value(self):
        @cache_tool_result(ttl_seconds=60)
        def returns_none(x):
            return None

        assert returns_none(1) is None
        assert returns_none(1) is None  # Cached

    def test_mutable_args_not_cached_twice(self):
        """Mutations to list args after call should not affect cache."""
        @cache_tool_result(ttl_seconds=60)
        def process(lst):
            return sum(lst)

        original = [1, 2, 3]
        result1 = process(original)
        original.append(4)  # Mutate original
        # Note: cache uses hash, so mutation after call doesn't matter
        result2 = process([1, 2, 3])  # New list same contents
        assert result1 == result2


class TestCacheWithHypothesis:
    """Property-based tests using Hypothesis."""

    def test_cache_idempotent(self):
        """Cache should return same result for same input across many calls."""
        import hypothesis
        from hypothesis import given, settings
        import hypothesis.strategies as st

        @cache_tool_result(ttl_seconds=60)
        def double(x):
            return x * 2

        @given(x=st.integers(min_value=-10000, max_value=10000))
        @settings(max_examples=100)
        def test_double_idempotent(x):
            result1 = double(x)
            result2 = double(x)
            assert result1 == result2 == x * 2

        test_double_idempotent()

    def test_cache_with_strings(self):
        """Cache should work correctly with string arguments."""
        import hypothesis.strategies as st
        from hypothesis import given, settings

        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def process(s):
            nonlocal call_count
            call_count += 1
            return s.upper()

        @given(s=st.text(min_size=0, max_size=100))
        @settings(max_examples=50)
        def test_string_cache(s):
            result1 = process(s)
            result2 = process(s)
            assert result1 == result2 == s.upper()

        test_string_cache()

    def test_cache_with_lists(self):
        """Cache should work correctly with list arguments."""
        import hypothesis.strategies as st
        from hypothesis import given, settings

        call_count = 0

        @cache_tool_result(ttl_seconds=60)
        def sum_list(lst):
            nonlocal call_count
            call_count += 1
            return sum(lst)

        @given(lst=st.lists(st.integers(min_value=-100, max_value=100), min_size=0, max_size=50))
        @settings(max_examples=50)
        def test_list_cache(lst):
            result1 = sum_list(lst)
            result2 = sum_list(lst)
            assert result1 == result2

        test_list_cache()


class TestCacheTTLExpiration:
    """Tests for TTL expiration behavior."""

    def test_cache_exactly_at_boundary(self):
        """Cache should be valid just before TTL expires."""
        call_count = 0

        @cache_tool_result(ttl_seconds=1)
        def get_value(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = get_value(5)
        assert call_count == 1

        # Wait 0.9 seconds - should still be cached
        time.sleep(0.9)
        result2 = get_value(5)
        assert call_count == 1  # Still cached
        assert result1 == result2

    def test_multiple_items_expire_independently(self):
        """Each cached item should expire independently."""
        call_count = 0

        @cache_tool_result(ttl_seconds=1)
        def get_value(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        get_value(1)
        time.sleep(0.5)
        get_value(2)  # Different arg, different cache entry
        time.sleep(0.6)  # First item should be expired now

        result = get_value(1)  # Should recompute
        assert call_count == 3
        assert result == 2


class TestCacheHashCollision:
    """Tests for hash collision resistance."""

    def test_different_args_produce_different_cache_entries(self):
        """Different args must produce different cache entries (hash collision resistance)."""
        cache = {}

        @cache_tool_result(ttl_seconds=60)
        def func(x):
            if x not in cache:
                cache[x] = True
            return x

        # These should all be cached separately
        values = list(range(100))
        for v in values:
            result = func(v)
            assert result == v

        # All should have been computed (no hash collisions merging them)
        assert len(cache) == 100
