# Linting Analysis Report - Hermes Agent

**Date:** 2026-04-14
**Python:** 3.13
**Tools:** ruff 0.x, pyrefly (Astral)

---

## Executive Summary

| Tool | Errors | Warnings | Fixable | Notes |
|------|--------|----------|---------|-------|
| ruff | 11,011 | 0 | 10,204 (93%) | E,W,F,I,B,C4,UP,RUF rules |
| ty | 3,931 | 0 | N/A | Type checker (Astral) |
| pyrefly | 4,124 | 0 | N/A | Type checker (Astral) |

### Overall Assessment

**HIGH VOLUME, LOW CRITICALITY.** The majority of errors are:
- Style/formatting (W293 blank lines, I001 import order) — **auto-fixable**
- Type annotation modernization (UP007 Union → |) — **auto-fixable**
- Missing type stubs for third-party modules — **noise, not bugs**

**No critical security vulnerabilities detected.** Minor security notes documented below.

---

## ruff Analysis

### Top Error Codes

| Code | Count | Category | Severity | Action |
|------|-------|----------|----------|--------|
| W293 | 3,006 | Blank line contains whitespace | LOW | `--fix` |
| P006 | 2,310 | `pass` in except clause | LOW | Manual review |
| P045 | 1,605 | `pass` in except clause (2nd) | LOW | Manual review |
| I001 | 1,090 | Import block unsorted | LOW | `--fix` |
| F401 | 849 | Unused import | LOW | `--fix` |
| F841 | 124 | Unused variable | LOW | `--fix` |
| E402 | 182 | Import not at top | LOW | Ignore/accept |
| W291 | 65 | Trailing whitespace | LOW | `--fix` |
| F005 | 79 | Unused binding | LOW | Manual review |

### Auto-fixable Issues (10,204 / 93%)

```bash
uvx ruff check . --fix --unsafe-fixes
```

**Note:** `--unsafe-fixes` enables auto-fix for rules that may change semantics.

### Files with Most Issues

| File | Errors |
|------|--------|
| run_agent.py | 402 |
| trajectory_compressor.py | 295 |
| cli.py | 279 |
| gateway/run.py | 255 |
| batch_runner.py | 242 |

---

## pyrefly Analysis

### Error Categories

| Category | Count | Severity | Notes |
|----------|-------|----------|-------|
| missing-attribute | 1,334 | LOW | Third-party stubs missing |
| bad-argument-type | 657 | LOW | Type narrowing needed |
| missing-import | 640 | LOW | pytest, mock not in venv |
| bad-function-definition | 314 | LOW | None defaults |
| unsupported-operation | 239 | LOW | Dict/list immutability |
| bad-assignment | 236 | LOW | Type mismatches |
| not-iterable | 146 | LOW | None checks needed |
| not-callable | 50 | MEDIUM | Callable guards needed |
| bad-override | 59 | LOW | Interface changes |
| unbound-name | 46 | MEDIUM | Undefined names |

### Critical/Bug-Related Issues Found

#### 1. trajectory_compressor.py - None defaults in function signatures

```python
# Lines 1241-1245
output: str = None,              # BUG: should be Optional[str]
target_max_tokens: int = None, # BUG: should be Optional[int]
tokenizer: str = None,          # BUG: should be Optional[str]
sample_percent: float = None,   # BUG: should be Optional[float]
```

**Impact:** Type error — None cannot be assigned to non-optional types.
**Fix:** Use `Optional[type]` or `type | None` syntax.

#### 2. trajectory_compressor.py:1047 - Dict assignment with None

```python
results[file_path][entry_idx] = None
```

**Impact:** Type error — None not assignable to tuple type.
**Fix:** Handle None case explicitly.

#### 3. Multiple files - Missing `pytest` stubs

```
ERROR Cannot find module `pytest`
```

**Impact:** 392 false positives in tests directory.
**Fix:** Install pytest types: `uv pip install pytest`

#### 4. Optional[NoneType] patterns

```python
# trajectory_compressor.py
output: str = None  # Should be Optional[str]
```

**Impact:** Type checker flags as error.
**Fix:** Change to `output: Optional[str] = None` or `output: str | None = None`.

### Files with Most Type Errors

| File | Errors |
|------|--------|
| trajectory_compressor.py | ~200+ |
| gateway/run.py | ~150+ |
| agent/*.py | ~100+ |
| tests/*.py | ~500+ (pytest stubs missing) |

---

## ty Analysis

**Tool:** ty 0.0.29 (Astral's pyright successor)
**Python:** 3.13
**Errors:** 3,931

### Error Categories

| Category | Count | Severity | Notes |
|----------|-------|----------|-------|
| invalid-argument-type | 926 | LOW | Type narrowing needed |
| unresolved-attribute | 726 | LOW | Stub files missing |
| unresolved-import | 646 | LOW | acp modules not resolved |
| invalid-parameter-default | 243 | **MEDIUM** | None defaults in function signatures |
| not-subscriptable | 158 | LOW | None checks needed |
| invalid-assignment | 149 | LOW | Type mismatches |
| unsupported-operator | 106 | LOW | Operator type issues |
| no-matching-overload | 59 | LOW | Overload resolution |
| invalid-method-override | 38 | LOW | Interface changes |
| invalid-return-type | 28 | LOW | Return type mismatches |
| unresolved-reference | 22 | MEDIUM | Undefined names |

### Critical Bug: invalid-parameter-default

**Location:** trajectory_compressor.py:1241-1245

```python
def main(
    input: str,
    output: str = None,              # BUG: None not assignable to str
    config: str = "configs/trajectory_compression.yaml",
    target_max_tokens: int = None,   # BUG: None not assignable to int
    tokenizer: str = None,            # BUG: None not assignable to str
    sample_percent: float = None,     # BUG: None not assignable to float
    seed: int = 42,
    dry_run: bool = False,
):
```

**Impact:** Type errors — ty correctly identifies these as bugs.
**Fix:** Change to `output: str | None = None`

### unresolved-import Errors

**Missing modules:**
- `acp` - agent-client-protocol
- `acp.schema`
- `pytest` stubs
- Third-party packages not in venv

**Impact:** ~650 false positives from missing stubs.
**Fix:** Install full dev dependencies: `uv sync --dev`

---

## Security Analysis

### Ruff Security Rules (S*)

| Rule | Location | Severity | Notes |
|------|----------|----------|-------|
| S603 | agent/anthropic_adapter.py:139 | LOW | subprocess call with hardcoded cmds |
| S110 | agent/anthropic_adapter.py:148 | LOW | try-except-pass (logging recommended) |
| S310 | agent/anthropic_adapter.py:391,401 | LOW | URL open with custom schemes |

**No critical security issues found.**

- S603: Uses hardcoded `["claude", "--version"]` — not user-input → **Safe**
- S310: `urllib.request.urlopen` with controlled endpoints → **Accept**
- No SQL injection, command injection, XSS, or credential leaks detected.

---

## Recommendations

### Immediate (Auto-Fix)

1. **Run ruff fix:**
   ```bash
   uvx ruff check . --fix --unsafe-fixes
   ```

2. **Fix None defaults** (trajectory_compressor.py):
   ```python
   # Before
   output: str = None

   # After
   output: str | None = None
   ```

### Short-Term (Manual Review)

1. **Sort imports** in run_agent.py (E402 import order)
2. **Fix unused imports** (F401) — many `re`, `os`, `json` unused
3. **Fix unused variables** (F841) — backend, tool_id, etc.

### Medium-Term

1. **Add pytest stubs** to dev dependencies:
   ```toml
   dev = [..., "pytest", "typeshed"]
   ```

2. **Type the trajectory_compressor module** — highest error density

3. **Consider pyproject.toml updates:**
   - Enable strict type checking mode for `agent/` package
   - Allow loose mode for `tests/`

---

## pyproject.toml Tool Config

Current config (after pyrefly init):

```toml
[tool.pyrefly]
pythonVersion = "3.11"
```

Note: pyrefly inherited `pythonVersion = "3.11"` from original config. Should be updated to `3.13`:
```toml
[tool.pyrefly]
pythonVersion = "3.13"
```

---

## Appendix: Error Counts by File (Top 20)

### ruff
```
run_agent.py: 402
trajectory_compressor.py: 295
cli.py: 279
gateway/run.py: 255
batch_runner.py: 242
tools/web_tools.py: 202
tools/rl_training_tool.py: 202
tools/skills_hub.py: 182
tools/browser_tool.py: 169
gateway/platforms/feishu.py: 165
```

### pyrefly
```
trajectory_compressor.py: ~400
gateway/run.py: ~300
agent/credential_pool.py: ~150
agent/model_metadata.py: ~120
tests/: ~500 (stubs issue)
```
