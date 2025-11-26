#!/usr/bin/env python3
"""
Simple STDIO MCP client for exercising the FastMCP server.

- Launches the server with uv from the project root.
- Handles the multi-message initialize handshake.
- Prints any stderr output from the child so startup failures are visible.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import threading
from pathlib import Path
from typing import Any, Dict, Optional

PROJECT_ROOT = Path(__file__).resolve().parent
UV_CACHE_DIR = PROJECT_ROOT / ".uv_cache"
UV_CACHE_DIR.mkdir(exist_ok=True)

print("[client] Using project root:", PROJECT_ROOT)

SERVER_CMD = [
    "uv",
    "--directory",
    str(PROJECT_ROOT),
    "run",
    "stdio_server.py",
]
SERVER_ENV = os.environ.copy()
SERVER_ENV.setdefault("UV_CACHE_DIR", str(UV_CACHE_DIR))


# ---------- Framing helpers ----------

def encode_message(obj: Dict[str, Any]) -> bytes:
    """FastMCP stdio transport expects newline-delimited JSON."""
    return (json.dumps(obj) + "\n").encode("utf-8")


def read_message(pipe) -> Optional[Dict[str, Any]]:
    while True:
        line = pipe.readline()
        if not line:
            return None
        text = line.decode(errors="ignore").strip()
        if not text:
            continue
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            print(f"[client] Skipping non-JSON line: {text[:200]} ({exc})")
            continue


def start_reader_thread(pipe, out_queue):
    def run():
        while True:
            msg = read_message(pipe)
            if msg is None:
                break
            out_queue.put(msg)

    t = threading.Thread(target=run, daemon=True)
    t.start()


def start_stderr_thread(pipe):
    def run():
        for line in iter(pipe.readline, b""):
            if not line:
                break
            print(f"[server stderr] {line.decode(errors='ignore').rstrip()}")

    t = threading.Thread(target=run, daemon=True)
    t.start()


# ---------- MCP Client ----------

class MCPClient:
    def __init__(self, cmd, *, env: dict[str, str] | None = None):
        self.proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        self.out_queue = queue.Queue()
        start_reader_thread(self.proc.stdout, self.out_queue)
        start_stderr_thread(self.proc.stderr)

    def send(self, message):
        self.proc.stdin.write(encode_message(message))
        self.proc.stdin.flush()

    def recv(self, timeout=None):
        return self.out_queue.get(timeout=timeout)

    def initialize(self):
        """Handle multi-message initialization handshake."""
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "1.0",
                "clientInfo": {"name": "local-mcp-test-client", "version": "0.1.0"},
                "capabilities": {},
            },
        }
        self.send(init_req)

        responses = []
        got_init_result = False
        while True:
            msg = self.recv()
            responses.append(msg)
            if msg.get("id") == init_req["id"]:
                got_init_result = True
            if msg.get("method") == "notifications/server/update":
                break
            if got_init_result and msg.get("method") is None:
                break

        self.send(
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": None,
            }
        )
        return responses

    def call(self, method, params=None, id=10):
        req = {"jsonrpc": "2.0", "id": id, "method": method, "params": params or {}}
        self.send(req)
        return self.recv()


def main():
    client = MCPClient(SERVER_CMD, env=SERVER_ENV)

    print("🔌 Initializing…")
    init_msgs = client.initialize()
    print(json.dumps(init_msgs, indent=2))

    print("\n📦 tools/list")
    tools = client.call("tools/list", id=20)
    print(json.dumps(tools, indent=2))

    print("\n🔍 Calling search_codebase_mcp…")
    resp = client.call(
        "tools/call",
        {
            "name": "search_codebase_mcp",
            "arguments": {
                "term": "parse_yaml_response_with_repair",
                "github_repo": "https://github.com/alexcpn/noagent-ai",
            },
        },
        id=30,
    )
    print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    main()
