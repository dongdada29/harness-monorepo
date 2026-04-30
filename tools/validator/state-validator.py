#!/usr/bin/env python3
"""
State Schema Validator — Validates harness state.json against state.v2.schema.json.

Usage:
  python3 state-validator.py <state-file> [--schema <schema-file>]
"""
import argparse
import json
import sys
import typing
from pathlib import Path

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
NC = "\033[0m"
BOLD = "\033[1m"


def ok(msg: str) -> str: return f"{GREEN}✅{NC}  {msg}"
def fail(msg: str) -> str: return f"{RED}❌{NC}  {msg}"
def warn(msg: str) -> str: return f"{YELLOW}⚠️{NC}  {msg}"
def bold(msg: str) -> str: return f"{BOLD}{msg}{NC}"


# Minimal JSON Schema validator (no external deps needed)
def validate_string(val, schema_val, path) -> typing.List[str]:
    errors = []
    if not isinstance(val, str):
        errors.append(f"{path}: expected string, got {type(val).__name__}")
    return errors


def validate_number(val, schema_val, path) -> typing.List[str]:
    errors = []
    if not isinstance(val, (int, float)):
        errors.append(f"{path}: expected number, got {type(val).__name__}")
    if "minimum" in schema_val and val < schema_val["minimum"]:
        errors.append(f"{path}: {val} < minimum {schema_val['minimum']}")
    if "maximum" in schema_val and val > schema_val["maximum"]:
        errors.append(f"{path}: {val} > maximum {schema_val['maximum']}")
    return errors


def validate_boolean(val, schema_val, path) -> typing.List[str]:
    errors = []
    if not isinstance(val, bool):
        errors.append(f"{path}: expected boolean, got {type(val).__name__}")
    return errors


def validate_object(val, schema_val, path) -> typing.List[str]:
    errors = []
    if not isinstance(val, dict):
        errors.append(f"{path}: expected object, got {type(val).__name__}")
        return errors
    props = schema_val.get("properties", {})
    additional = schema_val.get("additionalProperties", True)

    # Check required
    for req in schema_val.get("required", []):
        if req not in val:
            errors.append(f"{path}.{req}: required field missing")

    # Check defined properties
    for k, v in val.items():
        if k in props:
            errors.extend(validate_value(v, props[k], f"{path}.{k}"))
        elif not additional and k not in ["_schema", "version"]:
            errors.append(f"{path}.{k}: unknown property (not in schema)")

    return errors


def validate_array(val, schema_val, path) -> typing.List[str]:
    errors = []
    if not isinstance(val, list):
        errors.append(f"{path}: expected array, got {type(val).__name__}")
        return errors
    items_schema = schema_val.get("items", {})
    for i, item in enumerate(val):
        errors.extend(validate_value(item, items_schema, f"{path}[{i}]"))
    return errors


def validate_value(val, schema, path) -> typing.List[str]:
    errors = []
    const = schema.get("const")

    if const is not None:
        if val != const:
            errors.append(f"{path}: value must be {const}, got {val}")
        return errors

    schema_type = schema.get("type")
    # Handle union types like ["string", "null"]
    if isinstance(schema_type, list):
        # Try each type in the union, accept first match
        union_errors = []
        val_is_none = val is None
        for t in schema_type:
            if val_is_none and t == "null":
                return []  # null matches "null" type
            if val_is_none and t != "null":
                continue  # skip non-null types for null value
            sub_errors = validate_value(val, {**schema, "type": t}, path)
            if not sub_errors:
                return []  # Valid against at least one type
            union_errors.extend(sub_errors)
        if not val_is_none:  # Only report errors for non-null values
            errors.extend(union_errors)
        return errors

    if schema_type == "string":
        errors.extend(validate_string(val, schema, path))
    elif schema_type == "number" or schema_type == "integer":
        errors.extend(validate_number(val, schema, path))
    elif schema_type == "boolean":
        errors.extend(validate_boolean(val, schema, path))
    elif schema_type == "object":
        errors.extend(validate_object(val, schema, path))
    elif schema_type == "array":
        errors.extend(validate_array(val, schema, path))
    elif schema_type == "null":
        if val is not None:
            errors.append(f"{path}: expected null, got {type(val).__name__}")
    elif schema_type is None:
        pass  # No type constraint
    else:
        errors.append(f"{path}: unknown schema type {schema_type}")

    return errors


def validate_state(state: dict, schema: dict) -> typing.Tuple[bool, typing.List[str]]:
    errors = []

    # Top-level required fields
    for req in schema.get("required", []):
        if req not in state:
            errors.append(f"required field missing: {req}")

    # Validate _schema and version
    if "_schema" in schema.get("properties", {}):
        schema_val = schema["properties"]["_schema"]
        const = schema_val.get("const")
        if const and state.get("_schema") != const:
            errors.append(f"_schema must be '{const}', got '{state.get('_schema')}'")

    if "version" in schema.get("properties", {}):
        schema_val = schema["properties"]["version"]
        const = schema_val.get("const")
        if const and state.get("version") != const:
            errors.append(f"version must be '{const}', got '{state.get('version')}'")

    # Validate known fields
    for field, field_schema in schema.get("properties", {}).items():
        if field in state:
            errors.extend(validate_value(state[field], field_schema, field))

    return len(errors) == 0, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness State Schema Validator")
    parser.add_argument("state_file", nargs="?", help="Path to state.json")
    parser.add_argument("--schema", "-s", default=None, help="Path to schema file")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()

    # Find state file
    if args.state_file:
        state_path = Path(args.state_file)
    else:
        candidates = [
            Path("harness/feedback/state/state.json"),
            Path("harness/base/state.json"),
            Path("state.json"),
        ]
        state_path = None
        for c in candidates:
            if c.exists():
                state_path = c
                break
        if not state_path:
            print(f"{fail('state.json not found')}")
            print("Usage: state-validator.py <state-file> [--schema <schema>]")
            return 1

    # Find schema
    script_root = Path(__file__).resolve().parent.parent.parent
    if args.schema:
        schema_path = Path(args.schema).resolve()
        with open(schema_path) as f:
            schema = json.load(f)
    else:
        candidates = [
            script_root / "core" / "schema" / "state.v2.schema.json",
            Path("core/schema/state.v2.schema.json").resolve(),
        ]
        schema_path = None
        for c in candidates:
            if c.exists():
                schema_path = c
                break
        if not schema_path:
            print(f"{warn('Schema not found, running basic checks only')}")
            schema = {"properties": {}, "required": []}
        else:
            with open(schema_path) as f:
                schema = json.load(f)

    # Load state
    with open(state_path) as f:
        state = json.load(f)

    # Validate
    valid, errors = validate_state(state, schema)

    print(f"\n  {bold('State Schema Validator')}")
    print(f"  State:   {state_path}")
    if args.schema or schema_path:
        print(f"  Schema:  {schema_path or 'default v2'}")
    print()

    if valid:
        print(f"  {ok('Valid harness-state-v2 schema')}")
        print(f"  Schema:  {state.get('_schema', 'unknown')}")
        print(f"  Version: {state.get('version', 'unknown')}")
        project = state.get("project", "unknown")
        print(f"  Project: {project}")
        print()
        return 0

    print(f"  {fail('Schema validation failed')}")
    for err in errors:
        print(f"    • {err}")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
