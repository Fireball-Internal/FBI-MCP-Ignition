# Caldera MCP Plugin - Installation Guide

This guide describes how to install and setup the Caldera MCP Plugin for connecting Claude Code (or other MCP-compatible clients) to an Ignition SCADA gateway.

## Prerequisites
- Node.js (v18 or higher)
- Ignition SCADA Gateway running
- An MCP Client (e.g., Claude Desktop, Claude Code, Cursor)

## Installation Steps

1. **Navigate to the Caldera MCP Plugin directory:**
   ```bash
   cd c:\codebase\FBI-MCP-Ignition\caldera-mcp-plugin
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Build the project:**
   ```bash
   npm run build
   ```

## Configuration

You must configure your MCP client to start the Caldera MCP server. 

### Claude Desktop Example (`claude_desktop_config.json`)

Add the following to your configuration file, ensuring you replace the `args` with the absolute path to the compiled `index.js` file:

```json
{
  "mcpServers": {
    "caldera-ignition": {
      "command": "node",
      "args": [
        "C:\\codebase\\FBI-MCP-Ignition\\caldera-mcp-plugin\\build\\index.js"
      ],
      "env": {
        "IGNITION_URL": "http://localhost:8088",
        "IGNITION_USERNAME": "admin",
        "IGNITION_PASSWORD": "password"
      }
    }
  }
}
```

## Running

Once configured, restart your MCP client. The client will automatically start the Caldera MCP server and you will have access to the Ignition-specific tools.
