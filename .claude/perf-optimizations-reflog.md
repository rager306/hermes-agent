# Perf Optimizations — Preserved Commits (reflog)

These commits exist in reflog, recoverable for ~90 days after creation.
Run `git reflog` to find them.

## Key Perf Commits (Apr 14-15 2026)

| SHA | Description |
|-----|-------------|
| 7ea178fc | feat: add ruff and ty linters to dev dependencies |
| 83225456 | perf: verify all optimizations integrated |
| 5d8dd841 | perf: add tool result caching for web_search_tool |
| 07bbeced | perf: add asyncio.TaskGroup test for Python 3.13 |
| 8ec60053 | perf: add _is_tool_parallel_safe function and tests |
| 321ec29e | perf: set HERMES_TOOL_DELAY=0.0 for zero-latency tool execution |
| 3a7fd27c | docs: add performance optimization implementation plan |
| df4049b6 | docs: add architecture optimization analysis for Python 3.13 |

## To Restore

```bash
# Check reflog
git reflog --date=relative | grep -E "perf|ty|ruff"

# Cherry-pick specific commit
git cherry-pick <sha>
```

## Key Changes Summary

1. **tool_delay env var** — HERMES_TOOL_DELAY=0.0 for zero-latency
2. **web_search_tool caching** — cache_tool_result() in web_tools_cache.py
3. **_is_tool_parallel_safe()** — parallel execution safety check
4. **asyncio.TaskGroup** — concurrent task handling
5. **ruff/ty/pyrefly linters** — code quality tools in dev deps
