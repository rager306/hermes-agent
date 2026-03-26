# CONCERNS.md — Technical Debt, Known Issues, and Fragile Areas

## Overview

This document catalogs technical debt, known issues, security concerns, performance problems, and fragile architectural areas in the Hermes Agent codebase.

---

## 1. Known Issues (Documented in Tests)

### 1.1 Context Overflow Loop (#1630)
**Location:** `tests/test_1630_context_overflow_loop.py`

Gateway can enter an infinite 400 failure loop when:
- Large session triggers generic 400 error
- Error is not properly identified as context-length issue
- Session grows on each failure (messages persisted incorrectly)

**Mitigation:** Tests verify that generic 400 with large sessions triggers compression instead of aborting.

### 1.2 Agent Guardrails (PR #1321)
**Location:** `tests/test_agent_guardrails.py`

Three guardrail mechanisms were added to prevent problematic agent behavior:
1. **`_sanitize_api_messages()`** — Repairs orphaned tool call/result pairs
2. **`_cap_delegate_task_calls()`** — Limits subagent concurrency (MAX_CONCURRENT_CHILDREN)
3. **`_deduplicate_tool_calls()`** — Removes identical tool call duplicates

### 1.3 Anthropic API Error Handling
**Location:** `tests/test_anthropic_error_handling.py`

Error handling matrix for `run_conversation()` with `api_mode=anthropic_messages`:
- **429** → Retry with backoff (rate limit)
- **529** → Retry with backoff (overloaded)
- **400** → Non-retryable, immediate fail
- **401** → Credential refresh + retry
- **500** → Retry with backoff
- **"prompt is too long"** → Triggers context compression

### 1.4 SQL Injection Prevention
**Location:** `tests/test_sql_injection.py`, `agent/insights.py`

SQL injection mitigations are tested and in place:
- Column names must be safe identifiers (no `;`, `--`, `'`, `DROP`)
- Queries use parameterized placeholders (`?`)
- No brace interpolation in SQL

---

## 2. Technical Debt

### 2.1 Deprecated Configuration Options
**Location:** `hermes_cli/config.py` (lines 894-906)

```python
# HERMES_TOOL_PROGRESS and HERMES_TOOL_PROGRESS_MODE are deprecated —
# Use display.tool_progress in config.yaml instead
```

These deprecated options still exist in the codebase but should be migrated.

### 2.2 Large CLI Module
**Location:** `hermes_cli/`

The `hermes_cli` module has grown to 30+ files with overlapping responsibilities:
- `gateway.py` — 1800+ lines, handles gateway lifecycle, systemd/launchd service management
- `main.py` — 3300+ lines, monolithic command routing
- `setup.py` — 2400+ lines, installation logic
- `auth.py` — 2200+ lines, multi-provider authentication

**Concern:** High coupling, difficult to test, God classes.

### 2.3 Parallel Tool Execution Complexity
**Location:** `run_agent.py`, `tools/registry.py`

Multiple parallelization mechanisms with complex interactions:
- `_PARALLEL_SAFE_TOOLS` — whitelist of tools safe to parallelize
- `_NEVER_PARALLEL_TOOLS` — blacklist
- `_MAX_TOOL_WORKERS` — worker thread limit
- `_should_parallelize_tool_batch()` — complex decision logic

**Risk:** Race conditions in tool result aggregation.

### 2.4 Worktree Management
**Location:** `run_agent.py` (worktree functions)

Git worktree creation/cleanup has multiple failure modes:
- `_setup_worktree()` — creates isolated worktree
- `_cleanup_worktree()` — cleanup on exit
- `_prune_stale_worktrees()` — background cleanup

**Risk:** Orphaned worktrees on crashes, cleanup thread safety.

---

## 3. Security Concerns

### 3.1 Extensive Subprocess Usage
**Location:** Throughout `hermes_cli/`

Heavy use of `subprocess.run()` with external commands:
- 300+ `subprocess.run()` calls across hermes_cli
- Various timeout values (3s to 300s)
- Multiple privilege escalation patterns (sudo, systemctl)

**Mitigations in place:**
- No `shell=True` usage found (verified)
- `_is_destructive_command()` pattern matching
- DANGEROUS_PATTERNS in `approval.py`

**Residual risk:** Complex command construction could bypass pattern matching.

### 3.2 Command Approval System
**Location:** `tools/approval.py`

Pattern-based dangerous command detection:
```python
DANGEROUS_PATTERNS = [...]
_pattern_key_aliases = {...}
```

**Risk:** Pattern matching can be circumvented with obfuscation.

### 3.3 Tirith Security Tool
**Location:** `tools/tirith_security.py`

Binary verification with cosign:
- Downloads security tool binary
- Verifies with cosign signature
- Falls back on failure

**Risk:** `_INSTALL_FAILED` marker could prevent tool installation recovery.

### 3.4 Credential Handling
**Location:** `hermes_cli/auth.py`

Multiple OAuth flows with token refresh:
- `_auth_store_lock()` with 15s timeout
- Token caching mechanisms
- Environment variable expansion in credentials

**Risk:** Race conditions in concurrent token refresh.

---

## 4. Performance Concerns

### 4.1 Context Compression Complexity
**Location:** `agent/context_compressor.py`

Context compression has multiple thresholds and ratios:
```python
CONTEXT_TRUNCATE_HEAD_RATIO = 0.1  # 10% from head
CONTEXT_TRUNCATE_TAIL_RATIO = 0.1  # 10% from tail
SUMMARY_TOKENS_CEILING = 2000
```

**Risk:** Compression may lose important context, especially in long sessions.

### 4.2 Session Search Performance
**Location:** `hermes_state.py`, `agent/insights.py`

SQLite-based session storage with FTS (Full-Text Search):
- `_GET_SESSIONS_ALL` with parameterized queries
- Session context hashing (`_hash_id`, `_hash_sender_id`, `_hash_chat_id`)
- Insights aggregation queries

**Risk:** Large session databases may have query performance issues.

### 4.3 Terminal Environment Management
**Location:** `tools/terminal_tool.py`

Per-task environment creation with cleanup:
- `_active_environments` dict tracking active environments
- Cleanup thread with `_cleanup_running` flag
- Disk usage warnings (DISK_USAGE_WARNING_THRESHOLD_GB = 50)

**Risk:** Environment leaks on abnormal exit.

### 4.4 MCP Server Connection Management
**Location:** `hermes_cli/mcp_config.py`

MCP server lifecycle:
- `connect_timeout` defaults to 30s
- `timeout=connect_timeout + 10` for probe
- Connection pooling per server

**Risk:** Zombie MCP servers on connection failures.

---

## 5. Async and Concurrency Issues

### 5.1 Mixed Async Patterns
**Location:** Throughout codebase

Multiple async paradigms in use:
- `asyncio.run()` in `gateway.py:990`
- `threading.Thread()` for background tasks (banner update check, cleanup threads)
- Thread-local storage (`threading.local()` for `_auth_lock_holder`)

**Risk:** Event loop nesting issues, deadlock potential.

### 5.2 Thread-Safe Logger Usage
**Location:** Multiple files

Logger is accessed from multiple threads:
```python
Variable: [logger]  # Shared across all threads
```

**Risk:** Log messages may interleave or be corrupted.

### 5.3 Global State in model_tools.py
**Location:** `model_tools.py`

Global tool loop management:
```python
Variable: [_tool_loop, _tool_loop_lock, _worker_thread_local]
```

**Risk:** State leakage between agent iterations.

---

## 6. Error Handling Fragility

### 6.1 Broad Exception Catches
**Location:** Throughout codebase

Several locations catch broad exceptions:
- `except Exception:` patterns in various tools
- `except subprocess.CalledProcessError` with limited error context

**Risk:** Silent failures, masked bugs.

### 6.2 Missing Error Context
**Location:** Various tools

Error handling often lacks context:
- Generic error messages don't include file paths or input parameters
- Stack traces may be incomplete in async contexts

### 6.3 Retry Logic Complexity
**Location:** `run_agent.py`, `agent/anthropic_adapter.py`

Multiple retry mechanisms:
- Rate limit backoff
- Credential refresh retry
- Context compression retry

**Risk:** Retry storms on transient failures.

---

## 7. Resource Management

### 7.1 File Handle Leaks
**Location:** Various

Many file operations may not properly close handles:
- `Path.read_text()` / `Path.write_text()`
- JSON/YAML file operations

**Mitigation:** `utils.py` has `atomic_json_write()` and `atomic_yaml_write()`.

### 7.2 Image Cache Management
**Location:** `tools/vision_tools.py`, `tools/image_generation_tool.py`

Image processing creates temporary files:
- Base64 image cleanup
- Generated image cache

**Risk:** Disk space exhaustion with large images.

### 7.3 Background Thread Cleanup
**Location:** `tools/terminal_tool.py`

Cleanup thread pattern:
```python
_cleanup_thread = None
_cleanup_running = False
```

**Risk:** Threads may not exit cleanly on interpreter shutdown.

---

## 8. Testing Gaps

### 8.1 No Test for Worktree Race Conditions
**Location:** `tests/test_worktree.py`

Tests exist for worktree security but not for:
- Concurrent worktree creation
- Stale worktree cleanup during active use

### 8.2 No Integration Tests for Gateway Platforms
**Location:** `gateway/platforms/`

Each platform (Slack, Discord, Telegram, etc.) lacks integration tests:
- Message delivery under load
- Authentication refresh
- Rate limiting

### 8.3 MCP Tool Test Coverage
**Location:** `tests/acp/`

Limited MCP-specific test coverage for:
- Tool call streaming
- Partial tool result handling
- MCP server restart scenarios

---

## 9. Deprecated API Surface

### 9.1 Legacy Toolset Mapping
**Location:** `toolsets.py`

```python
_LEGACY_TOOLSET_MAP = {...}  # Deprecated toolset names
```

Old toolset names still work but generate warnings.

### 9.2 Environment Variable Expansion
**Location:** `hermes_cli/config.py`

Complex env var expansion in config:
- `_expand_env_vars()` handles nested expansions
- Multiple env var sources (`.env`, system env, config)

**Risk:** Secrets may leak into logs via expansion errors.

---

## 10. Third-Party Dependencies

### 10.1 Unpinned Dependencies
**Location:** `pyproject.toml`, `requirements.txt`

Several optional dependencies may have unpinned transitive deps:
- Browser automation tools
- Cloud provider SDKs
- Authentication library fallbacks

### 10.2 Cosign Binary Verification
**Location:** `tools/tirith_security.py`

Binary verification depends on external cosign tool:
- `_COSIGN_IDENTITY_REGEXP`
- `_COSIGN_ISSUER`

**Risk:** cosign tool availability or version changes break security.

---

## Summary Priority Matrix

| Area | Severity | Effort | Notes |
|------|----------|--------|-------|
| Deprecated config options | Low | Low | Legacy compat, easy removal |
| Subprocess security | Medium | Ongoing | Pattern matching gaps |
| Async/concurrency | Medium | High | Requires architectural review |
| Context compression | Medium | Medium | Algorithm improvements needed |
| Thread cleanup | Low | Medium | Graceful shutdown issues |
| Worktree race conditions | Medium | High | Needs dedicated test suite |
| Gateway platform tests | Low | High | Manual testing acceptable |

---

## Recommendations

1. **Immediate**: Add integration tests for worktree race conditions
2. **Short-term**: Deprecate and remove HERMES_TOOL_PROGRESS* options
3. **Medium-term**: Extract gateway.py into separate module package
4. **Long-term**: Migrate to async/await pattern consistently, remove threading for async operations
5. **Ongoing**: Add platform integration tests for message delivery
