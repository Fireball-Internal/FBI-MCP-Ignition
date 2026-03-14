# Caldera MCP Plugin

Connect Claude to your Ignition SCADA gateway through [Caldera MCP](https://github.com/caldera-mcp/caldera-mcp), providing 71+ tools and 5 domain skills for exploration, debugging, diagnostics, and development planning.

## Install

### Claude Code (plugin with skills + tools)

```bash
/plugin marketplace add jaedync/caldera-mcp-plugin
/plugin install caldera-mcp@caldera-mcp
```

Includes 5 workflow skills, shared reference files, and MCP server connection.

### Claude Desktop (tools only)

Download `caldera-mcp.mcpb` from [Releases](https://github.com/jaedync/caldera-mcp-plugin/releases), then open it to install. You'll be prompted for your Caldera MCP server URL (default: `http://localhost:8765/mcp`).

Or build from source:

```bash
cd desktop-extension
bash build.sh
open caldera-mcp.mcpb
```

### Local development (Claude Code)

```bash
claude --plugin-dir ./caldera-mcp-plugin
```

## Prerequisites

- [Caldera MCP server](https://github.com/caldera-mcp/caldera-mcp) running on your Ignition gateway
- **Claude Code**: v1.0.33+
- **Claude Desktop**: v0.10.0+

## What's included

### Skills (Claude Code only)

| Skill | Triggers when | What it provides |
|-------|--------------|-----------------|
| `exploring` | Browsing project structure, listing resources | Project navigation, tag exploration, search patterns |
| `debugging-views` | Broken bindings, layout issues, data not flowing | Binding trace workflow, silent failure catalog |
| `writing-jython` | Running scripts, probing databases, testing expressions | Jython 2.7 syntax rules, bridge context, script sessions |
| `planning` | Feature requests, building new screens | Pattern analysis, component schemas, design guidance |
| `safety-writes` | Any write/delete operation (auto-activates) | Write checklist, environment classification, backup awareness |

### Tools (both platforms)

71+ tools across these categories:

| Category | Examples |
|----------|----------|
| Views | `read_view`, `list_views`, `read_component`, `search_components` |
| Tags | `browse_tags`, `read_tags`, `write_tags` |
| Scripts | `execute_script`, `script_session_start/eval/end`, `read_script` |
| Database | `run_named_query`, `list_named_queries` |
| Schemas | `get_component_schema`, `get_binding_schema`, `get_expression_reference` |
| Design | `get_design_guidance`, `search_icons` |
| Visual | `screenshot_view`, `get_view_console_errors` |
| Gateway | `get_gateway_health`, `get_gateway_diagnostics` |

## Configuration

### Claude Code

Edit `plugins/caldera-mcp/.mcp.json`:

```json
{
  "mcpServers": {
    "caldera-mcp": {
      "type": "http",
      "url": "http://your-host:your-port/mcp"
    }
  }
}
```

### Claude Desktop

The server URL is configurable during extension installation. Default: `http://localhost:8765/mcp`.

## How it works

```
Claude Code    <--HTTP-->   Caldera MCP Server  <-->  Ignition Gateway
Claude Desktop <--stdio-->  mcp-remote  <--HTTP-->  Caldera MCP Server  <-->  Ignition Gateway
```

## License

MIT
