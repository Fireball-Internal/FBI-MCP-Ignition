---
name: exploring
description: >
  Explore and navigate Ignition gateway project structure, resources, and data.
  Use when browsing views, scripts, named queries, UDTs, tags, or gateway event
  scripts. Use when the user asks "what exists", "where is", "how is this
  structured", "show me", or wants to understand project organization. Activates
  for any Caldera MCP exploration task - listing resources, reading views or
  scripts, browsing tags, checking project overview, or searching for components.
  Even if the user just says "look at the project" or "what's on this gateway",
  this skill applies.
---

# Exploring an Ignition Gateway

Help experienced Ignition developers understand what's on their gateway. Think of yourself as a
senior colleague who can instantly search the entire project, read any resource, and trace
relationships across views, scripts, tags, and queries.

**Be direct. Lead with findings, not preamble.** Answer the question first. Don't open with
gateway health summaries or status reports unless the user asked for them.

## First Interaction

On your first interaction with this gateway, silently call `caldera:get_gateway_health` to orient
yourself. Note the gateway version, bridge status, and project list for your own context. Do NOT
dump this to the user unless they ask or something is wrong. Check if this is a QA or production
server - if production, stop and warn the user immediately.

## Project Structure

Start broad, then drill down:

```
caldera:get_project_overview(project)       -> Resource counts: views, scripts, queries, UDTs, events
caldera:list_views(project)                 -> All view paths, scan for naming conventions
caldera:list_scripts(project)               -> Project library scripts
caldera:list_named_queries(project)         -> All named queries
caldera:list_udts(project)                  -> User Defined Types
caldera:list_gateway_scripts(project)       -> Timer, startup, shutdown, tag change, scheduled, message scripts
```

Cross-reference: use `caldera:find_view_usage(project, view_path)` to trace where a view is embedded.

## Reading Resources

Read things before guessing about them:

```
caldera:read_view(project, view_path)                             -> Summary for large views
caldera:read_view(project, view_path, summary=false)              -> Full JSON (careful with huge views)
caldera:read_component(project, view_path, "root/flex/label_0")   -> One specific component subtree
caldera:read_script(project, script_path)                         -> Project library script source
caldera:read_named_query(project, query_path)                     -> Query definition, parameters, SQL
caldera:read_udt(project, udt_path)                               -> UDT definition with tag structure
caldera:read_gateway_script(project, event_type, name)            -> Gateway event script code
caldera:read_page(project, page_path)                             -> Page configuration
```

For large views, prefer `caldera:read_component` for specific subtrees over pulling the entire view
JSON. Summary mode gives you the component tree so you can identify the path you need, then drill in.

## Exploring Tags

Tag paths always include the provider in brackets:

```
caldera:browse_tags("[default]")                  -> Top-level tag tree
caldera:browse_tags("[default]Motors")             -> Drill into a folder
caldera:read_tags(["[default]Motor1/Speed", "[default]Motor1/Current"])  -> Values + quality
```

Common providers: `[default]` for user tags, `[System]` for gateway system tags.
Start with `caldera:browse_tags("[default]")` and navigate from there.

Batch tag reads: `caldera:read_tags` accepts an array. One call with 20 paths is faster than 20
individual calls.

## Searching

```
caldera:search_views(project, query)            -> Search view names and paths
caldera:search_scripts(project, query)          -> Search script names
caldera:search_components(query, category)      -> Find component types by keyword or category
caldera:find_view_usage(project, view_path)     -> Where a view is used as an embedded child
```

## Visual Inspection

When Playwright is available:

```
caldera:screenshot_view(project, view_path)              -> See what a view looks like
caldera:screenshot_gateway_page("/web/status")           -> Gateway status pages
caldera:get_gateway_diagnostics()                        -> CPU, memory, threads (no browser needed)
caldera:list_perspective_sessions()                      -> Who's connected and viewing what
```

## Effectiveness Tips

1. **Read before you guess.** The gateway has the answers. Don't speculate when you can verify.
2. **Use view summaries for orientation.** Get the tree structure first, then `caldera:read_component` to drill into specific parts.
3. **Ground your answers.** Cite what you found: "I see you're using flex repeaters with embedded views for equipment screens in /Equipment/*".

For common multi-tool sequences organized by task, see [tool-patterns.md](../../reference/tool-patterns.md).
