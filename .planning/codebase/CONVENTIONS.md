# Coding Conventions

**Analysis Date:** 2026-03-26

## Languages

**Primary:**
- Python 3.11+ (project requires `requires-python = ">=3.11"`)

## Code Style

**Formatting:**
- No automatic formatter configured (no Ruff, Black, or Prettier configs found)
- Manual formatting following PEP 8 guidelines
- 4-space indentation

**Linting:**
- Not configured (no ESLint, Ruff, or similar in `pyproject.toml`)
- Manual code review

**Type Hints:**
- Uses `typing` module imports (e.g., `Optional`, `Dict`, `List`, `Any`)
- Example from `gateway/session.py`:
  ```python
  from typing import Dict, List, Optional, Any
  ```
- Function signatures use string annotations for forward references:
  ```python
  def _skill_should_show(
      conditions: dict,
      available_tools: "set[str] | None",
      available_toolsets: "set[str] | None",
  ) -> bool:
  ```

## Naming Patterns

**Files:**
- Python files: `snake_case.py` (e.g., `prompt_builder.py`, `session.py`)
- Test files: `test_<module_name>.py` (e.g., `test_prompt_builder.py`)

**Directories:**
- `snake_case/` for package directories (e.g., `agent/`, `gateway/`, `hermes_cli/`)

**Classes:**
- PascalCase (e.g., `SessionSource`, `SessionStore`, `FakeHAServer`)
- Dataclasses use `@dataclass` decorator

**Functions:**
- snake_case (e.g., `_scan_context_content`, `build_skills_system_prompt`)
- Private functions prefixed with `_`

**Variables:**
- snake_case (e.g., `fake_home`, `session_id`, `chat_id`)
- Constants: UPPER_SNAKE_CASE (e.g., `CONTEXT_FILE_MAX_CHARS`)

**Type Variables:**
- Usually single letter or PascalCase (standard Python convention)

## Import Organization

**Order (per PEP 8):**
1. Standard library imports (`logging`, `os`, `re`, `pathlib`)
2. Related third-party imports (`pytest`, `pydantic`, `httpx`)
3. Local application imports (relative imports from same package)

**Example from `agent/prompt_builder.py`:**
```python
import logging
import os
import re
from pathlib import Path

from hermes_constants import get_hermes_home
from typing import Optional
```

**Cross-module imports in `gateway/session.py`:**
```python
from .config import (
    Platform,
    GatewayConfig,
    SessionResetPolicy,  # noqa: F401 — re-exported via gateway/__init__.py
    HomeChannel,
)
```

## Docstrings

**Style:** Google-style docstrings

**Module-level docstring** at `gateway/session.py`:
```python
"""
Session management for the gateway.

Handles:
- Session context tracking (where messages come from)
- Session storage (conversations persisted to disk)
- Reset policy evaluation (when to start fresh)
- Dynamic system prompt injection (agent knows its context)
"""
```

**Function docstrings** at `agent/prompt_builder.py`:
```python
def _find_git_root(start: Path) -> Optional[Path]:
    """Walk *start* and its parents looking for a ``.git`` directory.

    Returns the directory containing ``.git``, or ``None`` if we hit the
    filesystem root without finding one.
    """
```

## Error Handling

**Patterns:**
1. Silent fallback with logged debug message (preferred for non-critical failures):
   ```python
   except Exception as e:
       logger.debug("Failed to parse skill file %s: %s", skill_file, e)
       return True, {}, ""
   ```

2. Explicit error re-raising for critical failures:
   ```python
   except Exception as e:
       logger.error("Failed to read skill conditions from %s: %s", skill_file, e)
       raise
   ```

3. Graceful degradation (returning default values on error):
   ```python
   try:
       from tools.skills_tool import _get_disabled_skill_names
       disabled = _get_disabled_skill_names()
   except Exception:
       disabled = set()
   ```

4. Using `# noqa: F401` for intentional re-exports:
   ```python
   SessionResetPolicy,  # noqa: F401 — re-exported via gateway/__init__.py
   ```

## Logging

**Framework:** Standard Python `logging` module

**Pattern:**
```python
logger = logging.getLogger(__name__)
```

**Usage levels:**
- `logger.debug()` - Detailed information for debugging
- `logger.warning()` - Something unexpected but handled gracefully
- `logger.error()` - Serious problem, function could not perform an action

**Example from `agent/prompt_builder.py`:**
```python
if findings:
    logger.warning("Context file %s blocked: %s", filename, ", ".join(findings))
```

## Comment Style

**Inline comments:**
- Used sparingly, after the code they reference
- Use `# noqa: F401` to suppress linter warnings for intentional re-exports

**Block comments:**
- Used for section separators with `# ---------------------------------------------------------------------------`
- Used for guidance sections in test files

**Example section header:**
```python
# =========================================================================
# Context injection scanning
# =========================================================================
```

## Function Design

**Size:** Functions tend to be focused and single-purpose

**Parameters:** Explicit type hints preferred

**Return Values:**
- Use `tuple` for multiple return values when logical
- Use `Optional[T]` for values that may be None
- Use `dict` for complex structured returns

## Module Design

**Package structure:**
```
hermes-agent/
├── agent/           # Core agent logic
├── gateway/         # Message routing and platform integrations
├── hermes_cli/      # CLI interface
├── cron/           # Scheduled job handling
├── environments/    # Environment abstractions
├── tools/          # Tool implementations
└── tests/          # Co-located test suite
```

**Exports:** Use `__init__.py` to expose public API:
```python
from .config import (
    Platform,
    GatewayConfig,
    SessionResetPolicy,  # noqa: F401 — re-exported via gateway/__init__.py
    HomeChannel,
)
```

## Data Classes

**Pattern:** Uses Python dataclasses with `@dataclass`

**Example from `gateway/session.py`:**
```python
@dataclass
class SessionSource:
    platform: Platform
    chat_id: str
    chat_name: Optional[str] = None
    chat_type: str = "dm"
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    thread_id: Optional[str] = None
    chat_topic: Optional[str] = None
    user_id_alt: Optional[str] = None
    chat_id_alt: Optional[str] = None
```

## Pydantic Usage

**Models:** Uses Pydantic v2 (`pydantic>=2.12.5,<3`)

**Patterns:**
- `to_dict()` method for serialization
- `from_dict()` class method for deserialization
- `model_validator` or field validators for complex validation

## Regular Expressions

**Pattern storage:** Compiled at module level in UPPER_SNAKE_CASE variables:
```python
_PREFIX_RE = re.compile(
    r"(?<![A-Za-z0-9_-])(" + "|".join(_PREFIX_PATTERNS) + r")(?![A-Za-z0-9_-])"
)
```

## Async Patterns

**Async functions:** Use `async def`
**Await patterns:** Direct `await` without `asyncio.run()` in async contexts
**Context managers:** `async with` for resource management

---

*Convention analysis: 2026-03-26*
