#!/usr/bin/env python3
"""
MCP Client Wrapper - Communicates with MCP servers via stdio or HTTP

Enables code execution pattern from Anthropic's article:
https://www.anthropic.com/engineering/code-execution-with-mcp

Supports two transports:
- stdio: Local subprocess (existing behavior)
- http: Remote MCP servers via Streamable HTTP transport

Usage:
    from mcp.client import get_client

    client = get_client('fda-mcp')           # stdio
    client = get_client('chembl-mcp')        # http
    result = client.call_tool('lookup_drug', {'search_term': 'obesity'})
"""

import json
import subprocess
import os
import time
from typing import Dict, Any, Optional, Callable
from pathlib import Path

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass  # Available in stdlib, guard just in case

# MCP call tracking callback (set by skill executor)
_mcp_call_callback: Optional[Callable[[str, str, int, bool, Optional[str], Optional[int]], None]] = None


def set_mcp_call_callback(
    callback: Optional[Callable[[str, str, int, bool, Optional[str], Optional[int]], None]]
) -> None:
    """Set callback for MCP call tracking.

    Callback signature: (server, tool, duration_ms, success, error, response_size) -> None
    """
    global _mcp_call_callback
    _mcp_call_callback = callback


def get_mcp_call_callback() -> Optional[Callable]:
    """Get the current MCP call tracking callback."""
    return _mcp_call_callback


class MCPClient:
    """Client for communicating with an MCP server via stdio or HTTP"""

    def __init__(self, server_name: str, config: dict):
        """
        Initialize MCP client for a specific server

        Args:
            server_name: Name of the MCP server
            config: Server configuration from .mcp.json
        """
        self.server_name = server_name
        self.config = config
        self.process = None
        self._request_id = 0

        # Determine transport type
        self.transport = config.get('type', 'stdio')
        self._session_id = None
        self._http_url = config.get('url')

        if self.transport == 'http':
            self._initialize_http()
        else:
            self._start_server()

    # =========================================================================
    # Stdio Transport (existing)
    # =========================================================================

    def _start_server(self):
        """Start the MCP server process (stdio transport)"""
        command = [self.config['command']] + self.config.get('args', [])
        env = os.environ.copy()
        env.update(self.config.get('env', {}))

        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1
        )

        # Wait for server to initialize (if configured)
        # Some servers (like patents-mcp-server) need time to load dependencies
        startup_delay = self.config.get('startup_delay', 0)
        if startup_delay > 0:
            import time
            time.sleep(startup_delay)

        # Initialize connection
        self._send_request('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'mcp-code-execution',
                'version': '1.0.0'
            }
        })

        # Send initialized notification (required by MCP protocol)
        # This is a notification (no response expected)
        initialized_notification = {
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        }
        self.process.stdin.write(json.dumps(initialized_notification) + '\n')
        self.process.stdin.flush()

    def _send_request_stdio(self, method: str, params: dict, request: dict) -> dict:
        """Send JSON-RPC request via stdio transport"""
        request_json = json.dumps(request) + '\n'
        try:
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
        except BrokenPipeError as e:
            # Capture stderr for debugging
            stderr_output = ""
            if self.process.stderr:
                try:
                    # Non-blocking read of available stderr
                    import select
                    if select.select([self.process.stderr], [], [], 0)[0]:
                        stderr_output = self.process.stderr.read()
                except:
                    pass

            print(f"[MCP CLIENT ERROR] Subprocess stderr: {stderr_output}")
            raise

        # Read response (skip non-JSON lines like debug output)
        # CRITICAL FIX (2026-01-21): Some MCP servers (like Medicaid) output progress
        # messages during long operations (e.g., downloading 123MB NADAC data).
        # We need to keep reading until we get valid JSON, with a time-based timeout
        # instead of a line count limit.
        import select
        import time

        timeout_seconds = 120  # 2 minute timeout for slow operations
        max_non_json_lines = 500  # Safety limit to avoid infinite loops
        start_time = time.time()
        response_line = None
        non_json_count = 0

        while time.time() - start_time < timeout_seconds:
            # Use select to wait for data with 1-second intervals
            readable, _, _ = select.select([self.process.stdout], [], [], 1.0)

            if not readable:
                # No data yet, continue waiting
                continue

            line = self.process.stdout.readline()
            if not line:
                raise Exception(f"No response from MCP server {self.server_name}")

            line = line.strip()
            if not line:
                continue

            # Try to parse as JSON - skip non-JSON lines (debug output)
            try:
                response = json.loads(line)
                response_line = line
                break
            except json.JSONDecodeError:
                # This is likely debug/progress output, skip it and try next line
                non_json_count += 1
                if non_json_count >= max_non_json_lines:
                    raise Exception(f"Too many non-JSON lines ({non_json_count}) from MCP server {self.server_name}")
                continue

        if not response_line:
            elapsed = time.time() - start_time
            raise Exception(f"No valid JSON response from MCP server {self.server_name} after {elapsed:.1f}s timeout")

        # Check for errors
        if 'error' in response:
            raise Exception(f"MCP error: {response['error']}")

        return response.get('result', {})

    # =========================================================================
    # HTTP Transport (Streamable HTTP)
    # =========================================================================

    def _initialize_http(self):
        """Initialize HTTP transport via MCP Streamable HTTP protocol"""
        result = self._send_request('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'mcp-code-execution',
                'version': '1.0.0'
            }
        })

        # Send initialized notification (no response expected)
        self._request_id += 1
        notification = {
            'jsonrpc': '2.0',
            'method': 'notifications/initialized',
            'params': {}
        }
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
        }
        if self._session_id:
            headers['Mcp-Session-Id'] = self._session_id

        req = urllib.request.Request(
            self._http_url,
            data=json.dumps(notification).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        try:
            urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError:
            pass  # Some servers don't respond to notifications

    def _send_request_http(self, method: str, params: dict, request: dict) -> dict:
        """Send JSON-RPC request via HTTP transport"""
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream',
        }
        if self._session_id:
            headers['Mcp-Session-Id'] = self._session_id

        req = urllib.request.Request(
            self._http_url,
            data=json.dumps(request).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        try:
            response = urllib.request.urlopen(req, timeout=120)
        except urllib.error.HTTPError as e:
            if e.code == 404 and self._session_id:
                # Session expired — re-initialize and retry
                self._session_id = None
                self._initialize_http()
                headers['Mcp-Session-Id'] = self._session_id
                req = urllib.request.Request(
                    self._http_url,
                    data=json.dumps(request).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
                response = urllib.request.urlopen(req, timeout=120)
            else:
                raise Exception(
                    f"HTTP error from MCP server {self.server_name}: "
                    f"{e.code} {e.reason}"
                )

        # Capture session ID from response headers
        session_id = response.headers.get('Mcp-Session-Id')
        if session_id:
            self._session_id = session_id

        content_type = response.headers.get('Content-Type', '')
        body = response.read().decode('utf-8')

        # Parse response based on content type
        if 'text/event-stream' in content_type:
            result = self._parse_sse_response(body)
        else:
            result = json.loads(body)

        # Check for errors
        if isinstance(result, dict) and 'error' in result:
            raise Exception(f"MCP error: {result['error']}")

        return result.get('result', {})

    def _parse_sse_response(self, body: str) -> dict:
        """Parse Server-Sent Events response to extract JSON-RPC result"""
        for line in body.split('\n'):
            line = line.strip()
            if line.startswith('data:'):
                data = line[5:].strip()
                if not data:
                    continue
                try:
                    return json.loads(data)
                except json.JSONDecodeError:
                    continue

        raise Exception(
            f"No valid JSON-RPC message found in SSE response "
            f"from {self.server_name}"
        )

    # =========================================================================
    # Unified Interface
    # =========================================================================

    def _send_request(self, method: str, params: dict) -> dict:
        """Send JSON-RPC request to MCP server (dispatches by transport)"""
        self._request_id += 1
        request = {
            'jsonrpc': '2.0',
            'id': self._request_id,
            'method': method,
            'params': params
        }

        if self.transport == 'http':
            return self._send_request_http(method, params, request)
        else:
            return self._send_request_stdio(method, params, request)

    def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Call an MCP tool

        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool result (dict if JSON, str if text/markdown)
        """
        start_time = time.time()
        success = True
        error_msg = None
        response_size = None

        try:
            result = self._send_request('tools/call', {
                'name': tool_name,
                'arguments': arguments
            })

            # Extract content from MCP response
            if isinstance(result, dict) and 'content' in result:
                content = result['content']
                if isinstance(content, list) and len(content) > 0:
                    first_content = content[0]
                    if isinstance(first_content, dict):
                        # Handle different content types
                        if 'text' in first_content:
                            text = first_content['text']
                            response_size = len(text.encode('utf-8')) if text else 0
                            # Try to parse as JSON
                            try:
                                parsed = json.loads(text)
                                return parsed
                            except json.JSONDecodeError:
                                # Return as text (markdown, etc.)
                                return {'text': text, 'format': 'text'}
                        elif 'data' in first_content:
                            return first_content['data']

            return result

        except Exception as e:
            success = False
            error_msg = str(e)
            raise

        finally:
            # Record MCP call stats if callback is set
            duration_ms = int((time.time() - start_time) * 1000)
            callback = get_mcp_call_callback()
            if callback:
                try:
                    callback(
                        self.server_name,
                        tool_name,
                        duration_ms,
                        success,
                        error_msg,
                        response_size
                    )
                except Exception as cb_err:
                    # Don't let callback errors affect the main flow
                    print(f"[MCP CLIENT] Stats callback error: {cb_err}")

    def list_tools(self) -> list:
        """List available tools from this MCP server"""
        result = self._send_request('tools/list', {})
        return result.get('tools', [])

    def close(self):
        """Close the MCP server connection"""
        if self.transport == 'http':
            # Optionally terminate HTTP session
            if self._session_id:
                try:
                    req = urllib.request.Request(
                        self._http_url,
                        headers={'Mcp-Session-Id': self._session_id},
                        method='DELETE'
                    )
                    urllib.request.urlopen(req, timeout=5)
                except Exception:
                    pass  # Best-effort session cleanup
                self._session_id = None
        else:
            if self.process:
                self.process.terminate()
                self.process.wait(timeout=5)


# Global client registry
_clients = {}
_config = None


def load_config():
    """
    Load MCP configuration with environment-aware fallback.
    
    Priority:
    1. MCP_CONFIG_FILE env var (explicit path)
    2. .mcp.local.json (local overrides, gitignored)
    3. .mcp.server.json (production config)
    4. .mcp.json (default/legacy)
    """
    global _config
    if _config is not None:
        return _config
    
    # Config file priority
    config_names = ['.mcp.local.json', '.mcp.server.json', '.mcp.json']
    
    # Check env var first
    env_config = os.environ.get('MCP_CONFIG_FILE')
    if env_config:
        config_path = Path(env_config)
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                _config = data.get('mcpServers', {})
            return _config
        else:
            raise FileNotFoundError(f"MCP_CONFIG_FILE not found: {env_config}")
    
    # Find project root by walking up from this file
    current = Path(__file__).resolve()
    while current != current.parent:
        for config_name in config_names:
            config_path = current / config_name
            if config_path.exists():
                with open(config_path) as f:
                    data = json.load(f)
                    _config = data.get('mcpServers', {})
                return _config
        current = current.parent

    # Fallback: check current working directory
    for config_name in config_names:
        config_path = Path.cwd() / config_name
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                _config = data.get('mcpServers', {})
            return _config
    
    raise FileNotFoundError(
        f"Could not find MCP config. Tried: {', '.join(config_names)}. "
        f"Set MCP_CONFIG_FILE env var or create one of these files."
    )


def get_client(server_name: str) -> MCPClient:
    """
    Get or create an MCP client for the specified server

    Args:
        server_name: Name of the MCP server (e.g., 'fda-mcp')

    Returns:
        MCPClient instance
    """
    if server_name not in _clients:
        config = load_config()
        if server_name not in config:
            raise ValueError(f"Unknown MCP server: {server_name}")

        _clients[server_name] = MCPClient(server_name, config[server_name])

    return _clients[server_name]


def close_all():
    """Close all MCP client connections"""
    for client in _clients.values():
        client.close()
    _clients.clear()
