# Bridge Execution Context

`execute_script` runs Jython through the WebDev bridge, which differs from the Ignition Script Console in several ways.

## Contents
- Project library imports
- Return values
- Timeouts
- GUI access restrictions
- Named query scope
- Available scripting APIs

## Project Library Imports

Project library imports do not resolve in bridge context:
```python
# WRONG - ImportError in bridge context
from myproject.utils import helper

# RIGHT - inline the logic or use system APIs directly
```

Use `system.util.getProjectName()` to verify the execution context if needed.

## Return Values

The bridge captures the `_result` variable. This is the ONLY way to get structured data back:
```python
_result = {"status": "ok", "data": processed_data}
```

`print()` output goes to gateway stdout/logs but is not returned in the tool result.

## Timeouts

Long-running scripts may timeout. For heavy database queries:
- Limit result sets: `SELECT TOP 100 ...`
- Paginate if needed
- Use `system.db.runPrepQuery` for parameterized queries

## GUI Access Restrictions

These APIs are NOT available in bridge context:
- `system.gui.*` (Vision client only)
- `system.nav.*` (Vision client only)
- `system.perspective.openPopup` (session context only)

Available APIs:
- `system.tag.*` - tag reads, writes, configuration
- `system.db.*` - database queries, named queries
- `system.date.*` - date/time utilities
- `system.alarm.*` - alarm queries
- `system.util.*` - utility functions
- `system.opc.*` - OPC operations

## Named Query Scope

In gateway scope (where the bridge runs), named queries need the 3-argument form:
```python
# WRONG - fails or returns empty in gateway scope
system.db.runNamedQuery("queryPath", params)

# RIGHT - project name is required
system.db.runNamedQuery("projectName", "queryPath", params)
```

The project name is required because there's no implicit project context in gateway scope.
