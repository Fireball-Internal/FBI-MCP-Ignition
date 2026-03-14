# Perspective Silent Failure Catalog

These cause silent failures with no error messages. Check for ALL of them when debugging views.

## Contents
- Flex container style vs props
- Embedded view paramDirection
- Dropdown option format
- Tag path provider brackets
- Tag binding config key
- Table column render property
- Transform chain {value} semantics
- Expression binding tag references
- Cross-view communication

## Flex Container: style vs props

Layout CSS goes in `props.style`, not directly in `props`. This is the #1 Perspective trap.

```json
// WRONG - silently ignored, container defaults to row
{"props": {"flexDirection": "column"}}

// RIGHT - CSS properties go in style
{"props": {"style": {"flexDirection": "column"}}}
```

The component also has a native `props.direction` property, but CSS in `props.style` is the standard Perspective convention.

## Embedded View paramDirection

The TARGET view must have `paramDirection: "input"` on each parameter it accepts from a parent, or parent-provided values are silently ignored. Diagnose from JSON (`propConfig` will be empty or missing `paramDirection`). The fix is done in the Perspective Designer, not JSON.

## Dropdown Option Format

Options MUST be an array of `{value, label}` objects. Plain string arrays render but bind incorrectly:

```json
// WRONG - renders but value binding is broken
"options": ["Manual", "Auto", "Off"]

// RIGHT - proper value/label separation
"options": [
  {"value": 0, "label": "Manual"},
  {"value": 1, "label": "Auto"},
  {"value": 2, "label": "Off"}
]
```

## Tag Path Provider Brackets

Tag paths MUST include the provider in brackets. Without it, Ignition returns `Bad_NotFound` with `"Tag provider '' not found"`:

```
WRONG: WaterTreatment/ClearWell/Level
RIGHT: [default]WaterTreatment/ClearWell/Level
```

## Tag Binding Config Key

In view JSON, tag binding configurations use `config.tagPath`, not `config.path`. Using `config.path` causes the binding to resolve to null with no error.

## Table Column Render Property

Table columns use `render` for cell rendering configuration (progress bars, toggles), not `renderer` or `cellRenderer`. Check `caldera:get_component_schema("ia.display.table")` for the exact format.

## Transform Chain: {value} Changes Meaning

When a binding has multiple transforms, each transform's `{value}` is the output of the previous transform, not the original binding value:

```
Tag binding: [default]ClearWell/Temperature -> 18.7 (Celsius)
Transform 1 (expression): {value} * 9.0 / 5.0 + 32    -> 65.66 (Fahrenheit)
Transform 2 (expression): if({value} > 50, 'HIGH', 'NORMAL')
                          -> {value} is 65.66 (F), NOT 18.7 (C)!
```

If a threshold check is wrong after a unit conversion, check whether the threshold accounts for the converted units.

## Expression Binding Tag References

In expression bindings (`type: "expr"`), use the `tag()` function to read tag values. A tag path as a string literal is just a string:

```
WRONG (string literal, not a tag read):
  concat('Level: ', '[default]WaterTreatment/ClearWell/Level', '%')
  -> Shows: "Level: [default]WaterTreatment/ClearWell/Level%"

RIGHT (tag() function reads the value):
  concat('Level: ', tag('[default]WaterTreatment/ClearWell/Level'), '%')
  -> Shows: "Level: 72.3%"
```

## Cross-View Communication

View parameters (`view.params`) only flow parent -> child through embedded views. They do NOT work for:
- Direct page navigation (typing a URL or using nav actions)
- Sibling views at the same level
- Communication between docked views and the main page

When a parameterized view works embedded but shows defaults when navigated directly, the params aren't being provided because there's no parent. Solutions:

1. **URL parameters** - `/view-path?pumpPath=...` (configure in page config)
2. **Session custom properties** - `session.custom.selectedPump` (shared across session)
3. **Page params** - default values in page configuration
4. **Detect standalone mode** - check if params are empty, show selector

Use `caldera:validate_view_structure(view_json)` to catch many of these automatically.
