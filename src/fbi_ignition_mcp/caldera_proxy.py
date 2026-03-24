"""Caldera MCP gateway proxy — forwards tool calls to a remote Ignition gateway."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

DEFAULT_CALDERA_URL = "http://localhost:8765/mcp"


class CalderaProxy:
    """Thin async proxy that forwards MCP tool-calls to Caldera over HTTP.

    The Caldera MCP server exposes a standard MCP-over-HTTP endpoint on the
    Ignition gateway.  This class wraps ``httpx.AsyncClient`` to relay
    ``tools/call`` requests and stream the response back.
    """

    def __init__(self, base_url: str | None = None, timeout: float = 30.0) -> None:
        self.base_url = (
            base_url
            or os.environ.get("CALDERA_MCP_URL")
            or DEFAULT_CALDERA_URL
        )
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._client

    async def health_check(self) -> dict[str, Any]:
        """Ping the Caldera gateway and return connectivity info."""
        try:
            client = await self._get_client()
            resp = await client.get("/health")
            resp.raise_for_status()
            return {"connected": True, "url": self.base_url, "detail": resp.json()}
        except httpx.HTTPStatusError as exc:
            return {
                "connected": False,
                "url": self.base_url,
                "error": f"HTTP {exc.response.status_code}",
            }
        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            return {
                "connected": False,
                "url": self.base_url,
                "error": str(exc),
            }

    async def call_tool(
        self, tool_name: str, arguments: dict[str, Any] | None = None
    ) -> str:
        """Forward a tool call to the Caldera MCP server.

        Returns the JSON string response from the gateway, or an error
        message if the gateway is unreachable.
        """
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments or {},
            },
        }
        try:
            client = await self._get_client()
            resp = await client.post("", json=payload)
            resp.raise_for_status()
            data = resp.json()
            # Extract the result content from the MCP response envelope
            result = data.get("result", data)
            if isinstance(result, dict) and "content" in result:
                contents = result["content"]
                # Flatten text content blocks
                texts = [
                    c.get("text", json.dumps(c))
                    for c in contents
                    if isinstance(c, dict)
                ]
                return "\n".join(texts) if texts else json.dumps(result, indent=2)
            return json.dumps(result, indent=2)
        except (httpx.ConnectError, httpx.TimeoutException):
            return json.dumps(
                {
                    "error": "caldera_unreachable",
                    "message": (
                        f"Cannot reach Caldera MCP server at {self.base_url}. "
                        "Ensure the Caldera module is running on your Ignition gateway."
                    ),
                },
                indent=2,
            )
        except httpx.HTTPStatusError as exc:
            return json.dumps(
                {
                    "error": "caldera_http_error",
                    "status_code": exc.response.status_code,
                    "message": exc.response.text[:500],
                },
                indent=2,
            )

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
