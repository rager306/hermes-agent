# Hermes Agent Performance Optimization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce latency by 2-5 seconds per multi-tool turn through Python 3.13 upgrade, parallel tool execution, and async improvements.

**Architecture:** Tiered approach starting with zero-code-change optimizations (Python version), then adding parallel execution infrastructure for read-only tools, then async improvements. No architectural changes — purely incremental performance enhancements.

**Tech Stack:** Python 3.13, asyncio.TaskGroup, ThreadPoolExecutor, functools.lru_cache

---

## Scope

This plan covers Tier 1 and Tier 2 optimizations:
1. Python 3.13 upgrade (pyproject.toml change)
2. HERMES_TOOL_DELAY=0.0 (env change)
3. Expand _PARALLEL_SAFE_TOOLS with true parallel execution
4. Add asyncio.TaskGroup patterns
5. Tool result caching for read_file and web_search

---

## Task 1: Python 3.13 Upgrade

**Files:**
- Modify: `pyproject.toml:1-50`

- [ ] **Step 1: Read current pyproject.toml python requirement**

Run: `grep -n "python" pyproject.toml | head -5`
Expected: Shows current `python = ">=3.12"` or similar

- [ ] **Step 2: Update python version to >=3.13**

Modify `pyproject.toml` line containing `python = `:
```
python = ">=3.13"
```

- [ ] **Step 3: Verify uv can resolve dependencies**

Run: `uv sync --dry-run 2>&1 | head -20`
Expected: No python version conflicts

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml
git commit -m "perf: require Python 3.13 for baseline speedup (~5-15%)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: HERMES_TOOL_DELAY=0.0

**Files:**
- Modify: `~/.hermes/.env:331`

- [ ] **Step 1: Set HERMES_TOOL_DELAY=0.0 in .env**

Run: `grep -n "HERMES_TOOL_DELAY" ~/.hermes/.env`
Expected: Shows current value (0.7)

Edit `~/.hermes/.env` line 331:
```
HERMES_TOOL_DELAY=0.0
```

- [ ] **Step 2: Verify Hermes starts with new delay**

Run: `HERMES_TOOL_DELAY=0.0 uv run hermes gateway run --replace &`
Wait 10s, check logs:
```bash
tail -5 /root/.hermes/logs/gateway.log
```
Expected: Gateway running, no errors

- [ ] **Step 3: Note in .env.example**

If `.env.example` exists, add or update:
```
HERMES_TOOL_DELAY=0.0
```

- [ ] **Step 4: Commit**

```bash
git add .env.example 2>/dev/null || true
git commit -m "perf: set HERMES_TOOL_DELAY=0.0 for zero-latency tool execution

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Add True Parallel Tool Execution

**Files:**
- Modify: `run_agent.py:7500-7520`
- Test: `tests/run_agent/test_parallel_tool_execution.py`

- [ ] **Step 1: Read current tool execution loop**

Run: `sed -n '7490,7520p' run_agent.py`
Expected: Sequential loop with `time.sleep(self.tool_delay)`

- [ ] **Step 2: Identify safe tools that can run in parallel**

Current `_PARALLEL_SAFE_TOOLS` at line ~244:
```python
_PARALLEL_SAFE_TOOLS = frozenset({
    "ha_get_state", "ha_list_entities", "ha_list_services",
    "read_file", "search_files", "session_search",
    "skill_view", "skills_list", "vision_analyze",
    "web_extract", "web_search",
})
```

- [ ] **Step 3: Create test for parallel execution**

Create `tests/run_agent/test_parallel_tool_execution.py`:
```python
"""Tests for parallel tool execution on safe tools."""
import pytest
from run_agent import _PARALLEL_SAFE_TOOLS, _is_tool_parallel_safe


class TestParallelSafeTools:
    def test_parallel_safe_tools_defined(self):
        """_PARALLEL_SAFE_TOOLS should contain expected read-only tools."""
        expected = {"read_file", "search_files", "web_search", "web_extract"}
        assert expected.issubset(_PARALLEL_SAFE_TOOLS)

    def test_is_tool_parallel_safe_returns_true_for_safe_tools(self):
        """Read-only tools should be marked as parallel-safe."""
        safe_tools = ["read_file", "search_files", "web_search"]
        for tool in safe_tools:
            assert _is_tool_parallel_safe(tool) is True

    def test_is_tool_parallel_safe_returns_false_for_unsafe_tools(self):
        """Write tools should not be parallel-safe."""
        unsafe_tools = ["write_file", "browser_tool", "terminal"]
        for tool in unsafe_tools:
            assert _is_tool_parallel_safe(tool) is False
```

- [ ] **Step 4: Run test to verify it fails (no _is_tool_parallel_safe yet)**

Run: `pytest tests/run_agent/test_parallel_tool_execution.py -v 2>&1 | head -30`
Expected: FAIL with "cannot import name '_is_tool_parallel_safe'"

- [ ] **Step 5: Implement _is_tool_parallel_safe function**

Add near `_PARALLEL_SAFE_TOOLS` (around line 244):
```python
def _is_tool_parallel_safe(tool_name: str) -> bool:
    """Check if a tool is safe to run in parallel with other tools."""
    return tool_name in _PARALLEL_SAFE_TOOLS
```

- [ ] **Step 6: Run test to verify it passes**

Run: `pytest tests/run_agent/test_parallel_tool_execution.py -v`
Expected: PASS (3 tests)

- [ ] **Step 7: Modify tool execution loop for parallel safe tools**

Modify `run_agent.py:7500-7515` to use asyncio.gather for parallel-safe tools:

Change from:
```python
for i, tool_call in enumerate(assistant_message.tool_calls):
    if should_skip:
        skipped_tc = assistant_message.tool_calls[i]
        skipped_name = skipped_tc.function.name
        skip_msg = {
            "role": "tool",
            "content": f"[Tool execution skipped — {skipped_name} was not started. User sent a new message]",
            "tool_call_id": skipped_tc.id
        }
        messages.append(skip_msg)
        break

    if self.tool_delay > 0 and i < len(assistant_message.tool_calls):
        time.sleep(self.tool_delay)
```

To:
```python
# Group tools: parallel-safe vs sequential
parallel_calls = []
sequential_calls = []
for i, tool_call in enumerate(assistant_message.tool_calls):
    if should_skip:
        skipped_tc = assistant_message.tool_calls[i]
        skipped_name = skipped_tc.function.name
        skip_msg = {
            "role": "tool",
            "content": f"[Tool execution skipped — {skipped_name} was not started. User sent a new message]",
            "tool_call_id": skipped_tc.id
        }
        messages.append(skip_msg)
        break

    if _is_tool_parallel_safe(tool_call.function.name):
        parallel_calls.append((i, tool_call))
    else:
        sequential_calls.append((i, tool_call))

# Execute parallel-safe tools concurrently
if parallel_calls and self.tool_delay == 0:
    # Run parallel tools together
    import asyncio
    # ... (will complete in Step 8)
```

- [ ] **Step 8: Complete parallel execution implementation**

Add after the grouping logic:
```python
    # Execute parallel-safe tools concurrently
    if parallel_calls and self.tool_delay == 0:
        import asyncio
        async def run_parallel():
            tasks = []
            for i, tool_call in parallel_calls:
                task = self._run_tool_async(function_name, function_args, effective_task_id, tool_call.id)
                tasks.append(task)
            return await asyncio.gather(*tasks, return_exceptions=True)

        parallel_results = asyncio.run(run_parallel())
        for (i, tool_call), result in zip(parallel_calls, parallel_results):
            if isinstance(result, Exception):
                messages.append({"role": "tool", "content": f"Error: {result}", "tool_call_id": tool_call.id})
            else:
                messages.append(result)

    # Execute sequential tools with delays
    for i, tool_call in sequential_calls:
        if self.tool_delay > 0:
            time.sleep(self.tool_delay)
        result = self._run_tool(function_name, function_args, effective_task_id, tool_call.id)
        messages.append(result)
```

- [ ] **Step 9: Run existing tests to verify no regression**

Run: `pytest tests/run_agent/test_run_agent.py -v -k "test_tool" 2>&1 | head -50`
Expected: All pass or pre-existing failures (not from our changes)

- [ ] **Step 10: Commit**

```bash
git add tests/run_agent/test_parallel_tool_execution.py run_agent.py
git commit -m "perf: add parallel execution for _PARALLEL_SAFE_TOOLS

- Add _is_tool_parallel_safe() function
- Group tools into parallel-safe and sequential buckets
- Execute parallel-safe tools concurrently with asyncio.gather
- Maintain sequential execution with delays for unsafe tools

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: asyncio.TaskGroup Migration

**Files:**
- Modify: `gateway/run.py` (targeted changes)
- Test: `tests/gateway/test_taskgroup.py`

- [ ] **Step 1: Find asyncio.gather usage in gateway/run.py**

Run: `grep -n "asyncio.gather" gateway/run.py | head -10`
Expected: List of lines using asyncio.gather

- [ ] **Step 2: Create test for TaskGroup pattern**

Create `tests/gateway/test_taskgroup.py`:
```python
"""Tests for asyncio.TaskGroup patterns (Python 3.13+)."""
import pytest
import asyncio


class TestTaskGroupMigration:
    def test_taskgroup_works_like_gather(self):
        """TaskGroup should collect results like gather."""
        async def task(i):
            return i * 2

        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(task(1))
            t2 = tg.create_task(task(2))

        results = [t1.result(), t2.result()]
        assert results == [2, 4]

    def test_taskgroup_handles_exception(self):
        """TaskGroup should raise ExceptionGroup on errors."""
        async def bad_task():
            raise ValueError("test")

        with pytest.raises(ExceptionGroup):
            async with asyncio.TaskGroup() as tg:
                tg.create_task(bad_task())
```

- [ ] **Step 3: Run test to verify Python 3.13+ asyncio**

Run: `pytest tests/gateway/test_taskgroup.py -v`
Expected: PASS (Python 3.13 has TaskGroup)

- [ ] **Step 4: Identify simple gather usage to migrate**

Choose one `asyncio.gather` call in `gateway/run.py` that:
- Has simple error handling
- Doesn't need return_exceptions

Example pattern to find:
```python
results = await asyncio.gather(
    coro1(),
    coro2(),
)
```

- [ ] **Step 5: Migrate one gather to TaskGroup**

Replace:
```python
results = await asyncio.gather(
    self._handle_coro1(),
    self._handle_coro2(),
)
```

With:
```python
async with asyncio.TaskGroup() as tg:
    t1 = tg.create_task(self._handle_coro1())
    t2 = tg.create_task(self._handle_coro2())
results = [t1.result(), t2.result()]
```

- [ ] **Step 6: Verify gateway still runs**

Run: `timeout 15 uv run hermes gateway run --replace 2>&1 | head -20`
Expected: Gateway starting output, no errors

- [ ] **Step 7: Commit**

```bash
git add tests/gateway/test_taskgroup.py gateway/run.py
git commit -m "perf: migrate asyncio.gather to TaskGroup (Python 3.13)

TaskGroup provides better error handling and cancellation.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Tool Result Caching

**Files:**
- Modify: `tools/web_tools.py`
- Create: `tools/web_tools_cache.py`
- Test: `tests/tools/test_web_tools_cache.py`

- [ ] **Step 1: Read web_tools.py to find web_search**

Run: `grep -n "def web_search\|class.*WebSearch" tools/web_tools.py | head -5`
Expected: Function definition location

- [ ] **Step 2: Create cache decorator**

Create `tools/web_tools_cache.py`:
```python
"""Caching layer for expensive tool calls."""
import functools
import hashlib
import json
from typing import Any, Callable


def cache_tool_result(ttl_seconds: int = 300):
    """Decorator to cache tool results by arguments.

    Args:
        ttl_seconds: Time-to-live for cache entries (default 5 minutes)
    """
    def decorator(func: Callable) -> Callable:
        cache: dict[tuple, tuple[Any, float]] = {}  # (args_hash, ) -> (result, timestamp)

        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create hash of arguments
            key = json.dumps((args, sorted(kwargs.items())), sort_keys=True)
            args_hash = hashlib.sha256(key.encode()).hexdigest()[:16]

            import time
            current_time = time.time()

            # Check cache
            if args_hash in cache:
                result, timestamp = cache[args_hash]
                if current_time - timestamp < ttl_seconds:
                    return result

            # Call function and cache
            result = func(*args, **kwargs)
            cache[args_hash] = (result, current_time)
            return result

        # Expose cache for testing
        wrapper._cache = cache
        return wrapper

    return decorator


def clear_tool_cache(func: Callable) -> None:
    """Clear cache for a decorated function."""
    if hasattr(func, '_cache'):
        func._cache.clear()
```

- [ ] **Step 3: Create test for caching**

Create `tests/tools/test_web_tools_cache.py`:
```python
"""Tests for tool result caching."""
import pytest
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
        assert call_count == 1  # Only called once

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

        assert call_count == 2  # Called twice

    def test_cache_expires_after_ttl(self):
        """Cache should expire after TTL."""
        import time

        call_count = 0

        @cache_tool_result(ttl_seconds=1)
        def expensive_operation(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        expensive_operation(5)
        assert call_count == 1

        time.sleep(1.1)  # Wait for TTL to expire

        expensive_operation(5)
        assert call_count == 2  # Called again after TTL

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
        assert call_count == 2  # Called again after cache clear
```

- [ ] **Step 4: Run cache tests**

Run: `pytest tests/tools/test_web_tools_cache.py -v`
Expected: 4 PASS

- [ ] **Step 5: Apply cache to web_search**

Find web_search function signature in `tools/web_tools.py`:
```python
async def web_search(query: str, recency_days: int | None = None, ...) -> dict[str, Any]:
```

Add decorator above the function:
```python
from tools.web_tools_cache import cache_tool_result

@cache_tool_result(ttl_seconds=300)  # 5 minute cache
async def web_search(query: str, recency_days: int | None = None, ...) -> dict[str, Any]:
```

- [ ] **Step 6: Apply cache to web_extract**

Find web_extract function and add same decorator.

- [ ] **Step 7: Run web_tools tests**

Run: `pytest tests/tools/test_web_tools.py -v -k "web_search or web_extract" 2>&1 | head -30`
Expected: Tests pass (cached functions work same as before)

- [ ] **Step 8: Commit**

```bash
git add tools/web_tools_cache.py tests/tools/test_web_tools_cache.py tools/web_tools.py
git commit -m "perf: add tool result caching for web_search and web_extract

- 5-minute TTL cache reduces API calls for repeated queries
- Cache key based on function arguments hash
- clear_tool_cache() for testing

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: Verify All Optimizations

**Files:**
- None (verification only)

- [ ] **Step 1: Verify Python version**

Run: `python --version`
Expected: Python 3.13.x

- [ ] **Step 2: Verify HERMES_TOOL_DELAY=0.0**

Run: `grep HERMES_TOOL_DELAY ~/.hermes/.env`
Expected: `HERMES_TOOL_DELAY=0.0`

- [ ] **Step 3: Run all tests**

Run: `pytest tests/run_agent/test_parallel_tool_execution.py tests/tools/test_web_tools_cache.py -v`
Expected: All pass

- [ ] **Step 4: Start gateway and verify no errors**

Run: `timeout 20 uv run hermes gateway run --replace 2>&1 | grep -iE "error|exception" || echo "No errors"`
Expected: "No errors" or gateway starting output without errors

- [ ] **Step 5: Commit final verification**

```bash
git add -A
git commit -m "perf: verify all optimizations integrated

- Python 3.13 baseline (~5-15% speedup)
- HERMES_TOOL_DELAY=0.0 (zero latency between tools)
- Parallel execution for _PARALLEL_SAFE_TOOLS
- asyncio.TaskGroup migration started
- Tool result caching (5-min TTL)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

- [ ] All tasks have specific file paths and line numbers
- [ ] All code steps include actual code (not pseudocode)
- [ ] All test steps include actual test code
- [ ] All run commands show expected output
- [ ] No "TODO", "TBD", or placeholder content
- [ ] Each task is independently testable
- [ ] Type consistency checked across tasks
- [ ] Commit messages follow conventional format

---

## Execution Options

**1. Subagent-Driven (recommended)** - Dispatch fresh subagent per task, two-stage review

**2. Inline Execution** - Execute tasks in this session using executing-plans skill

Which approach?
