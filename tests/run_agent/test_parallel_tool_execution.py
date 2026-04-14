"""Tests for parallel tool execution on safe tools."""
import json
from types import SimpleNamespace

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from run_agent import (
    _NEVER_PARALLEL_TOOLS,
    _PARALLEL_SAFE_TOOLS,
    _is_tool_parallel_safe,
    _should_parallelize_tool_batch,
)


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


def _make_tool_call(name: str, path: str | None = None) -> SimpleNamespace:
    """Construct a mock tool call object for _should_parallelize_tool_batch."""
    args = {"path": path} if path is not None else {}
    return SimpleNamespace(
        function=SimpleNamespace(name=name, arguments=json.dumps(args))
    )


class TestParallelToolExecutionPropertyBased:
    """Property-based tests for parallel tool execution infrastructure."""

    @given(tool_name=st.text(min_size=1))
    def test_is_tool_parallel_safe_is_deterministic(self, tool_name: str):
        """_is_tool_parallel_safe should return same result for same input."""
        result1 = _is_tool_parallel_safe(tool_name)
        result2 = _is_tool_parallel_safe(tool_name)
        assert result1 == result2

    @given(st.sampled_from(sorted(_PARALLEL_SAFE_TOOLS)))
    def test_parallel_safe_tools_return_true(self, tool: str):
        """Every tool in _PARALLEL_SAFE_TOOLS should return True."""
        assert _is_tool_parallel_safe(tool) is True

    @given(st.sampled_from(sorted(_NEVER_PARALLEL_TOOLS)))
    def test_never_parallel_tools_return_false(self, tool: str):
        """Tools in _NEVER_PARALLEL_TOOLS should never be parallel-safe."""
        assert _is_tool_parallel_safe(tool) is False

    @given(
        tool_names=st.lists(
            st.sampled_from(sorted(_PARALLEL_SAFE_TOOLS)), min_size=2, max_size=10
        )
    )
    @settings(max_examples=50)
    def test_should_parallelize_batch_all_safe(self, tool_names: list[str]):
        """Batch of all safe tools should be parallelizable."""
        tool_calls = [_make_tool_call(name, f"/tmp/file_{i}.txt") for i, name in enumerate(tool_names)]
        assert _should_parallelize_tool_batch(tool_calls) is True

    @given(
        tool_names=st.lists(
            st.sampled_from(sorted(_PARALLEL_SAFE_TOOLS)), min_size=0, max_size=1
        )
    )
    @settings(max_examples=50)
    def test_should_parallelize_batch_too_few_tools(self, tool_names: list[str]):
        """Batch with fewer than 2 tools should not be parallelized."""
        tool_calls = [_make_tool_call(name, f"/tmp/file_{i}.txt") for i, name in enumerate(tool_names)]
        assert _should_parallelize_tool_batch(tool_calls) is False

    @given(
        safe_tools=st.lists(
            st.sampled_from(sorted(_PARALLEL_SAFE_TOOLS)), min_size=1, max_size=5
        )
    )
    @settings(max_examples=50)
    def test_should_parallelize_batch_mixed_with_never_parallel(self, safe_tools: list[str]):
        """Batch containing a never-parallel tool should not be parallelized."""
        assume(len(_NEVER_PARALLEL_TOOLS) > 0)
        never_parallel_list = list(_NEVER_PARALLEL_TOOLS)
        combined = safe_tools + never_parallel_list[:1]
        tool_calls = [_make_tool_call(name, f"/tmp/file_{i}.txt") for i, name in enumerate(combined)]
        assert _should_parallelize_tool_batch(tool_calls) is False

    @given(
        path1=st.from_regex(r"/[a-zA-Z0-9_/-]+", fullmatch=True),
        path2=st.from_regex(r"/[a-zA-Z0-9_/-]+", fullmatch=True),
    )
    @settings(max_examples=50)
    def test_path_scoped_tool_with_different_paths(self, path1: str, path2: str):
        """Path-scoped tools with different absolute paths should be parallelizable."""
        assume(path1 != path2)
        tool_calls = [
            _make_tool_call("read_file", path1),
            _make_tool_call("read_file", path2),
        ]
        # Different paths do not overlap, so should be parallelizable
        assert _should_parallelize_tool_batch(tool_calls) is True

