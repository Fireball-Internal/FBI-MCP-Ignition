#!/usr/bin/env python3
"""FBI Ignition MCP Server — unified Ignition SCADA tooling.

Combines:
- Caldera MCP gateway proxy (execution tools)
- ignition-lint (validation tools)
- WhiskeyHouse Perspective component schemas
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Import ignition-lint tools
# ---------------------------------------------------------------------------
from ignition_lint.server import (
    check_linter_status as _il_check_linter_status,
)
from ignition_lint.server import (
    lint_ignition_project as _il_lint_ignition_project,
)
from ignition_lint.server import (
    lint_jython_scripts as _il_lint_jython_scripts,
)
from ignition_lint.server import (
    lint_perspective_components as _il_lint_perspective_components,
)

from .caldera_proxy import CalderaProxy
from .schema_tools import get_component_types, validate_component_json

# ---------------------------------------------------------------------------
# Reference docs path (Caldera plugin reference material)
# ---------------------------------------------------------------------------
_REFERENCE_DIR = (
    Path(__file__).resolve().parents[2]
    / "caldera-mcp-plugin"
    / "plugins"
    / "caldera-mcp"
    / "reference"
)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------
mcp = FastMCP(
    "FBI MCP Ignition",
    instructions=(
        "Unified MCP server for Ignition SCADA development. "
        "Provides linting/validation tools (offline) and Caldera gateway "
        "proxy tools (requires live Ignition gateway). "
        "Use lint/schema tools to validate code before deploying via Caldera."
    ),
)

# Caldera proxy — singleton, lazy-inited on first gateway tool call
_proxy: CalderaProxy | None = None


def _get_proxy() -> CalderaProxy:
    global _proxy
    if _proxy is None:
        _proxy = CalderaProxy()
    return _proxy


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: Lint tools (from ignition-lint)
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
def check_linter_status() -> str:
    """Check ignition-lint schema availability and configuration."""
    return _il_check_linter_status()


@mcp.tool()
def lint_perspective_components(
    project_path: str,
    component_type: str | None = None,
    verbose: bool = False,
    ignore_codes: str | None = None,
) -> str:
    """Lint Perspective view components in an Ignition project directory.

    Args:
        project_path: Path to the Ignition project root.
        component_type: Optional filter for specific component type (e.g. "ia.display.label").
        verbose: Include extra detail in output.
        ignore_codes: Comma-separated lint codes to suppress.
    """
    return _il_lint_perspective_components(
        project_path, component_type, verbose, ignore_codes
    )


@mcp.tool()
def lint_jython_scripts(
    project_path: str,
    verbose: bool = False,
    ignore_codes: str | None = None,
) -> str:
    """Lint Jython/Python scripts in an Ignition project directory.

    Args:
        project_path: Path to the Ignition project root.
        verbose: Include extra detail in output.
        ignore_codes: Comma-separated lint codes to suppress.
    """
    return _il_lint_jython_scripts(project_path, verbose, ignore_codes)


@mcp.tool()
def lint_ignition_project(
    project_path: str,
    lint_type: str = "all",
    component_type: str | None = None,
    verbose: bool = False,
    ignore_codes: str | None = None,
) -> str:
    """Comprehensive linting for an entire Ignition project.

    Runs Perspective component validation, naming convention checks, and
    Jython script analysis in one pass.

    Args:
        project_path: Path to the Ignition project root.
        lint_type: What to lint — "all", "perspective", "naming", or "scripts".
        component_type: Optional component type filter.
        verbose: Include extra detail in output.
        ignore_codes: Comma-separated lint codes to suppress.
    """
    return _il_lint_ignition_project(
        project_path, lint_type, component_type, verbose, ignore_codes
    )


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: Schema validation tools (WhiskeyHouse schemas)
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
def validate_component_json_tool(
    component_json: str,
    schema_mode: str = "robust",
) -> str:
    """Validate raw Perspective component JSON against empirical schemas.

    Pass the full JSON of a single Perspective component (with type, meta,
    props, children).  Returns structured validation results with any errors.

    Args:
        component_json: A JSON string of a Perspective component.
        schema_mode: Schema strictness — "robust" (recommended) or "permissive".
    """
    return validate_component_json(component_json, schema_mode)


@mcp.tool()
def list_component_types(schema_mode: str = "robust") -> str:
    """List all known Ignition Perspective ia.* component types.

    Returns a JSON array of component type identifiers recognized by the schema.

    Args:
        schema_mode: Schema to inspect — "robust" or "permissive".
    """
    return get_component_types(schema_mode)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: Caldera gateway proxy tools
# ═══════════════════════════════════════════════════════════════════════════


@mcp.tool()
async def caldera_health() -> str:
    """Check connectivity to the Caldera MCP server on the Ignition gateway."""
    proxy = _get_proxy()
    result = await proxy.health_check()
    return json.dumps(result, indent=2)


# ---------------------------------------------------------------------------
# Caldera proxy tool factory
# ---------------------------------------------------------------------------

def _make_caldera_tool(
    tool_name: str, description: str, params: dict[str, Any] | None = None
):
    """Create and register a Caldera proxy tool on the MCP server.

    Uses exec() to generate functions with explicit parameter signatures
    because FastMCP v2 rejects **kwargs in tool functions.
    """
    if params:
        param_names = list(params.keys())
        sig_parts = ", ".join(f"{name}: str = ''" for name in param_names)
        body_dict = ", ".join(f"'{name}': {name}" for name in param_names)

        func_code = f"""
async def {tool_name}({sig_parts}) -> str:
    proxy = _get_proxy()
    args = {{{body_dict}}}
    # Strip empty defaults so we don't send blank strings
    args = {{k: v for k, v in args.items() if v != ''}}
    return await proxy.call_tool('{tool_name}', args)
"""
        local_ns: dict[str, Any] = {"_get_proxy": _get_proxy}
        exec(func_code, local_ns)  # noqa: S102
        fn = local_ns[tool_name]

        param_docs = "\n".join(
            f"        {name}: {info.get('description', '')}"
            for name, info in params.items()
        )
        fn.__doc__ = f"{description}\n\n    Args:\n{param_docs}"
        mcp.tool(name=tool_name)(fn)
    else:
        async def _proxy_tool_no_args() -> str:
            proxy = _get_proxy()
            return await proxy.call_tool(tool_name, {})

        _proxy_tool_no_args.__doc__ = description
        _proxy_tool_no_args.__name__ = tool_name
        mcp.tool(name=tool_name)(_proxy_tool_no_args)


# -- Gateway & connectivity ------------------------------------------------

_make_caldera_tool("get_gateway_health", "Get Ignition gateway health status and diagnostics.")
_make_caldera_tool("get_connection_status", "Check MCP-to-Ignition connectivity status.")
_make_caldera_tool(
    "get_project_overview",
    "Get overview of an Ignition project — resource counts for views, scripts, queries, UDTs.",
    {"project": {"description": "Ignition project name"}},
)

# -- Views -----------------------------------------------------------------

_make_caldera_tool(
    "list_views",
    "List all Perspective view paths in a project.",
    {"project": {"description": "Ignition project name"}},
)
_make_caldera_tool(
    "read_view",
    "Read a Perspective view structure and bindings.",
    {
        "project": {"description": "Ignition project name"},
        "view_path": {"description": "Path to the view (e.g. 'Main/Overview')"},
    },
)
_make_caldera_tool(
    "write_view",
    "Write or update a Perspective view. Use with caution.",
    {
        "project": {"description": "Ignition project name"},
        "view_path": {"description": "Path to the view"},
        "view_json": {"description": "Full view JSON to write"},
    },
)
_make_caldera_tool(
    "read_component",
    "Read a specific component from a Perspective view.",
    {
        "project": {"description": "Ignition project name"},
        "view_path": {"description": "Path to the view"},
        "component_path": {"description": "Dot-delimited component path (e.g. 'root/flex/label')"},
    },
)
_make_caldera_tool(
    "search_views",
    "Search view names/paths by keyword.",
    {
        "project": {"description": "Ignition project name"},
        "query": {"description": "Search keyword"},
    },
)
_make_caldera_tool(
    "search_components",
    "Search for component types by keyword.",
    {"query": {"description": "Search keyword"}},
)
_make_caldera_tool(
    "find_view_usage",
    "Find where a view is embedded as a child in other views.",
    {
        "project": {"description": "Ignition project name"},
        "view_path": {"description": "Path of the view to search for"},
    },
)
_make_caldera_tool(
    "screenshot_view",
    "Take a screenshot of a Perspective view (requires Playwright on gateway).",
    {
        "project": {"description": "Ignition project name"},
        "view_path": {"description": "Path to the view"},
    },
)
_make_caldera_tool(
    "get_view_console_errors",
    "Get runtime JS/binding console errors from a Perspective view.",
    {
        "project": {"description": "Ignition project name"},
        "view_path": {"description": "Path to the view"},
    },
)

# -- Tags ------------------------------------------------------------------

_make_caldera_tool(
    "browse_tags",
    "Browse the Ignition tag tree at a given path.",
    {"path": {"description": "Tag path to browse (e.g. '[default]' or '[default]Folder')"}},
)
_make_caldera_tool(
    "read_tags",
    "Read values and quality for one or more tags. Accepts an array of paths.",
    {"tag_paths": {"description": "JSON array of tag paths to read"}},
)
_make_caldera_tool(
    "write_tags",
    "Write values to one or more tags. Use with caution.",
    {"tag_writes": {"description": "JSON array of {path, value} objects"}},
)

# -- Scripts ---------------------------------------------------------------

_make_caldera_tool(
    "list_scripts",
    "List project library scripts.",
    {"project": {"description": "Ignition project name"}},
)
_make_caldera_tool(
    "read_script",
    "Read a project library script's source code.",
    {
        "project": {"description": "Ignition project name"},
        "script_path": {"description": "Script resource path"},
    },
)
_make_caldera_tool(
    "execute_script",
    "Execute a Jython script on the Ignition gateway.",
    {"code": {"description": "Jython 2.7 code to execute"}},
)
_make_caldera_tool(
    "script_session_start",
    "Start an interactive Jython script session.",
    {},
)
_make_caldera_tool(
    "script_session_eval",
    "Evaluate code in an active script session.",
    {
        "session_id": {"description": "Session ID from script_session_start"},
        "code": {"description": "Jython code to evaluate"},
    },
)
_make_caldera_tool(
    "script_session_end",
    "End an interactive script session.",
    {"session_id": {"description": "Session ID to close"}},
)
_make_caldera_tool(
    "list_gateway_scripts",
    "List gateway event scripts (timer, startup, shutdown, tag change, etc.).",
    {"project": {"description": "Ignition project name"}},
)

# -- Database / Named Queries ----------------------------------------------

_make_caldera_tool(
    "list_named_queries",
    "List all named queries in a project.",
    {"project": {"description": "Ignition project name"}},
)
_make_caldera_tool(
    "run_named_query",
    "Execute a named query and return results.",
    {
        "project": {"description": "Ignition project name"},
        "query_path": {"description": "Named query path"},
        "parameters": {"description": "Optional JSON object of query parameters"},
    },
)

# -- UDTs ------------------------------------------------------------------

_make_caldera_tool(
    "list_udts",
    "List User Defined Types in a project.",
    {"project": {"description": "Ignition project name"}},
)

# -- Design ----------------------------------------------------------------

_make_caldera_tool(
    "get_component_schema",
    "Get the schema definition for a specific Perspective component type.",
    {"component_type": {"description": "Component type (e.g. 'ia.display.label')"}},
)
_make_caldera_tool(
    "get_binding_schema",
    "Get the schema for a binding type.",
    {"binding_type": {"description": "Binding type name"}},
)
_make_caldera_tool(
    "get_expression_reference",
    "Get expression language reference documentation.",
    {},
)
_make_caldera_tool(
    "get_design_guidance",
    "Get design guidance and best practices for Perspective development.",
    {},
)
_make_caldera_tool(
    "search_icons",
    "Search available Material Design icons by keyword.",
    {"query": {"description": "Icon search keyword"}},
)

# -- Project Management ----------------------------------------------------

_make_caldera_tool(
    "snapshot_project",
    "Create a snapshot/backup of an Ignition project.",
    {"project": {"description": "Ignition project name"}},
)
_make_caldera_tool(
    "get_gateway_diagnostics",
    "Get detailed gateway diagnostic information.",
    {},
)


# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: Resources — reference docs & linter info
# ═══════════════════════════════════════════════════════════════════════════


def _read_reference(filename: str) -> str:
    """Read a Caldera reference doc, returning its content or a fallback."""
    path = _REFERENCE_DIR / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return f"Reference file '{filename}' not found at {path}"


@mcp.resource("ignition://reference/bindings")
def ref_bindings() -> str:
    """Ignition binding types reference — property, tag, expression, query, etc."""
    return _read_reference("bindings.md")


@mcp.resource("ignition://reference/jython-syntax")
def ref_jython_syntax() -> str:
    """Jython 2.7 syntax rules, gotchas, and Ignition-specific patterns."""
    return _read_reference("jython-syntax.md")


@mcp.resource("ignition://reference/perspective-pitfalls")
def ref_perspective_pitfalls() -> str:
    """Common Perspective development pitfalls and how to avoid them."""
    return _read_reference("perspective-pitfalls.md")


@mcp.resource("ignition://reference/tool-patterns")
def ref_tool_patterns() -> str:
    """Recommended multi-tool sequences for common Ignition tasks."""
    return _read_reference("tool-patterns.md")


@mcp.resource("ignition://reference/bridge-context")
def ref_bridge_context() -> str:
    """Ignition bridge context and scripting gateway reference."""
    return _read_reference("bridge-context.md")


@mcp.resource("ignition://linter/status")
def linter_status() -> str:
    """Ignition linter configuration and schema availability."""
    return _il_check_linter_status()


# ═══════════════════════════════════════════════════════════════════════════
# Entry point
# ═══════════════════════════════════════════════════════════════════════════


def main() -> None:
    """Launch the FBI Ignition MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
