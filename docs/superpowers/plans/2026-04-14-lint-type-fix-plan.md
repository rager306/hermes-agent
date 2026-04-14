# Hermes Agent Lint & Type Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix all linting (Ruff) and type checking (Pyrefly, Ty) errors in the codebase through systematic, prioritized approach.

**Architecture:** Three-phase approach: (1) Ruff auto-fix + manual fixes, (2) Pyrefly false-positive suppression + real bug fixes, (3) Ty None-check fixes + type annotations.

**Tech Stack:** ruff, pyrefly, ty, mcp serena, gitnexus

---

## Scope

This plan covers ALL linting and type errors across the entire codebase:

| Linter | Total Errors | Auto-fix | Manual | Priority |
|--------|-------------|----------|--------|----------|
| Ruff | 409 | ~370 (90%) | ~39 | HIGH |
| Pyrefly | 3,549 | 0 | 3,549 | MEDIUM |
| Ty | 2,970 | 0 | 2,970 | HIGH |

---

## Error Summary by Category

### Ruff (409 errors)
| Code | Count | Type | Fix |
|------|-------|------|-----|
| RUF001 | 175 | Ambiguous chars in strings | auto-fix |
| RUF002 | 50 | Ambiguous chars in docstrings | auto-fix |
| F401 | 49 | Unused imports | auto-fix |
| RUF003 | 22 | Ambiguous chars in comments | auto-fix |
| UP035 | 24 | Deprecated typing imports | auto-fix |
| RUF012 | 38 | Mutable class attributes | manual |
| B027 | 15 | Empty abstract methods | manual |
| RUF006 | 12 | asyncio.create_task not stored | manual |
| RUF043 | 8 | pytest.raises non-raw regex | auto-fix |
| Other | 16 | Various | mixed |

### Pyrefly (3,549 errors)
| Type | Count | Fix |
|------|-------|-----|
| missing-import | 516 | Install deps |
| missing-attribute | 1,342 | False positives (conditional imports) |
| bad-argument-type | 566 | Real type bugs |
| unsupported-operation | 258 | None checks |
| bad-assignment | 192 | Type narrowing |
| not-iterable | 151 | None checks |
| bad-index | 126 | Type fixes |
| bad-override | 59 | Signature alignment |
| Other | 173 | Various |

### Ty (2,970 errors)
| Type | Count | Fix |
|------|-------|-----|
| unresolved-attribute | 950 | None checks |
| invalid-argument-type | 842 | Handle str\|None |
| invalid-assignment | 421 | Type narrowing |
| unresolved-import | 230 | Install deps |
| not-subscriptable | 169 | Fix type inference |
| unsupported-operator | 108 | Type narrowing |
| call-non-callable | 72 | Fix typing.Any |
| no-matching-overload | 59 | Fix signatures |
| Other | 120 | Various |

---

## Task 1: Ruff Auto-Fix + ClassVar Fixes

**Files:**
- Modify: `agent/display.py` (ClassVar)
- Modify: `acp_adapter/server.py` (ClassVar)
- Modify: `gateway/run.py` (ClassVar)
- Modify: `run_agent.py` (ClassVar)

- [ ] **Step 1: Run ruff auto-fix**

Run: `uv run ruff check . --fix 2>&1 | tail -20`
Expected: ~328 errors fixed, ~39 remaining

- [ ] **Step 2: Verify auto-fix results**

Run: `uv run ruff check . 2>&1 | grep -E "RUF001|RUF002|RUF003|F401|UP035|RUF043" | wc -l`
Expected: 0 (all auto-fixed)

- [ ] **Step 3: Fix RUF012 - Mutable class attributes (ClassVar)**

Run: `uv run ruff check . 2>&1 | grep "RUF012"`
Expected: List of files with RUF012 errors

For each file, add `ClassVar` annotation:

**agent/display.py:**
```python
# Before
_SPINNERS = [...]
KAWAII_WAITING = [...]

# After
from typing import ClassVar
_SPINNERS: ClassVar[list] = [...]
KAWAII_WAITING: ClassVar[list] = [...]
```

**acp_adapter/server.py:96:**
```python
# Before
_SLASH_COMMANDS = {...}

# After
_SLASH_COMMANDS: ClassVar[dict[str, str]] = {...}
```

- [ ] **Step 4: Fix RUF006 - asyncio.create_task not stored**

Run: `uv run ruff check . 2>&1 | grep "RUF006"`
Expected: List of files with RUF006 errors

For each location, either store the task or add `# type: ignore`:
```python
# If task needs tracking:
task = asyncio.create_task(self._session_expiry_watcher())
self._background_tasks.add(task)

# If intentional fire-and-forget, add:
asyncio.create_task(...)  # type: ignore
```

- [ ] **Step 5: Verify ruff passes for modified files**

Run: `uv run ruff check agent/display.py acp_adapter/server.py gateway/run.py run_agent.py 2>&1`
Expected: 0 errors

- [ ] **Step 6: Commit**

```bash
git add -A
git commit -m "fix: resolve Ruff RUF012 ClassVar and RUF006 asyncio issues

- Add ClassVar annotations to mutable class defaults
- Store asyncio.create_task references where needed
- Auto-fix all RUF001/002/003/UP035/F401/RUF043 errors

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 2: B027 - Add @abstractmethod Decorators

**Files:**
- Modify: `agent/memory_provider.py` (8 methods)
- Modify: `gateway/platforms/base.py` (4 methods)
- Modify: `agent/context_engine.py` (2 methods)

- [ ] **Step 1: Find all B027 errors**

Run: `uv run ruff check . 2>&1 | grep "B027"`
Expected: List of empty abstract methods

- [ ] **Step 2: Add @abstractmethod to agent/memory_provider.py**

Read the file and add `@abstractmethod` to these methods:
- `queue_prefetch`
- `sync_turn`
- `shutdown`
- `on_turn_start`
- `on_session_end`
- `on_delegation`
- `save_config`
- `on_memory_write`

```python
# Before
def on_session_start(self, session_id: str, **kwargs) -> None:
    """Called when a new conversation session begins."""
    pass

# After
@abstractmethod
def on_session_start(self, session_id: str, **kwargs) -> None:
    """Called when a new conversation session begins."""
    pass
```

- [ ] **Step 3: Add @abstractmethod to gateway/platforms/base.py**

Read the file and add `@abstractmethod` to:
- `send_typing`
- `stop_typing`
- `on_processing_start`
- `on_processing_complete`

- [ ] **Step 4: Add @abstractmethod to agent/context_engine.py**

Add to `on_session_start` and `on_session_end`

- [ ] **Step 5: Verify B027 fixed**

Run: `uv run ruff check agent/memory_provider.py gateway/platforms/base.py agent/context_engine.py 2>&1`
Expected: 0 B027 errors

- [ ] **Step 6: Commit**

```bash
git add agent/memory_provider.py gateway/platforms/base.py agent/context_engine.py
git commit -m "fix: add @abstractmethod to empty abstract methods (B027)

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 3: Pyrefly - Install Missing Dependencies + Suppress False Positives

**Files:**
- Modify: `pyproject.toml` (add deps)
- Modify: `gateway/platforms/discord.py` (type: ignore)
- Modify: `gateway/platforms/telegram.py` (type: ignore)
- Modify: `gateway/platforms/api_server.py` (type: ignore)

- [ ] **Step 1: Install missing test dependencies**

Run: `uv sync --extra dev 2>&1 | tail -5`
Expected: pytest, pytest-asyncio, pytest-xdist installed

- [ ] **Step 2: Verify pytest import errors resolved**

Run: `uv run pyrefly check . 2>&1 | grep "missing-import.*pytest" | wc -l`
Expected: 0

- [ ] **Step 3: Add type: ignore for conditional import false positives**

For files with many `missing-attribute` on `NoneType` from conditional imports:

```python
# gateway/platforms/discord.py - add at top of conditional import block
try:
    import discord
    from discord import opus
except ImportError:
    discord = None  # type: ignore[assignment,assignment]
    opus = None  # type: ignore[assignment,assignment]
```

Run: `uv run pyrefly check gateway/platforms/discord.py 2>&1 | grep "missing-attribute" | wc -l`
Expected: Should decrease significantly

- [ ] **Step 4: Commit**

```bash
git add -A
git commit -m "fix(pyrefly): install missing deps and suppress conditional import false positives

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 4: Pyrefly - Fix Real Type Bugs (bad-argument-type, bad-override)

**Files:**
- Modify: `agent/anthropic_adapter.py` (TypedDict keys)
- Modify: `optional-skills/rl/**/agentic_opd_env.py` (method overrides)
- Modify: `agent/auxiliary_client.py` (type fixes)

- [ ] **Step 1: Find bad-typed-dict-key errors**

Run: `uv run pyrefly check . 2>&1 | grep "bad-typed-dict-key"`
Expected: List of TypedDict key errors in anthropic_adapter.py

- [ ] **Step 2: Fix TypedDict keys in anthropic_adapter.py**

Read `agent/anthropic_adapter.py` around lines 260-296 and fix TypedDict key types.

- [ ] **Step 3: Find bad-override errors**

Run: `uv run pyrefly check . 2>&1 | grep "bad-override" | head -20`
Expected: List of method signature mismatches

- [ ] **Step 4: Fix method overrides in optional-skills**

Read and align method signatures with parent classes.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "fix(pyrefly): resolve TypedDict key and method override errors

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 5: Ty - Fix None Checks (unresolved-attribute, invalid-assignment)

**Files:**
- Modify: `cli.py` (many None checks)
- Modify: `run_agent.py` (72 errors)
- Modify: `agent/auxiliary_client.py` (54+ errors)
- Modify: `gateway/platforms/discord.py` (Interaction=None)

- [ ] **Step 1: Find top files by unresolved-attribute count**

Run: `uv run ty check . 2>&1 | grep "unresolved-attribute" | awk -F: '{print $1}' | sort | uniq -c | sort -rn | head -10`
Expected: List of files with most None attribute errors

- [ ] **Step 2: Fix cli.py os.getenv / runtime.get None handling**

```python
# Before
api_key = runtime.get("api_key")  # returns str|None

# After
api_key = runtime.get("api_key") or ""  # or: runtime.get("api_key", "")
```

Run: `uv run ty check cli.py 2>&1 | grep "invalid-argument-type" | head -10`

- [ ] **Step 3: Fix agent/auxiliary_client.py None handling**

Read the file and add None guards for dict.get() calls.

- [ ] **Step 4: Verify improvements**

Run: `uv run ty check cli.py run_agent.py 2>&1 | grep -E "invalid-argument-type|unresolved-attribute" | wc -l`
Expected: Significantly reduced from baseline

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "fix(ty): resolve None check errors in cli and aux_client

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Task 6: Final Verification

- [ ] **Step 1: Run full ruff check**

Run: `uv run ruff check . 2>&1`
Expected: 0 errors

- [ ] **Step 2: Run full pyrefly check (baseline comparison)**

Run: `uv run pyrefly check . 2>&1 | grep "error" | wc -l`
Expected: Significantly reduced from 3,549

- [ ] **Step 3: Run full ty check (baseline comparison)**

Run: `uv run ty check . 2>&1 | grep "error" | wc -l`
Expected: Significantly reduced from 2,970

- [ ] **Step 4: Run test suite**

Run: `uv run pytest tests/ -x -q 2>&1 | tail -20`
Expected: All tests pass

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "fix: complete lint and type error resolution

Phase 1: Ruff auto-fix + manual (ClassVar, abstract methods)
Phase 2: Pyrefly deps + false positive suppression
Phase 3: Ty None check improvements

Ruff: 409 -> 0
Pyrefly: reduced by ~60%
Ty: reduced by ~50%

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>"
```

---

## Self-Review Checklist

- [ ] All tasks have specific file paths and line numbers
- [ ] All code steps include actual code patterns
- [ ] All run commands show expected output
- [ ] No "TODO", "TBD", or placeholder content
- [ ] Each task is independently testable
- [ ] Commit messages follow conventional format

---

## Execution Options

**1. Subagent-Driven (recommended)** - Dispatch fresh subagent per task, two-stage review

**2. Inline Execution** - Execute tasks in this session using executing-plans skill

Which approach?
