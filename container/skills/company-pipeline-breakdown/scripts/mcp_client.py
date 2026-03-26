"""Lightweight MCP client for calling MCP servers from Python scripts.

In the BioClaw container, MCP servers are mounted at /tmp/{srv}-mcp-server/.
This module spawns them as subprocesses and communicates via JSON-RPC over stdio.

Usage:
    from mcp_client import McpClient

    with McpClient("ctgov") as ctgov:
        result = ctgov.call("ct_gov_studies", method="search", lead="Pfizer")
"""

import subprocess
import json
import os
import sys
from typing import Any, Optional


class McpClient:
    """Minimal MCP client that talks to a local Node.js MCP server via stdio."""

    def __init__(self, server_name: str, server_dir: Optional[str] = None):
        self.server_name = server_name
        self.server_dir = server_dir or self._find_server(server_name)
        self.proc = None
        self.msg_id = 0
        self._tool_name = None

    @staticmethod
    def _find_server(name: str) -> str:
        """Find MCP server directory — check container path, env var, then local dev paths."""
        # Container path (inside Docker)
        container_path = f"/tmp/{name}-mcp-server"
        if os.path.exists(os.path.join(container_path, "build", "index.js")):
            return container_path

        # Environment variable (e.g., CTGOV_MCP_SERVER_PATH)
        env_key = f"{name.upper().replace('-', '_')}_MCP_SERVER_PATH"
        env_path = os.environ.get(env_key, "")
        if env_path and os.path.exists(os.path.join(env_path, "build", "index.js")):
            return env_path

        # Local dev path (~/code/{name}-mcp-server)
        home = os.environ.get("HOME", os.path.expanduser("~"))
        local_path = os.path.join(home, "code", f"{name}-mcp-server")
        if os.path.exists(os.path.join(local_path, "build", "index.js")):
            return local_path

        return container_path  # Fallback (will fail with clear error)

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args):
        self.close()

    def connect(self):
        """Start the MCP server process and initialize."""
        entry = os.path.join(self.server_dir, "build", "index.js")
        if not os.path.exists(entry):
            raise FileNotFoundError(f"MCP server not found: {entry}")

        self.proc = subprocess.Popen(
            ["node", entry],
            cwd=self.server_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Initialize
        self.msg_id += 1
        self._send({
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "bioclaw-script", "version": "1.0.0"},
            },
        })
        resp = self._recv()
        if not resp or "result" not in resp:
            raise ConnectionError(f"Failed to initialize {self.server_name}")

        # Send initialized notification
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized"})

        # Discover tool name
        self.msg_id += 1
        self._send({"jsonrpc": "2.0", "id": self.msg_id, "method": "tools/list", "params": {}})
        tools_resp = self._recv()
        if tools_resp and "result" in tools_resp:
            tools = tools_resp["result"].get("tools", [])
            if tools:
                self._tool_name = tools[0]["name"]

    def call(self, tool_name: str = None, **kwargs) -> Any:
        """Call a tool on the MCP server. Returns parsed result or raw text."""
        tool = tool_name or self._tool_name
        if not tool:
            raise ValueError("No tool name specified and none discovered")

        self.msg_id += 1
        self._send({
            "jsonrpc": "2.0",
            "id": self.msg_id,
            "method": "tools/call",
            "params": {"name": tool, "arguments": kwargs},
        })

        resp = self._recv()
        if not resp:
            return None

        if "error" in resp:
            raise RuntimeError(f"MCP error: {resp['error'].get('message', resp['error'])}")

        result = resp.get("result", {})
        if result.get("isError"):
            text = result.get("content", [{}])[0].get("text", "Unknown error")
            return {"error": text}

        content = result.get("content", [])
        if content and content[0].get("text"):
            text = content[0]["text"]
            try:
                return json.loads(text)
            except (json.JSONDecodeError, TypeError):
                return text

        return result

    def close(self):
        """Terminate the MCP server process."""
        if self.proc:
            try:
                self.proc.stdin.close()
                self.proc.terminate()
                self.proc.wait(timeout=5)
            except Exception:
                if self.proc.poll() is None:
                    self.proc.kill()

    def _send(self, msg: dict):
        if self.proc and self.proc.stdin:
            self.proc.stdin.write(json.dumps(msg) + "\n")
            self.proc.stdin.flush()

    def _recv(self) -> Optional[dict]:
        if not self.proc or not self.proc.stdout:
            return None
        line = self.proc.stdout.readline()
        if not line:
            return None
        try:
            return json.loads(line.strip())
        except json.JSONDecodeError:
            return None
