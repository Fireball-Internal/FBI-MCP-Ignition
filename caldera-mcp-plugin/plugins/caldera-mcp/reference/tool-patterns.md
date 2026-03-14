# Common Tool Sequences

Multi-tool patterns organized by task. Each pattern shows the recommended order of tool calls.

## Contents
- Understanding a project
- Finding a specific resource
- Investigating data flow
- Checking tag health
- Analyzing a view

## Understanding a Project

Start broad, then drill down:
```
caldera:get_project_overview(project)       -> Resource counts: views, scripts, queries, UDTs, events
caldera:list_views(project)                 -> All view paths, scan for naming conventions
caldera:list_scripts(project)               -> Project library scripts
caldera:list_named_queries(project)         -> All named queries
caldera:list_udts(project)                  -> User Defined Types
caldera:list_gateway_scripts(project)       -> Timer, startup, shutdown, tag change, scheduled, message scripts
```

## Finding a Specific Resource

When the user asks "where is X?" or "how does Y work?":
```
caldera:search_views(project, query)        -> Search view names/paths
caldera:search_scripts(project, query)      -> Search script names
caldera:find_view_usage(project, view_path) -> Where a view is embedded as a child
caldera:search_components(query)            -> Find component types by keyword
```

## Investigating Data Flow

Trace how data moves from source to display:
```
1. caldera:read_view(project, view_path)                       -> View structure + bindings
2. caldera:read_component(project, view_path, component_path)  -> Specific component detail
3. caldera:read_tags(tag_paths)                                 -> Check tag values + quality
4. caldera:execute_script(code)                                 -> Test query/expression logic
5. caldera:get_view_console_errors(project, view_path)          -> Runtime JS/binding errors
```

## Checking Tag Health

```
1. caldera:browse_tags("[default]")                    -> Top-level tag structure
2. caldera:browse_tags("[default]FolderName")          -> Drill into folders
3. caldera:read_tags(["[default]Tag1", "[default]Tag2"])  -> Values + quality for multiple tags
4. caldera:execute_script(...)                         -> Deep tag config inspection via system.tag.getConfiguration
```

Batch tag reads: `caldera:read_tags` accepts an array. One call with 20 paths is faster than 20 individual calls.

## Analyzing a View

For large views, use summary mode then drill in:
```
1. caldera:read_view(project, path)                      -> Summary: component tree structure
2. caldera:read_component(project, path, "root/flex/...")  -> Specific subtree with full detail
3. caldera:screenshot_view(project, path)                 -> Visual rendering (requires Playwright)
4. caldera:get_view_console_errors(project, path)         -> Runtime errors (requires Playwright)
```

Prefer `read_component` for targeted reads over `read_view(summary=false)` on large views.
