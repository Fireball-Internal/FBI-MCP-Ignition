---
name: debugging-views
description: >
  Debug Ignition Perspective view issues including broken bindings, missing data,
  Bad_NotFound tag quality, silent component failures, and layout problems. Use
  when a view isn't displaying correctly, data isn't flowing through bindings,
  components behave unexpectedly, or the user mentions any Perspective debugging
  scenario. Also covers tracing transform chains, checking tag paths, diagnosing
  expression bindings, and using screenshots or console errors to identify
  problems. If something looks wrong in a Perspective view, this skill applies.
---

# Debugging Perspective Views

Help experienced Ignition developers trace and fix view issues. Perspective has many silent
failure modes where components look fine but data doesn't flow. Your job is to systematically
trace the data path from source to display and identify where it breaks.

**Be direct. Lead with findings, not preamble.**

## First Interaction

On your first interaction with this gateway, silently call `caldera:get_gateway_health` to orient
yourself. Note the gateway version, bridge status, and project list for your own context. Do NOT
dump this to the user unless they ask or something is wrong. Check if this is a QA or production
server - if production, stop and warn the user immediately.

## Binding Trace Workflow

When a view isn't displaying data correctly, follow this sequence:

1. `caldera:read_view(project, view_path)` - check view structure and bindings
2. `caldera:read_component(project, view_path, component_path)` - zoom into the broken component
3. Examine its bindings: what tags, expressions, or queries is it bound to?
4. Use `caldera:execute_script` or `caldera:read_tags` to check if the data source returns expected values
5. `caldera:get_view_console_errors(project, view_path)` - capture runtime JS errors and binding failures (requires Playwright)
6. `caldera:screenshot_view(project, view_path)` - see what it actually looks like

## Understanding Component Schemas

When a component isn't behaving as expected:

```
caldera:search_components(query="table")              -> Find the exact type name
caldera:get_component_schema("ia.display.table")      -> Full property schema, events, examples
caldera:get_binding_schema("tag")                     -> How tag bindings work
caldera:get_expression_reference(function_name="if")  -> Expression language reference
```

## Common Silent Failures

Perspective has specific pitfalls that cause silent failures with no error messages. When
debugging a view, check for these common traps:

- Flex container CSS in `props` instead of `props.style`
- Missing `paramDirection: "input"` on embedded view params
- Dropdown options as string arrays instead of `{value, label}` objects
- Tag paths missing `[default]` provider brackets
- `config.path` instead of `config.tagPath` in tag bindings
- `renderer` instead of `render` in table column config

For the full catalog with examples and fixes, see [perspective-pitfalls.md](../../reference/perspective-pitfalls.md).

## Transform Chain Debugging

When a binding has multiple transforms, each transform's `{value}` is the output of the previous
transform, not the original binding value. If a threshold check seems wrong after a unit
conversion transform, check whether the threshold accounts for the converted units.

## Expression vs Tag Bindings

In expression bindings, use `tag()` to read tag values. A bare tag path is just a string literal:

```
WRONG: concat('Level: ', '[default]ClearWell/Level', '%')
RIGHT: concat('Level: ', tag('[default]ClearWell/Level'), '%')
```

For full binding reference, see [bindings.md](../../reference/bindings.md).

## Using Scripts for Diagnosis

When you need to test a hypothesis about data flow, use `caldera:execute_script` to probe the
gateway directly. This is the fastest way to verify whether a data source returns what's expected.

For Jython 2.7 syntax rules (critical when writing diagnostic scripts), see [jython-syntax.md](../../reference/jython-syntax.md).

## Validation

Use `caldera:validate_view_structure(view_json)` to automatically check for many common issues
before writing changes.
