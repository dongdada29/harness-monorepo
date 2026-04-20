#!/usr/bin/env python3
"""
Harness Validator — Validates harness configuration files.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ---------------------------------------------------------------------------
# ANSI
# ---------------------------------------------------------------------------

GREEN = "\033[0;32m"
RED = "\033[0;31m"
YELLOW = "\033[1;33m"
NC = "\033[0m"
BOLD = "\033[1m"


def ok(msg: str) -> str: return f"{GREEN}✅{NC}  {msg}"
def fail(msg: str) -> str: return f"{RED}❌{NC}  {msg}"
def warn(msg: str) -> str: return f"{YELLOW}⚠️{NC}  {msg}"
def bold(msg: str) -> str: return f"{BOLD}{msg}{NC}"


# ---------------------------------------------------------------------------
# Schema definitions
# ---------------------------------------------------------------------------

STATE_REQUIRED_FIELDS = [
    "_schema", "version", "type", "platform",
    "lastUpdated", "checkpoints", "gates", "metrics",
]

STATE_OPTIONAL_FIELDS = [
    "autonomy", "currentTask", "taskStatus", "project",
    "recentChanges", "taskHistory", "patterns",
]

VALID_TYPES = ["generic", "electron", "tauri", "agent", "universal"]
VALID_PLATFORMS = ["auto", "electron", "tauri", "universal", "node", "browser"]
VALID_CP_STATUS = ["pending", "in_progress", "completed", "skipped", "failed"]
VALID_GATE_STATUS = ["pending", "passed", "failed", "skipped"]
VALID_AUTONOMY_LEVELS = list(range(1, 10))


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def validate_state_json(path: Path) -> Tuple[bool, List[str]]:
    errors = []
    if not path.exists():
        return False, [f"File not found: {path}"]

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return False, [f"JSON parse error: {e}"]

    # Required fields
    for field in STATE_REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    # Type check
    if "type" in data and data["type"] not in VALID_TYPES:
        errors.append(f"Invalid type '{data['type']}'. Valid: {VALID_TYPES}")

    # Platform check
    if "platform" in data and data["platform"] not in VALID_PLATFORMS:
        errors.append(f"Invalid platform '{data['platform']}'. Valid: {VALID_PLATFORMS}")

    # Checkpoints
    cps = data.get("checkpoints", {})
    for cp_name, status in cps.items():
        if status not in VALID_CP_STATUS:
            errors.append(f"Invalid checkpoint status '{status}' for '{cp_name}'")

    # Gates
    gates = data.get("gates", {})
    for gate_name, status in gates.items():
        if status not in VALID_GATE_STATUS:
            errors.append(f"Invalid gate status '{status}' for '{gate_name}'")

    # Autonomy level
    autonomy = data.get("autonomy", {})
    level = autonomy.get("level")
    if level is not None and level not in VALID_AUTONOMY_LEVELS:
        errors.append(f"Invalid autonomy level {level}. Valid: 1-9")

    return len(errors) == 0, errors


def validate_constraints_md(path: Path) -> Tuple[bool, List[str]]:
    errors = []
    if not path.exists():
        return False, [f"File not found: {path}"]

    content = path.read_text()

    # Check for required sections
    required_sections = ["##", "###"]
    if not re.search(r"#{1,3}\s+\w", content):
        errors.append("No markdown headers found")

    # Check for blocked paths in constraints
    if "Blocked" in content or "block" in content.lower():
        blocked = re.findall(r"[-~`]?`?([^`\n]+)`?", content)
        if not blocked:
            errors.append("Blocked paths listed but no actual paths found")

    return len(errors) == 0, errors


def validate_schema_json(path: Path) -> Tuple[bool, List[str]]:
    errors = []
    if not path.exists():
        return False, [f"File not found: {path}"]

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return False, [f"JSON parse error: {e}"]

    if "type" not in data:
        errors.append("Missing 'type' field")
    if "$schema" not in data and "schema" not in data:
        errors.append("Missing schema declaration")

    return len(errors) == 0, errors


def validate_project(project_path: Path) -> bool:
    """Validate a complete harness project."""
    print(f"\n{'='*56}")
    print(f"  Validating: {project_path}")
    print(f"{'='*56}\n")

    results = {}

    # State.json
    state_candidates = [
        project_path / "harness" / "base" / "state.json",
        project_path / "harness" / "feedback" / "state" / "state.json",
        project_path / "state.json",
    ]
    state_found = None
    for candidate in state_candidates:
        if candidate.exists():
            state_found = candidate
            break

    if state_found:
        valid, errors = validate_state_json(state_found)
        results["state.json"] = (valid, errors, str(state_found))
    else:
        results["state.json"] = (False, ["state.json not found in expected locations"], "not found")

    # Constraints.md
    constraint_candidates = [
        project_path / "harness" / "base" / "constraints.md",
        project_path / "constraints.md",
    ]
    const_found = None
    for candidate in constraint_candidates:
        if candidate.exists():
            const_found = candidate
            break

    if const_found:
        valid, errors = validate_constraints_md(const_found)
        results["constraints.md"] = (valid, errors, str(const_found))
    else:
        results["constraints.md"] = (False, ["constraints.md not found"], "not found")

    # Schema.json
    schema_candidates = [
        project_path / "state.v2.schema.json",
        project_path / "state.v1.schema.json",
        project_path / "schema.json",
    ]
    schema_found = None
    for candidate in schema_candidates:
        if candidate.exists():
            schema_found = candidate
            break

    if schema_found:
        valid, errors = validate_schema_json(schema_found)
        results["schema.json"] = (valid, errors, str(schema_found))
    else:
        results["schema.json"] = (False, ["schema not found (optional)"], "not found (optional)")

    # Print results
    passed = 0
    failed = 0
    for name, (valid, errors, path) in results.items():
        status = "PASSED" if valid else "FAILED"
        icon = ok(name) if valid else fail(name)
        print(f"  {icon}  ({status})")
        print(f"         {path}")
        if errors:
            for err in errors:
                print(f"       {RED}  • {err}{NC}")
        print()
        if valid:
            passed += 1
        else:
            failed += 1

    print(f"{'─'*56}")
    total = passed + failed
    if failed == 0:
        print(f"  {GREEN}✅ OVERALL: PASSED ({passed}/{total}){NC}")
    else:
        print(f"  {RED}❌ OVERALL: FAILED ({passed}/{total}){NC}")
    print(f"{'─'*56}\n")

    return failed == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Validator")
    parser.add_argument("project", nargs="?", default=".", help="Project path")
    parser.add_argument("--all", action="store_true", help="Validate all files")
    parser.add_argument("--state", action="store_true", help="Validate state.json only")
    parser.add_argument("--constraints", action="store_true", help="Validate constraints.md only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()
    project = Path(args.project).expanduser().resolve()

    if not project.exists():
        print(f"{RED}[ERROR]{NC} Path not found: {project}")
        return 1

    if args.state:
        candidates = [
            project / "harness" / "feedback" / "state" / "state.json",
            project / "harness" / "base" / "state.json",
        ]
        target = None
        for c in candidates:
            if c.exists():
                target = c
                break
        if not target:
            print(f"{RED}[ERROR]{NC} state.json not found")
            return 1
        valid, errors = validate_state_json(target)
        print(f"{ok('state.json') if valid else fail('state.json')}")
        for e in errors:
            print(f"  {RED}  • {e}{NC}")
        return 0 if valid else 1

    if args.constraints:
        candidates = [
            project / "harness" / "base" / "constraints.md",
            project / "constraints.md",
        ]
        target = None
        for c in candidates:
            if c.exists():
                target = c
                break
        if not target:
            print(f"{RED}[ERROR]{NC} constraints.md not found")
            return 1
        valid, errors = validate_constraints_md(target)
        print(f"{ok('constraints.md') if valid else fail('constraints.md')}")
        for e in errors:
            print(f"  {RED}  • {e}{NC}")
        return 0 if valid else 1

    # Full project validation
    passed = validate_project(project)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())