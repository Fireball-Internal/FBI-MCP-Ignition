"""Tests for the unified FBI Ignition MCP server."""

from __future__ import annotations

import json

import pytest


def test_server_imports():
    """Server module imports without error."""
    from fbi_ignition_mcp import server  # noqa: F401

    assert server.mcp is not None
    assert server.mcp.name == "FBI MCP Ignition"


def test_validate_component_json_valid():
    """Valid component passes schema validation."""
    from fbi_ignition_mcp.schema_tools import validate_component_json

    component = json.dumps(
        {
            "type": "ia.display.label",
            "meta": {"name": "TestLabel"},
            "props": {"text": "Hello"},
        }
    )
    result = json.loads(validate_component_json(component, "permissive"))
    assert result["valid"] is True
    assert result["component_type"] == "ia.display.label"


def test_validate_component_json_invalid_json():
    """Malformed JSON returns an error."""
    from fbi_ignition_mcp.schema_tools import validate_component_json

    result = json.loads(validate_component_json("{bad json", "robust"))
    assert result["valid"] is False
    assert result["error"] == "invalid_json"


def test_list_component_types():
    """Component type listing returns ia.* types."""
    from fbi_ignition_mcp.schema_tools import get_component_types

    types = json.loads(get_component_types("robust"))
    assert isinstance(types, list)
    # Should have at least some types if the schema is valid
    if types:
        assert all(t.startswith("ia.") for t in types)


def test_caldera_proxy_construct():
    """CalderaProxy can be constructed with a custom URL."""
    from fbi_ignition_mcp.caldera_proxy import CalderaProxy

    proxy = CalderaProxy(base_url="http://test:9999/mcp")
    assert proxy.base_url == "http://test:9999/mcp"
    assert proxy.timeout == 30.0


@pytest.mark.asyncio
async def test_caldera_proxy_unreachable():
    """Calling a tool on an unreachable gateway returns a graceful error."""
    from fbi_ignition_mcp.caldera_proxy import CalderaProxy

    proxy = CalderaProxy(base_url="http://127.0.0.1:1/mcp", timeout=1.0)
    result = await proxy.call_tool("get_gateway_health", {})
    data = json.loads(result)
    assert data["error"] == "caldera_unreachable"
    await proxy.close()


@pytest.mark.asyncio
async def test_caldera_health_check_unreachable():
    """Health check on unreachable gateway returns connected=False."""
    from fbi_ignition_mcp.caldera_proxy import CalderaProxy

    proxy = CalderaProxy(base_url="http://127.0.0.1:1/mcp", timeout=1.0)
    result = await proxy.health_check()
    assert result["connected"] is False
    await proxy.close()
