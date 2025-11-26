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
)

# Create MCP instance
mcp = FastMCP()


@mcp.tool()
def get_function_context_for_project_mcp(function_name: str, github_repo: str) -> str:
    """
    Get the details of a function in a GitHub repo along with its callees.
    """
    return get_function_context_for_project(function_name, github_repo)


@mcp.tool()
def get_function_references_mcp(function_name: str, github_repo: str) -> str:
    """
    Get the references of a function in a GitHub repo.
    """
    return find_function_calls_within_project(function_name, github_repo)


@mcp.tool()
def search_codebase_mcp(
    term: str,
    github_repo: str,
    file_patterns: list[str] | None = None,
    ignore_names: list[str] | None = None,
    max_results: int = 200,
) -> str:
    """
    Search the repository for `term` and return matching lines in grep-like format.
    """
    return search_codebase_for_project(
        term=term,
        github_repo=github_repo,
        file_patterns=file_patterns,
        ignore_names=ignore_names,
        max_results=max_results,
    )
    
@mcp.tool()
def get_pull_request_diff_mcp(repo_url, pr_number) -> dict[str, str]:   
    """ 
    Fetch per-file diffs for a given repo URL and PR number.
    Get the git diff of the changes of all commits for the given pull/merge request number.
    Args:
        repo_url (str): The URL of the GitHub repository.
        pr_number (int): The pull request number.
    returns:
        dict: A dictionary mapping changed file paths to their respective diffs.
    """
    
    from tools.code_indexer import get_pr_diff_url as get_diff_util
    return get_diff_util(repo_url, pr_number)

if __name__ == "__main__":
    # Must NOT print anything.
    # Must only run in pure STDIO mode.
   mcp.run(transport='stdio')