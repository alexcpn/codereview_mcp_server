#!/usr/bin/env python3
"""
FastMCP STDIO Server for Code Indexing Tools

Fully Claude Desktop compatible (STRICT STDIO, no prints, no logs).
"""

from fastmcp import FastMCP
from tools.code_indexer import (
    get_function_context_for_project,
    find_function_calls_within_project,
    search_codebase_for_project,
    index_local_folder,
    index_github_repo,
)

# Create MCP instance
mcp = FastMCP()


@mcp.tool()
def get_function_context_for_project_mcp(function_name: str, repo_name: str) -> str:
    """
    Get the details of a function in a GitHub repo along with its callees.
    """
    return get_function_context_for_project(function_name, repo_name)


@mcp.tool()
def get_function_references_mcp(function_name: str, repo_name: str) -> str:
    """
    Get the references of a function in a GitHub repo.
    """
    return find_function_calls_within_project(function_name, repo_name)


@mcp.tool()
def search_codebase_mcp(
    term: str,
    repo_name: str,
    file_patterns: list[str] | None = None,
    ignore_names: list[str] | None = None,
    max_results: int = 200,
) -> str:
    """
    Search the repository for `term` and return matching lines in grep-like format.
    """
    return search_codebase_for_project(
        term=term,
        repo_name=repo_name,
        file_patterns=file_patterns,
        ignore_names=ignore_names,
        max_results=max_results,
    )
    


@mcp.tool()
def index_folder_mcp(folder_path: str, re_index: bool = False) -> str:
    """
    Index a local folder so the other tools can query it.

    Indexed data is persisted to an SQLite cache on disk. On subsequent calls
    (even after a server restart), the cached index is loaded instantly without
    re-parsing. Pass ``re_index=True`` to discard the cache and force a fresh
    re-index of the folder.

    After indexing, pass the same ``folder_path`` as the ``repo_name``
    parameter in get_function_context_for_project_mcp,
    get_function_references_mcp, or search_codebase_mcp.

    @param folder_path: Absolute or relative path to a local code directory.
    @param re_index: If True, discard cached data and force a full re-index from disk. Defaults to False.
    """
    return index_local_folder(folder_path, re_index=re_index)


@mcp.tool()
def index_github_repo_mcp(github_url: str, re_index: bool = False) -> str:
    """
    Clone a GitHub repo (shallow, depth=1) and index it for querying.

    Indexed data is persisted to an SQLite cache on disk. On subsequent calls
    (even after a server restart), the cached index is loaded instantly without
    re-cloning. Pass ``re_index=True`` to discard the cache and force a fresh
    clone and re-index.

    After indexing, use the same ``github_url`` as the ``repo_name``
    parameter in get_function_context_for_project_mcp,
    get_function_references_mcp, or search_codebase_mcp.

    @param github_url: HTTPS URL of the GitHub repository.
    @param re_index: If True, discard cached data and force a fresh clone and re-index. Defaults to False.
    """
    return index_github_repo(github_url, re_index=re_index)


if __name__ == "__main__":
    # Must NOT print anything.
    # Must only run in pure STDIO mode.
   mcp.run(transport='stdio')