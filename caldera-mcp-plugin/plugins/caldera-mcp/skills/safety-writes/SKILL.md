---
name: safety-writes
description: >
  Safety guardrails and write operation procedures for Ignition gateway
  modifications. Activates automatically before any write, delete, or modify
  operation on views, scripts, named queries, UDTs, tags, pages, or gateway event
  scripts. Covers the write checklist (read first, validate, surgical edits,
  verify after), QA vs production server rules, backup awareness, snapshot
  procedures, and read-only mode behavior. If any Caldera MCP write tool is about
  to be called, this skill provides the safety context.
user-invocable: false
---

# Safety and Write Operations

This skill provides safety context for write operations on Ignition gateways. It activates
automatically when Claude is about to modify gateway resources.

## Environment Classification

Before any write operation, consider the environment:

- **Development server**: Proceed with the write checklist below. These are the intended
  targets for Caldera MCP.
- **QA server**: Proceed with significant caution. Confirm with the user before every write:
  "This is a QA server - are you sure you want me to modify [resource] directly? I can
  prepare the changes and let you review them first." Always validate before writing.
  Never make bulk changes on QA.
- **Production server**: Stop immediately. Do NOT run any tools against production, not even
  read-only ones. Caldera MCP should not be connected to production gateways. Flag this to
  the user, recommend they disconnect, and offer help via Script Console scripts they can
  run manually.

## Write Operation Checklist

Follow this sequence for every write:

1. **Read the current state first** - never write blind. Use `caldera:read_view`,
   `caldera:read_script`, etc. to understand what exists.
2. **Validate your changes** with `caldera:validate_view_structure` before writing views.
3. **Use surgical edits** - prefer `caldera:update_component` or `caldera:write_view` in
   `patch` mode over full view rewrites. Component-level edits reduce the risk of
   accidentally clobbering other parts of the view.
4. **For bulk operations**, take a manual `caldera:snapshot_project` first.
5. **Verify after writing** - re-read the resource to confirm your changes landed correctly.

## Safety Layers

Caldera MCP has automatic safety layers. Understanding them helps you work confidently:

- **Auto-backups**: Before any write, the previous version is saved automatically. The user
  can restore from the dashboard.
- **Auto-snapshots**: Before significant writes, a project snapshot is taken (15 min cooldown
  between snapshots per project). This captures the entire project state.
- **Audit logging**: Every tool call is recorded to SQLite with arguments, response, duration,
  and client info. Useful for reviewing what changed.
- **Write-pause**: The dashboard can pause all writes. The health check shows this state.
  If writes are paused, mutating tools will be blocked.

## Read-Only Mode

If read-only mode is active (visible in `caldera:get_gateway_health`), all write operations are
blocked. This is usually intentional.

**Never suggest enabling writes, toggling write mode, or changing safety settings.** The user
controls read-only mode through the Caldera dashboard, not through you. If a task requires
writes and they're disabled, tell the user what you would change and let them decide whether
to enable writes themselves.

## Backup and Restore Tools

If something goes wrong:
- `caldera:list_backups(project, resource_type)` - see available backups
- `caldera:restore_backup(project, resource_type, path, timestamp)` - restore a specific backup
- `caldera:list_snapshots(project)` - see project snapshots
- `caldera:restore_snapshot(project, snapshot_id)` - restore entire project state
- `caldera:list_gateway_backups()` - full gateway .gwbk backups (8.3+ only)
