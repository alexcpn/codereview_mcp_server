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
    index_github_repo,
    get_function_context_for_project,
    find_function_calls_within_project,
    search_codebase_for_project,
    all_refs,
    code_ref,
    code_languages,
    _load_from_cache,
    _DB_PATH,
)

TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")


def _clear_caches():
    """Remove any cached state so each test starts fresh."""
    all_refs.clear()
    code_ref.clear()
    code_languages.clear()


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


class TestCachePersistence:
    def setup_method(self):
        _clear_caches()
        # remove any existing cache DB so tests are deterministic
        if os.path.exists(_DB_PATH):
            os.remove(_DB_PATH)

    def teardown_method(self):
        # clean up cache DB after each test
        if os.path.exists(_DB_PATH):
            os.remove(_DB_PATH)

    def test_cache_db_created_after_indexing(self):
        """After indexing, the SQLite DB file should exist with rows."""
        index_local_folder(TOOLS_DIR)
        assert os.path.exists(_DB_PATH)
        import sqlite3
        con = sqlite3.connect(_DB_PATH)
        count = con.execute("SELECT COUNT(*) FROM repos").fetchone()[0]
        con.close()
        assert count >= 1

    def test_load_from_cache_restores_data(self):
        """After clearing in-memory caches, _load_from_cache restores them."""
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)

        # clear in-memory state
        _clear_caches()
        assert abs_tools not in all_refs

        # load from SQLite
        result = _load_from_cache(abs_tools)
        assert result is not None
        all_classes, all_functions = result
        assert len(all_functions) > 0
        assert abs_tools in all_refs

    def test_query_works_after_cache_restore(self):
        """Query tools should work after loading from SQLite cache."""
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)

        # clear in-memory state and restore from cache
        _clear_caches()
        _load_from_cache(abs_tools)

        context = get_function_context_for_project("index_all_files", abs_tools)
        assert context is not None
        assert "index_all_files" in context

    def test_reindex_uses_cache(self):
        """Second call to index_local_folder should use SQLite cache (no re-parse)."""
        index_local_folder(TOOLS_DIR)
        abs_tools = os.path.abspath(TOOLS_DIR)

        # clear only in-memory state (SQLite cache remains)
        _clear_caches()

        # this should load from SQLite, not re-index
        result = index_local_folder(TOOLS_DIR)
        assert "Indexed" in result
        assert abs_tools in all_refs


GITHUB_REPO = "https://github.com/alexcpn/codereview_mcp_server"


class TestIndexGithubRepo:
    def setup_method(self):
        _clear_caches()

    def test_index_github_repo_clones_and_indexes(self):
        """Clone a real repo and verify indexing produces a valid summary."""
        result = index_github_repo(GITHUB_REPO)
        assert "Indexed" in result
        assert "function(s)" in result
        assert "class(es)" in result

    def test_index_github_repo_populates_cache(self):
        """After indexing, all_refs should be keyed by the github URL."""
        index_github_repo(GITHUB_REPO)
        assert GITHUB_REPO in all_refs
        cached = all_refs[GITHUB_REPO]
        assert len(cached["functions"]) > 0
        assert len(cached["classes"]) > 0

    def test_query_after_index_github_repo(self):
        """Query tools should work using the github URL as repo_name."""
        index_github_repo(GITHUB_REPO)
        context = get_function_context_for_project("index_all_files", GITHUB_REPO)
        assert context is not None
        assert "index_all_files" in context


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
