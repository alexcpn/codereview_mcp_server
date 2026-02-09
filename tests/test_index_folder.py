"""
Tests for the index_local_folder functionality.

Indexes the project's own tools/ directory (Python files) and verifies
that the existing query helpers work with the indexed data.
"""

import os
import sys
import pytest

# Ensure the project root is on sys.path so "tools" is importable.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tools.code_indexer import (
    index_local_folder,
    get_function_context_for_project,
    find_function_calls_within_project,
    search_codebase_for_project,
    all_refs,
    code_ref,
)

TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")


def _clear_caches():
    """Remove any cached state so each test starts fresh."""
    all_refs.clear()
    code_ref.clear()


class TestIndexLocalFolder:
    def setup_method(self):
        _clear_caches()

    # ── basic indexing ──────────────────────────────────────────────

    def test_index_returns_summary(self):
        result = index_local_folder(TOOLS_DIR)
        assert "Indexed" in result
        assert "function(s)" in result
        assert "class(es)" in result

    def test_index_populates_cache(self):
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)
        assert abs_tools in all_refs
        cached = all_refs[abs_tools]
        assert len(cached["functions"]) > 0

    def test_index_already_indexed(self):
        index_local_folder(TOOLS_DIR)
        result = index_local_folder(TOOLS_DIR)
        assert "Already indexed" in result

    def test_index_invalid_path(self):
        result = index_local_folder("/nonexistent/path/xyz")
        assert "Error" in result

    # ── query tools work after indexing ─────────────────────────────

    def test_get_function_context_after_index(self):
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)
        context = get_function_context_for_project("index_all_files", abs_tools)
        assert context is not None
        assert "index_all_files" in context

    def test_find_function_calls_after_index(self):
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)
        refs = find_function_calls_within_project("_run_query", abs_tools)
        assert "_run_query" in refs

    def test_search_codebase_after_index(self):
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)
        results = search_codebase_for_project("def index_all_files", abs_tools)
        assert "index_all_files" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
