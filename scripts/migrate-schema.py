#!/usr/bin/env python3
"""Migrate all state.json files to harness-state-v2 schema."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent

SCHEMA = "harness-state-v2"
VERSION = "2.0.0"

FEEDBACK_STATE_TEMPLATE = {
    "_schema": SCHEMA,
    "version": VERSION,
    "project": None,
    "type": "generic",
    "platform": "generic",
    "lastUpdated": None,
    "checkpoints": {
        "CP0": "pending", "CP1": "pending", "CP2": "pending",
        "CP3": "pending", "CP4": "pending"
    },
    "gates": {
        "init": "pending", "plan": "pending", "exec": "pending",
        "verify": "pending", "complete": "pending"
    },
    "healing": {
        "enabled": True,
        "maxAttempts": 3,
        "currentAttempt": 0,
        "lastAttempt": None,
        "lastError": None,
        "retryHistory": [],
        "autoHeal": True,
    },
    "metrics": {"tasksCompleted": 0, "tasksBlocked": 0},
    "autonomy": {"level": 4, "requireApprovalFor": [], "autoMergeOnCI": False},
    "recentChanges": [],
    "taskHistory": [],
}

BASE_STATE_TEMPLATE = {
    "_schema": SCHEMA,
    "version": VERSION,
    "project": None,
    "type": "generic",
    "platform": "generic",
    "lastUpdated": None,
    "checkpoints": {
        "CP0": "pending", "CP1": "pending", "CP2": "pending",
        "CP3": "pending", "CP4": "pending"
    },
    "gates": {
        "init": "pending", "plan": "pending", "exec": "pending",
        "verify": "pending", "complete": "pending"
    },
    "metrics": {"tasksCompleted": 0, "tasksBlocked": 0},
    "autonomy": {"level": 4, "requireApprovalFor": [], "autoMergeOnCI": False},
    "recentChanges": [],
    "taskHistory": [],
}

def migrate_feedback_state(path):
    with open(path) as f:
        data = json.load(f)
    original_schema = data.get("_schema", "unknown")
    
    # Preserve existing values
    template = FEEDBACK_STATE_TEMPLATE.copy()
    template["project"] = data.get("project", path.parts[-4])  # 3 dirs up from harness/feedback/state/
    template["type"] = data.get("type", "generic")
    template["platform"] = data.get("platform", "generic")
    template["lastUpdated"] = data.get("lastUpdated")
    
    # Checkpoints
    cp = data.get("checkpoints", {})
    if isinstance(cp, dict):
        for k in ["CP0","CP1","CP2","CP3","CP4"]:
            v = cp.get(k, "pending")
            if isinstance(v, str):
                template["checkpoints"][k] = v
            elif isinstance(v, dict):
                template["checkpoints"][k] = v.get("status", "pending")
    else:
        for k in ["CP0","CP1","CP2","CP3","CP4"]:
            if k in cp:
                val = cp[k]
                template["checkpoints"][k] = val if isinstance(val, str) else "pending"
    
    # Gates
    gates = data.get("gates", {})
    if isinstance(gates, dict):
        for k in template["gates"]:
            if k in gates:
                template["gates"][k] = gates[k]
    
    # Healing - preserve existing if present
    if "healing" in data:
        template["healing"] = data["healing"]
    
    # Metrics
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        template["metrics"] = {
            "tasksCompleted": metrics.get("tasksCompleted", 0),
            "tasksBlocked": metrics.get("tasksBlocked", 0),
        }
    
    # Autonomy
    autonomy = data.get("autonomy", {})
    if isinstance(autonomy, dict):
        template["autonomy"] = {
            "level": autonomy.get("level", 4),
            "requireApprovalFor": autonomy.get("requireApprovalFor", []),
            "autoMergeOnCI": autonomy.get("autoMergeOnCI", False),
        }
    
    # Recent changes
    if "recentChanges" in data:
        template["recentChanges"] = data["recentChanges"]
    
    # Task history
    if "taskHistory" in data:
        template["taskHistory"] = data["taskHistory"]
    
    return original_schema, template


def migrate_base_state(path):
    with open(path) as f:
        data = json.load(f)
    original_schema = data.get("_schema", "unknown")
    
    template = BASE_STATE_TEMPLATE.copy()
    template["project"] = data.get("project")
    template["type"] = data.get("type", "generic")
    template["platform"] = data.get("platform", "generic")
    template["lastUpdated"] = data.get("lastUpdated")
    
    cp = data.get("checkpoints", {})
    if isinstance(cp, dict):
        for k in ["CP0","CP1","CP2","CP3","CP4"]:
            if k in cp:
                val = cp[k]
                template["checkpoints"][k] = val if isinstance(val, str) else "pending"
    
    gates = data.get("gates", {})
    if isinstance(gates, dict):
        for k in template["gates"]:
            if k in gates:
                template["gates"][k] = gates[k]
    
    metrics = data.get("metrics", {})
    if isinstance(metrics, dict):
        template["metrics"] = {
            "tasksCompleted": metrics.get("tasksCompleted", 0),
            "tasksBlocked": metrics.get("tasksBlocked", 0),
        }
    
    autonomy = data.get("autonomy", {})
    if isinstance(autonomy, dict):
        template["autonomy"] = {
            "level": autonomy.get("level", 4),
            "requireApprovalFor": autonomy.get("requireApprovalFor", []),
            "autoMergeOnCI": autonomy.get("autoMergeOnCI", False),
        }
    
    if "recentChanges" in data:
        template["recentChanges"] = data["recentChanges"]
    if "taskHistory" in data:
        template["taskHistory"] = data["taskHistory"]
    
    return original_schema, template


def main():
    updated = []
    
    # feedback/state/state.json files
    for path in ROOT.rglob("harness/feedback/state/state.json"):
        original_schema, new_data = migrate_feedback_state(path)
        with open(path, "w") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        updated.append((str(path), original_schema, SCHEMA))
    
    # base/state.json files
    for path in ROOT.rglob("harness/base/state.json"):
        original_schema, new_data = migrate_base_state(path)
        with open(path, "w") as f:
            json.dump(new_data, f, indent=2, ensure_ascii=False)
        updated.append((str(path), original_schema, SCHEMA))
    
    print(f"Migrated {len(updated)} files to {SCHEMA}:\n")
    for path, old, new in updated:
        rel = path.replace(str(ROOT) + "/", "")
        print(f"  {old} → {new}:  {rel}")
    
    # Also update the example todo-app
    example = ROOT / "examples/todo-app/harness/feedback/state/state.json"
    if example.exists():
        with open(example) as f:
            data = json.load(f)
        if "_schema" not in data:
            data["_schema"] = SCHEMA
            data["version"] = VERSION
            with open(example, "w") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"\n  (new) → {SCHEMA}:  examples/todo-app/harness/feedback/state/state.json (added schema)")

if __name__ == "__main__":
    main()
