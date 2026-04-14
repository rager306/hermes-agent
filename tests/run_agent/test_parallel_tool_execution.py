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
