"""
  FastMCP Server for Code Indexing Tools
    This script sets up a FastMCP server to expose tools for code indexing,
    specifically for retrieving function context, call references, and simple
    string searches within a GitHub repository.
 
    Author: Alex Punnen
    License: MIT License
  
"""
from fastmcp import FastMCP
from tools.code_indexer import (
    get_function_context_for_project,
    find_function_calls_within_project,
    search_codebase_for_project,
    index_local_folder,
    index_github_repo,
)

mcp = FastMCP()


@mcp.tool()
def get_function_context_for_project_mcp(function_name: str, repo_name: str) -> str:
    """
    Get the details of a function in a GitHub repo along with its callees.
    
    @param function_name: The name of the function to find.
    @param repo_name: The URL of the GitHub repo.
    """
    print(f"Finding context for function: {function_name} in repo: {repo_name}")
    return get_function_context_for_project(function_name, repo_name)


@mcp.tool()
def get_function_references_mcp(function_name: str, repo_name: str) -> str:
    """
    Get the references of a function in a GitHub repo.
    
    @param function_name: The name of the function whose references to find.
    @param repo_name: The URL of the GitHub repo.
    """
    print(f"Finding references for function: {function_name} in repo: {repo_name}")
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
    Search the repository for ``term`` and return matching lines in a grep-like format.
    """
    print(f"Searching for term '{term}' in repo: {repo_name}")
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
    print(f"Indexing local folder: {folder_path}")
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
    print(f"Indexing GitHub repo: {github_url}")
    return index_github_repo(github_url, re_index=re_index)


if __name__ == "__main__":

    import os
    ip = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "7860"))
    print(f"Starting Code AST MCP server on {ip}:{port}")
    try:
        mcp.run(
            transport="streamable-http",
            host=ip,
            port=port,
            path="/mcp",
            log_level="debug",
        )
    except Exception as e:
        print(f"Failed to start MCP server: {e}")
