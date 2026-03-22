#!/usr/bin/env python3
"""Harness CLI - Agent Workflow Management Tool"""
import argparse, json, sys
from pathlib import Path
from datetime import datetime

S = "harness/feedback/state/state.json"

def cmd_init(a):
    state = {
        "_schema": "harness-v2", "version": "1.0.0", "type": "generic",
        "platform": "auto", "lastUpdated": datetime.now().isoformat(),
        "currentTask": None, "taskStatus": "idle",
        "checkpoints": {f"CP{i}": "pending" for i in range(6)},
        "gates": {"init": "pending", "plan": "pending", "exec": "pending", "verify": "pending", "complete": "pending"},
        "metrics": {"tasksCompleted": 0, "tasksBlocked": 0, "averageTaskDuration": 0}
    }
    Path(S).parent.mkdir(parents=True, exist_ok=True)
    with open(S, "w") as f: json.dump(state, f, indent=2)
    print(f"[OK] Initialized at {S}")

def cmd_status(a):
    p = Path(a.project or ".") / S
    if not p.exists(): print(f"[ERROR] Not found: {p}"); return 1
    with open(p) as f: state = json.load(f)
    print()
    print("=== Harness Status ===")
    print(f"Project: {state.get('project', 'unknown')}")
    print(f"Task: {state.get('currentTask', 'none')}")
    print(f"Status: {state.get('taskStatus', 'unknown')}")
    print()
    print("Checkpoints:")
    for k, v in state.get("checkpoints", {}).items():
        icon = "[OK]" if v == "completed" else "[..]" if v == "in_progress" else "[--]"
        print(f"  {icon} {k}: {v}")
    print()
    print("Gates:")
    for k, v in state.get("gates", {}).items():
        icon = "[OK]" if v == "passed" else "[XX]" if v == "failed" else "[--]"
        print(f"  {icon} {k}: {v}")
    m = state.get("metrics", {})
    print()
    print(f"Metrics: Completed={m.get('tasksCompleted', 0)}, Blocked={m.get('tasksBlocked', 0)}")
    return 0

def cmd_checkpoint(a):
    p = Path(a.project or ".") / S
    if not p.exists(): print(f"[ERROR] Not found: {p}"); return 1
    with open(p) as f: state = json.load(f)
    name = a.name or "CP1"
    state["checkpoints"][name] = "completed"
    state["lastUpdated"] = datetime.now().isoformat()
    with open(p, "w") as f: json.dump(state, f, indent=2)
    print(f"[OK] {name} marked completed")

def cmd_validate(a):
    p = Path(a.project or ".") / S
    if not p.exists(): print(f"[ERROR] Not found: {p}"); return 1
    try:
        with open(p) as f: state = json.load(f)
    except Exception as e: print(f"[ERROR] {e}"); return 1
    errs = [e for e in ["_schema", "checkpoints", "metrics"] if e not in state]
    if errs: print("[FAIL] " + ", ".join(errs)); return 1
    print(f"[OK] Schema: {state.get('_schema', 'unknown')}")
    return 0

def cmd_report(a):
    p = Path(a.project or ".") / S
    if not p.exists(): print(f"[ERROR] Not found: {p}"); return 1
    with open(p) as f: state = json.load(f)
    cps = state.get("checkpoints", {})
    done = sum(1 for v in cps.values() if v == "completed")
    total = len(cps)
    pct = done * 100 // total if total else 0
    print()
    print("="*40)
    print("Harness Report")
    print("="*40)
    print(f"Project: {state.get('project', 'unknown')}")
    print(f"Type: {state.get('type', 'unknown')}")
    print(f"Progress: {done}/{total} ({pct}%)")
    print(f"Last Updated: {state.get('lastUpdated', 'never')}")
    print("="*40)
    print()
    return 0

p = argparse.ArgumentParser(description="Harness CLI")
sub = p.add_subparsers(dest="cmd")
sub.add_parser("init")
sp = sub.add_parser("status"); sp.add_argument("-p", "--project")
cp = sub.add_parser("checkpoint"); cp.add_argument("name", nargs="?"); cp.add_argument("-p", "--project")
vp = sub.add_parser("validate"); vp.add_argument("-p", "--project")
rp = sub.add_parser("report"); rp.add_argument("-p", "--project")
a = p.parse_args()
funcs = {"init": cmd_init, "status": cmd_status, "checkpoint": cmd_checkpoint, "validate": cmd_validate, "report": cmd_report}
funcs.get(a.cmd, lambda: p.print_help())(a)
