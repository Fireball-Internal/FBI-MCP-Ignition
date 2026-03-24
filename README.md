# FBI Ignition MCP Server

Unified MCP server for Ignition SCADA development — combines Caldera execution tools, ignition-lint validation, and Perspective component schemas.

## Quick Start

```bash
uv sync --extra dev
uv run fbi-ignition-mcp
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CALDERA_MCP_URL` | `http://localhost:8765/mcp` | Caldera MCP server URL on your Ignition gateway |
