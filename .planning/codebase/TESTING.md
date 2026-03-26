# Testing Patterns

**Analysis Date:** 2026-03-26

## Test Framework

**Runner:**
- pytest 9.x (`pytest>=9.0.2,<10`)
- pytest-asyncio 1.x (`pytest-asyncio>=1.3.0,<2`)
- pytest-xdist for parallel execution (`pytest-xdist>=3.0,<4`)

**Assertion Library:**
- pytest built-in assertions
- unittest.mock for mocking

**Config in `pyproject.toml`:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: marks tests requiring external services (API keys, Modal, etc.)",
]
addopts = "-m 'not integration' -n auto"
```

**Run Commands:**
```bash
pytest                          # Run all tests (excluding integration)
pytest -m integration          # Run integration tests only
pytest -n auto                 # Run with parallel workers (auto-detected)
pytest tests/gateway/           # Run specific directory
pytest tests/agent/test_*.py   # Run specific test file
```

## Test File Organization

**Location:**
- Co-located in `tests/` directory mirroring source structure
- `tests/` contains subdirectories matching source packages: `agent/`, `gateway/`, `cron/`, `acp/`

**Naming:**
- `test_<module_name>.py` for test files
- Example: `tests/agent/test_prompt_builder.py`, `tests/gateway/test_session.py`

**Structure:**
```
tests/
├── conftest.py              # Shared fixtures
├── fakes/
│   ├── __init__.py
│   └── fake_ha_server.py    # Fake Home Assistant server
├── agent/
│   └── test_*.py
├── gateway/
│   └── test_*.py
├── cron/
│   └── test_*.py
└── acp/
    └── test_*.py
```

## Test Structure

**Class-based organization** using pytest classes:
```python
class TestSessionSourceRoundtrip:
    def test_full_roundtrip(self):
        source = SessionSource(
            platform=Platform.TELEGRAM,
            chat_id="12345",
            ...
        )
        d = source.to_dict()
        restored = SessionSource.from_dict(d)

        assert restored.platform == Platform.TELEGRAM
        assert restored.chat_id == "12345"
```

**Independent test classes** for different aspects:
```python
class TestSessionSourceRoundtrip:
    ...

class TestSessionSourceDescription:
    ...

class TestBuildSessionContextPrompt:
    ...
```

## Fixtures and Factories

**Global fixtures in `tests/conftest.py`:**

1. `_isolate_hermes_home` - Redirects HERMES_HOME to temp directory:
```python
@pytest.fixture(autouse=True)
def _isolate_hermes_home(tmp_path, monkeypatch):
    """Redirect HERMES_HOME to a temp dir so tests never write to ~/.hermes/."""
    fake_home = tmp_path / "hermes_test"
    fake_home.mkdir()
    (fake_home / "sessions").mkdir()
    (fake_home / "cron").mkdir()
    (fake_home / "memories").mkdir()
    (fake_home / "skills").mkdir()
    monkeypatch.setenv("HERMES_HOME", str(fake_home))
```

2. `mock_config` - Returns minimal hermes config:
```python
@pytest.fixture()
def mock_config():
    """Return a minimal hermes config dict suitable for unit tests."""
    return {
        "model": "test/mock-model",
        "toolsets": ["terminal", "file"],
        ...
    }
```

3. `_ensure_current_event_loop` - Provides event loop for sync tests:
```python
@pytest.fixture(autouse=True)
def _ensure_current_event_loop(request):
    if request.node.get_closest_marker("asyncio") is not None:
        yield
        return
    ...
```

4. `_enforce_test_timeout` - 30-second timeout per test:
```python
@pytest.fixture(autouse=True)
def _enforce_test_timeout():
    """Kill any individual test that takes longer than 30 seconds."""
    if sys.platform == "win32":
        yield
        return
    old = signal.signal(signal.SIGALRM, _timeout_handler)
    signal.alarm(30)
    yield
    signal.alarm(0)
    signal.signal(signal.SIGALRM, old)
```

**Local fixtures** defined within test files:
```python
class TestSessionStoreRewriteTranscript:
    @pytest.fixture()
    def store(self, tmp_path):
        config = GatewayConfig()
        with patch("gateway.session.SessionStore._ensure_loaded"):
            s = SessionStore(sessions_dir=tmp_path, config=config)
        s._db = None
        s._loaded = True
        return s
```

## Mocking

**Framework:** `unittest.mock` (from Python stdlib)

**Common patterns:**

1. **Patch decorator for context:**
```python
from unittest.mock import patch

class TestSessionStoreRewriteTranscript:
    def test_rewrite_replaces_jsonl(self, store, tmp_path):
        with patch("gateway.session.SessionStore._ensure_loaded"):
            s = SessionStore(sessions_dir=tmp_path, config=config)
```

2. **MagicMock for db/stores:**
```python
from unittest.mock import MagicMock

@pytest.fixture
def store_with_mock_db(self, tmp_path):
    s._db = MagicMock()
    return s

def test_uses_database_count_when_available(self, store_with_mock_db):
    store._db.session_count.return_value = 3
    assert store.has_any_sessions() is True
```

3. **Monkeypatch for environment/attributes:**
```python
def test_logs_parse_failures_and_returns_defaults(self, tmp_path, monkeypatch, caplog):
    def boom(*args, **kwargs):
        raise OSError("read exploded")

    monkeypatch.setattr(type(skill_file), "read_text", boom)
    with caplog.at_level(logging.DEBUG, logger="agent.prompt_builder"):
        is_compat, frontmatter, desc = _parse_skill_file(skill_file)
```

4. **sys monkeypatching:**
```python
from unittest.mock import patch

with patch("tools.skills_tool.sys") as mock_sys:
    mock_sys.platform = "linux"
    is_compat, _, _ = _parse_skill_file(skill_file)
```

## Async Testing

**Marker:** `@pytest.mark.asyncio` for async test functions

**Example from `tests/acp/test_server.py`:**
```python
@pytest.mark.asyncio
async def test_server_handshake(self, server):
    conn = await server.connect()
    await conn.send(...)
    assert conn.state == State.AUTHENTICATED
```

**Fake async server pattern** using `aiohttp`:
```python
# From tests/fakes/fake_ha_server.py
class FakeHAServer:
    async def __aenter__(self) -> "FakeHAServer":
        await self.start()
        return self

    async def __aexit__(self, *exc) -> None:
        await self.stop()

# Usage:
async with FakeHAServer(token="test-token") as server:
    url = server.url
    await server.push_event(event_data)
```

## Assertions

**Standard pytest assertions:**
```python
assert restored.platform == Platform.TELEGRAM
assert "Home Chat" in prompt
assert len(messages) == 2
```

**Exception testing:**
```python
def test_invalid_platform_raises(self):
    with pytest.raises((ValueError, KeyError)):
        SessionSource.from_dict({"platform": "nonexistent", "chat_id": "1"})
```

**caplog for logging assertions:**
```python
def test_logs_parse_failures_and_returns_defaults(self, tmp_path, monkeypatch, caplog):
    ...
    assert "Failed to parse skill file" in caplog.text
    assert str(skill_file) in caplog.text
```

## Test Categories

**Markers:**
- `integration` - Tests requiring external services (API keys, Modal, etc.)

**Exclusion pattern:**
```bash
pytest -m 'not integration'
```

## Common Patterns

**Fixture for tmp_path:**
```python
def test_something(self, tmp_path):
    skill_file = tmp_path / "SKILL.md"
    skill_file.write_text("---\nname: test\n---\n")
```

**Patch + tmp_path:**
```python
@pytest.fixture()
def store(self, tmp_path):
    config = GatewayConfig()
    with patch("gateway.session.SessionStore._ensure_loaded"):
        s = SessionStore(sessions_dir=tmp_path, config=config)
    s._loaded = True
    return s
```

**Async context manager:**
```python
async with FakeHAServer(token="test-token") as server:
    # test code here
```

**Regression test pattern:**
```python
class TestWhatsAppDMSessionKeyConsistency:
    """Regression: all session-key construction must go through build_session_key
    so DMs are isolated by chat_id across platforms."""
```

## Fake Implementations

**Location:** `tests/fakes/`

**Example: `FakeHAServer`** in `tests/fakes/fake_ha_server.py`:
- Real HTTP + WebSocket server using `aiohttp.web`
- Mimics Home Assistant API surface
- Tracks received service calls and notifications for test assertions

**Usage pattern:**
```python
async with FakeHAServer(token="test-token") as server:
    url = server.url
    await server.push_event(event_data)
    assert server.received_notifications
```

---

*Testing analysis: 2026-03-26*
