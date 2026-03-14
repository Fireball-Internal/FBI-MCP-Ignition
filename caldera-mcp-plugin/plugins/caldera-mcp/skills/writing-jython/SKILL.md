---
name: writing-jython
description: >
  Write and execute Jython 2.7 scripts on the Ignition gateway via execute_script
  and script sessions. Use when the user needs to probe databases, inspect tags,
  test expressions, run named queries, or perform any gateway-side investigation
  via scripting. Covers Jython 2.7 syntax rules (no f-strings, no walrus
  operator, no type hints), bridge execution context limitations, the _result
  return pattern, and script session management for iterative debugging. If the
  user needs to run code on the gateway or you need to test a hypothesis by
  executing a script, this skill applies.
---

# Writing and Executing Jython Scripts

`caldera:execute_script` runs Jython 2.7 on the gateway with full access to the Ignition
scripting API. This is your Swiss Army knife for troubleshooting: query databases, inspect tags,
test expressions, trace data flows, and validate hypotheses about system behavior.

**Be direct. Lead with findings, not preamble.**

## First Interaction

On your first interaction with this gateway, silently call `caldera:get_gateway_health` to orient
yourself. Note the gateway version, bridge status, and project list for your own context. Do NOT
dump this to the user unless they ask or something is wrong. Check if this is a QA or production
server - if production, stop and warn the user immediately.

## Probing Database Issues

Write and run queries directly to debug data problems:

```python
caldera:execute_script("""
results = system.db.runNamedQuery("project", "Equipment/GetAlarms", {"areaId": 42})
_result = {
    "rowCount": results.rowCount,
    "columns": list(results.columnNames),
    "sample": [
        {col: results.getValueAt(r, col) for col in results.columnNames}
        for r in range(min(5, results.rowCount))
    ]
}
""")
```

For raw SQL:
```python
caldera:execute_script("""
ds = system.db.runQuery("SELECT TOP 10 * FROM alarm_events ORDER BY eventtime DESC", "MyDB")
_result = {
    "columns": list(ds.columnNames),
    "rows": [
        {col: str(ds.getValueAt(r, col)) for col in ds.columnNames}
        for r in range(ds.rowCount)
    ]
}
""")
```

## Inspecting Tag Configuration

```python
caldera:execute_script("""
config = system.tag.getConfiguration("[default]Motors/Motor1", True)
tag_list = list(config)
if tag_list:
    tag = tag_list[0]
    _result = {
        "name": str(tag.get("name", "")),
        "tagType": str(tag.get("tagType", "")),
        "valueSource": str(tag.get("valueSource", "")),
        "dataType": str(tag.get("dataType", "")),
        "opcServer": str(tag.get("opcServer", "")),
        "opcItemPath": str(tag.get("opcItemPath", ""))
    }
else:
    _result = {"error": "Tag not found"}
""")
```

## Testing Expressions

Replicate what an expression binding would do:
```python
caldera:execute_script("""
result = system.tag.readBlocking(["[default]Motor1/Speed"])[0]
speed = result.value
status = "Running" if speed > 0 else "Stopped"
color = "#22C55E" if speed > 0 else "#EF4444"
_result = {"speed": speed, "quality": str(result.quality), "status": status, "color": color}
""")
```

## Script Sessions

For iterative investigation where you build up context step by step:

```
caldera:script_session_start()                        -> Returns session_id
caldera:script_session_eval(session_id, code_step_1)  -> Run first probe, inspect result
caldera:script_session_eval(session_id, code_step_2)  -> Dig deeper, variables persist
caldera:script_session_eval(session_id, code_step_3)  -> Continue investigation
caldera:script_session_end(session_id)                -> Clean up when done
```

Sessions are ideal when you don't know what you're looking for yet. Variables persist across
calls. They timeout after 1 hour.

## Jython 2.7 Syntax

Scripts run in Jython 2.7, NOT Python 3. The most common traps: no f-strings, no dict unpacking
(`{**a, **b}`), no walrus operator, no type hints, integer division returns int.

For the complete syntax reference with examples, see [jython-syntax.md](../../reference/jython-syntax.md).

## Bridge Execution Context

The bridge differs from the Script Console: no project library imports, return values via
`_result` only, named queries need the 3-argument form with project name.

For the full bridge reference, see [bridge-context.md](../../reference/bridge-context.md).

## Providing Scripts for QA/Production

When debugging QA/production (where Caldera MCP shouldn't be connected), develop and test on dev
first, then provide a Script Console version:

```python
# Script Console version - paste into Ignition Designer Script Console
# Investigates: [describe what this checks]
results = system.db.runNamedQuery("project", "path/to/query", {"param": value})
for row in range(results.rowCount):
    print("{}: {}".format(
        results.getValueAt(row, "name"),
        results.getValueAt(row, "status")
    ))
```

Use `caldera:validate_script(code)` to syntax-check before running if unsure.
