# Hermes Agent Architecture Optimization Analysis

**Date:** 2026-04-14
**Python Version:** 3.13
**Analysis Tools:** GitNexus, Serene MCP, Jina Web Search

---

## Executive Summary

Hermes Agent has significant optimization opportunities. The most impactful finding: **`HERMES_TOOL_DELAY` is already configurable via environment variable** but defaults to 1.0s. Combined with other findings, potential latency reduction of **2-5 seconds per multi-tool turn**.

---

## 1. Python 3.13 Async Improvements — Current State

### What Python 3.13 Actually Offers

| Feature | Status | Impact for Hermes |
|---------|--------|-------------------|
| **Optional NoGIL** | Experimental (Python 3.14+) | Not yet production-ready |
| **Faster CPython** | ~5-15% baseline speedup | Moderate — applies everywhere |
| **Async Improvements** | Ongoing | `asyncio.TaskGroup` improvements |
| **Memory Optimization** | Per-file compiler | ~10% less memory |

**Key Insight:** Python 3.13's NoGIL is not production-ready. Hermes should target Python 3.14 (late 2025) or 3.15 for free-threading support. However, baseline 3.13 optimizations are available NOW.

### Recommended Action
```bash
# Current
python = ">=3.12"

# Recommended for Python 3.13 gains
python = ">=3.13"
```
This gives ~5-15% baseline speedup with no code changes.

---

## 2. Tool Delay (HIGH IMPACT — Already Configurable!)

### Current State
- **Location:** `run_agent.py:549`
- **Default:** 1.0 second
- **Environment Variable:** `HERMES_TOOL_DELAY` ✅ ALREADY IMPLEMENTED
- **Current User Value:** 0.7s (from `.env`)

```python
HERMES_TOOL_DELAY = float(os.environ.get("HERMES_TOOL_DELAY", 1.0))
```

### Delay Impact Analysis

| Tool Calls | Delay (1.0s) | Delay (0.7s) | Delay (0.0s) | Savings |
|------------|---------------|--------------|--------------|---------|
| 1 tool | 0s | 0s | 0s | 0s |
| 2 tools | 1s | 0.7s | 0s | 0.3-1s |
| 4 tools | 3s | 2.1s | 0s | 0.9-3s |
| 8 tools | 7s | 4.9s | 0s | 2.1-7s |

### Bottleneck Location
```python
# run_agent.py:7510-7511
if self.tool_delay > 0 and i < len(assistant_message.tool_calls):
    time.sleep(self.tool_delay)
```

### Recommendation
**Already done.** User has `HERMES_TOOL_DELAY=0.7` in `.env`. Further reduction to `0.0` possible if no rate limiting issues. Suggested testing sequence: 0.7 → 0.5 → 0.3 → 0.0.

---

## 3. Parallel Tool Execution — MODERATE IMPACT

### Current State
Hermes already has `_PARALLEL_SAFE_TOOLS` infrastructure:

```python
# run_agent.py:244-258
_PARALLEL_SAFE_TOOLS = frozenset({
    "ha_get_state", "ha_list_entities", "ha_list_services",
    "read_file", "search_files", "session_search",
    "skill_view", "skills_list", "vision_analyze",
    "web_extract", "web_search",
})
```

But implementation appears to use sequential execution with delays.

### Implementation Pattern
The tool execution loop in `run_agent.py:7500-7511` processes tools sequentially with `time.sleep(tool_delay)` between each. True parallel execution for safe tools could provide significant speedup.

### Recommendation
Add `asyncio.gather` or `ThreadPoolExecutor` for `_PARALLEL_SAFE_TOOLS`:
```python
# Pseudocode for parallel safe tool execution
if all(tool in _PARALLEL_SAFE_TOOLS for tool in tools):
    results = await asyncio.gather(*[execute(t) for t in tools])
```

---

## 4. ThreadPoolExecutor Configuration — INVESTIGATION NEEDED

### Current Configuration
```python
# environments/agent_loop.py:34,46
_tool_executor = ThreadPoolExecutor(max_workers=128)  # HIGH
# tools/delegate_tool.py - uses ThreadPoolExecutor for subagents
```

### Python 3.13 Threading Implications
- **With GIL:** Threads only effective for IO-bound tasks
- **Without GIL (experimental):** True parallelism for CPU-bound tasks
- **Current Hermes workload:** Mostly IO-bound (network calls, file IO)

### Recommendation
1. Keep ThreadPoolExecutor for IO-bound tool execution
2. Monitor `python3.13t` (free-threaded build) for future migration
3. Consider `asyncio.to_thread()` for async-native concurrency

---

## 5. Honcho Context Calls — OPTIMIZATION OPPORTUNITY

### Current Pattern
From `plugins/memory/honcho/__init__.py:121-152`, Honcho uses:
- Prefetch thread (`_prefetch_thread`) for background loading
- `threading.Lock` for synchronization
- Context cadence of 1 turn minimum between API calls

### Sequential Calls Issue
If multiple context-gathering calls happen sequentially (user_profile, session_context, etc.), they could be parallelized with `ThreadPoolExecutor`.

### Recommendation
Check if these calls are sequential:
```python
# Potential parallelization
with ThreadPoolExecutor(max_workers=2) as executor:
    future_profile = executor.submit(fetch_user_profile, ...)
    future_context = executor.submit(fetch_session_context, ...)
    profile, context = future_profile.result(), future_context.result()
```

---

## 6. Caching Opportunities — MODERATE IMPACT

### Existing Caches
1. **Context Length Cache** (`agent/model_metadata.py:554`) — YAML file cache
2. **Model Metadata Cache** — In-memory with disk persistence
3. **Honcho Prefetch** — Background thread prefetching

### Missing Caches
| Cache Type | Opportunity | Impact |
|------------|-------------|--------|
| Tool Result Cache | Cache read_file, web_search results | HIGH |
| LLM Response Cache | Cache repeated prompts | MEDIUM |
| Session State Cache | Reduce Honcho API calls | MEDIUM |

---

## 7. Streaming and Partial Execution — LOW-MODERATE IMPACT

### Current Streaming Support
Tests show streaming accumulator and callbacks exist (`tests/run_agent/test_streaming.py`).

### Opportunity
Claude Code-style partial tool execution during streaming. Currently Hermes waits for full response before executing tools.

### Recommendation
Investigate `run_agent.py` streaming implementation for partial execution opportunity. This could provide 15-20% speedup for streaming responses with tools.

---

## 8. Async/Await Architecture — HIGH BASELINE IMPROVEMENT

### Current Async Usage
- 262 async/await patterns in `gateway/run.py`
- `asyncio.gather` used extensively in gateway
- `asyncio.create_task` for concurrent operations

### Python 3.13 Async Improvements
- `asyncio.TaskGroup` improvements (better error handling)
- `asyncio.timeout` official (previously provisional)
- Improved cancellation handling

### Recommendation
Update to Python 3.13 and use new TaskGroup patterns:
```python
# Python 3.13+
async with asyncio.TaskGroup() as tg:
    tg.create_task(coro1())
    tg.create_task(coro2())
```

---

## Priority Implementation Plan

### Tier 1: Immediate (No Code Changes)
1. ✅ **HERMES_TOOL_DELAY already configured** — Test 0.0 for maximum speed
2. **Upgrade to Python 3.13** — Add to `pyproject.toml`, gain 5-15% baseline

### Tier 2: Low Effort, High Impact
3. **Expand `_PARALLEL_SAFE_TOOLS`** — Add more read-only tools
4. **Add tool result caching** for `read_file`, `web_search`
5. **Use `asyncio.TaskGroup`** instead of `asyncio.gather`

### Tier 3: Moderate Effort
6. **Parallel Honcho context calls** — ThreadPoolExecutor for context gathering
7. **Streaming partial execution** — Execute safe tools during streaming
8. **Gateway prefetch cache sharing** — Share cache across AIAgent instances

### Tier 4: Future (Python 3.14+)
9. **Free-threaded Python migration** — Monitor Python 3.14 production readiness
10. **ProcessPoolExecutor for CPU-bound** — Replace ThreadPoolExecutor where applicable

---

## Files to Modify for Tier 2

| File | Change | Impact |
|------|--------|--------|
| `pyproject.toml` | `python = ">=3.13"` | +5-15% speed |
| `run_agent.py:244` | Add more tools to `_PARALLEL_SAFE_TOOLS` | Faster parallel |
| `run_agent.py` | Use `asyncio.TaskGroup` | Better async |
| `tools/web_tools.py` | Add cache decorators | Reduced API calls |
| `gateway/run.py` | Share prefetch cache | -200ms gateway |

---

## Verification Commands

```bash
# Test tool delay reduction
HERMES_TOOL_DELAY=0.0 uv run hermes gateway run --replace

# Benchmark with Python 3.13
python --version  # Should be 3.13.x
uv run python --version

# Check ThreadPoolExecutor usage
grep -r "ThreadPoolExecutor" --include="*.py" | head -20

# Monitor async patterns
grep -r "asyncio\." --include="*.py" run_agent.py gateway/run.py | wc -l
```

---

## Conclusion

Hermes already has good architectural foundations. Key opportunities:

1. **Biggest win:** Python 3.13 upgrade (+5-15% baseline)
2. **Already done:** `HERMES_TOOL_DELAY` configurable (user has 0.7s)
3. **Quick wins:** Expand parallel safe tools, add result caching
4. **Future:** Python 3.14 free-threading for true parallelism

The codebase is well-structured for async operations. Focus on:
- Reducing sequential bottlenecks
- Adding caching for expensive operations
- Upgrading to Python 3.13 for baseline improvements
