---
title: Code Review MCP Server
emoji: 🛰️
colorFrom: indigo
colorTo: blue
sdk: docker
app_file: Dockerfile
pinned: false
---

# MCP Server Exposing Repo Code details

### An MCP Server that provides the context for effective code-review of Python, Go and C++ GitHub Repos

MCP is the Model Context Protocol that is used to expose APIs to LLMs, both API description as well as a way to call the API through JSON-RPC.

The MCP server exposes multiple tools implemented in [tools/code_indexer.py](/tools/code_indexer.py):

- **index_github_repo_mcp(github_url, re_index=False)** — Clone a GitHub repo (shallow, depth=1) and index it for querying. Set `re_index=True` to force a fresh clone and re-index.
- **index_folder_mcp(folder_path, re_index=False)** — Index a local folder so the other tools can query it. Set `re_index=True` to force a fresh re-index from disk.
- **get_function_context_for_project_mcp** — Get the details of a function along with its callees.
- **get_function_references_mcp** — Get the references of a function in the indexed codebase.
- **search_codebase_mcp** — Search the repository for a term and return matching lines in grep-like format.

**Note:** You must first index a repo or folder (via `index_github_repo_mcp` or `index_folder_mcp`) before querying it with the other tools. The returned folder path / key should be passed as the `repo_name` parameter to the query tools.

### Caching

Indexed data is persisted to an SQLite database (`cache/index_cache.db`). On subsequent calls — even after a server restart — the cached index is loaded instantly without re-cloning or re-parsing. To pick up new changes in a repo or folder, call the index tool again with `re_index=True`.

The Server use the [TreeSitter project](https://tree-sitter.github.io/tree-sitter/) to do AST parsing of the source and extract, classes, methods, reference and doc stings. Currenly limited to Python,Go and CPP source, but can easily extend to other languages that TreeSitter supports

Uses uv as the  package manager.

Client call example in [Colab Notebook](https://colab.research.google.com/drive/11xryaGH28jpTSd-V2NJ3j5WQJLzr14j4#scrollTo=NRCZqhrb5Pn_)

A sample of this server is hosted in Hugging Face Spaces - https://alexcpn-treesitter-mcp.hf.space/mcp/

---

## How to Run


## Running the Server on  Streamable HTTP

Runs on `http://127.0.0.1:7860/mcp`

```
uv run codereview_mcp_server/http_server.py
```

Check with MCP Insepctor

```
npx @modelcontextprotocol/inspector  
```

Select Streamable HTTP and give the URL `http://127.0.0.1:7860/mcp`


You can expose the above via Ngrok `ngrok http http://localhost:7860` to the Internet 

# Running the STDIO Server


STDIO Client will run the Server and query the tools

```
uv run codereview_mcp_server/stdio_client.py
```

## Use MCP Inspector to check

Example
```
npx @modelcontextprotocol/inspector   uv   --directory codereview_mcp_server/   run   stdio_server.py
```


For testing the logic/for development and extension

```
 uv run code_ast_mcp_server/tools/code_indexer.py 
```

## Configuration for Claude Desktop

```
{
  "mcpServers": {
    "CodeReviewMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "<add path>/codereview_mcp_server",
        "run",
        "stdio_server.py"
      ]
    }
  }
}
```

## Building Docker and Running

```
docker build -t codereview-mcp-server .

docker run -it --rm -p 7860:7860 codereview-mcp-server
```
