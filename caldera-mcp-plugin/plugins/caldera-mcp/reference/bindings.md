# Perspective Binding Reference

## Contents
- Binding types overview
- Tag bindings
- Expression bindings
- Property bindings
- Query bindings

## Binding Types Overview

| Type | Config key | Use case |
|------|-----------|----------|
| `tag` | `config.tagPath` | Direct tag value display |
| `expr` | `config.expression` | Computed values, conditionals |
| `property` | `config.path` | Cross-component references |
| `query` | `config.queryPath` | Named query results |

## Tag Bindings

Config uses `tagPath` (not `path`):
```json
{
  "type": "tag",
  "config": {
    "tagPath": "[default]Motors/Motor1/Speed"
  }
}
```

`{value}` in transforms refers to the tag's current value.

## Expression Bindings

Use `tag()` function to read tags inside expressions:
```
tag('[default]Motors/Motor1/Speed') * 9.0 / 5.0 + 32
```

A bare tag path string is just a string literal, not a tag read.

Available functions: check with `caldera:get_expression_reference(function_name)` or `caldera:get_expression_reference(category="math")`.

## Property Bindings

Reference other component properties:
```json
{
  "type": "property",
  "config": {
    "path": "this.custom.selectedItem"
  }
}
```

## Query Bindings

Reference named queries:
```json
{
  "type": "query",
  "config": {
    "queryPath": "Equipment/GetAlarms",
    "polling": { "rate": 5000 },
    "parameters": {
      "areaId": "{this.custom.selectedArea}"
    }
  }
}
```

For binding schema details, use `caldera:get_binding_schema(type)` where type is "tag", "expr", "property", or "query".
