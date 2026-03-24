"""Schema validation tools for Ignition Perspective components."""

from __future__ import annotations

import json
from typing import Any

import jsonschema

from ignition_lint.schemas import schema_path_for


def _load_schema(mode: str = "robust") -> dict[str, Any]:
    """Load a bundled Perspective component schema by mode name."""
    path = schema_path_for(mode)
    with open(path) as f:
        return json.load(f)


def validate_component_json(
    component_json: str, schema_mode: str = "robust"
) -> str:
    """Validate a raw Perspective component JSON string against the schema.

    Returns a JSON string with validation results including any errors.
    """
    try:
        component = json.loads(component_json)
    except json.JSONDecodeError as exc:
        return json.dumps(
            {"valid": False, "error": "invalid_json", "message": str(exc)}, indent=2
        )

    schema = _load_schema(schema_mode)

    errors: list[dict[str, Any]] = []
    validator = jsonschema.Draft7Validator(schema)
    for error in validator.iter_errors(component):
        errors.append(
            {
                "path": list(error.absolute_path),
                "message": error.message,
                "schema_path": list(error.absolute_schema_path),
            }
        )

    return json.dumps(
        {
            "valid": len(errors) == 0,
            "component_type": component.get("type", "unknown"),
            "error_count": len(errors),
            "errors": errors[:20],  # cap for readability
            "schema_mode": schema_mode,
        },
        indent=2,
    )


def get_component_types(schema_mode: str = "robust") -> str:
    """List all known ia.* component types from the bundled schema.

    Returns a JSON array of component type strings.
    """
    schema = _load_schema(schema_mode)

    types: set[str] = set()
    # Walk the schema looking for enum values on the 'type' field
    def _extract_types(node: Any) -> None:
        if isinstance(node, dict):
            if "properties" in node and "type" in node["properties"]:
                type_schema = node["properties"]["type"]
                if "enum" in type_schema:
                    types.update(type_schema["enum"])
                if "const" in type_schema:
                    types.add(type_schema["const"])
            # Walk oneOf / anyOf / allOf / items / definitions
            for key in ("oneOf", "anyOf", "allOf"):
                if key in node:
                    for item in node[key]:
                        _extract_types(item)
            if "items" in node:
                _extract_types(node["items"])
            for key in ("definitions", "$defs"):
                if key in node:
                    for defn in node[key].values():
                        _extract_types(defn)

    _extract_types(schema)

    sorted_types = sorted(t for t in types if isinstance(t, str) and t.startswith("ia."))
    return json.dumps(sorted_types, indent=2)
