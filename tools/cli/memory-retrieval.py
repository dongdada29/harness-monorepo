#!/usr/bin/env python3
"""
Memory Retrieval CLI — Query harness state.json for historical patterns.

Usage:
  python3 memory-retrieval.py <project> [--type episodic|semantic|healing] [--keywords k1,k2] [--limit 5]
"""
import argparse
import json
import sys
import typing
from pathlib import Path
from datetime import datetime, timedelta

GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
NC = "\033[0m"
RED = "\033[0;31m"
BOLD = "\033[1m"


def ok(msg: str) -> str: return f"{GREEN}✅{NC}  {msg}"
def bold(msg: str) -> str: return f"{BOLD}{msg}{NC}"


def load_state(project: Path) -> typing.Optional[dict]:
    candidates = [
        project / "harness" / "feedback" / "state" / "state.json",
        project / "harness" / "base" / "state.json",
    ]
    for c in candidates:
        if c.exists():
            with open(c) as f:
                return json.load(f)
    return None


def query_task_history(state: dict, keywords: list[str], limit: int = 5) -> list[dict]:
    """Find tasks matching keywords from taskHistory."""
    if "taskHistory" not in state or not state["taskHistory"]:
        return []

    results = []
    kw_lower = [k.lower() for k in keywords]

    for entry in reversed(state["taskHistory"]):
        task_text = entry.get("task", "").lower()
        if any(k in task_text for k in kw_lower):
            results.append(entry)
        elif not keywords:
            results.append(entry)
        if len(results) >= limit:
            break

    return results


def query_healing_history(state: dict, keywords: list[str], limit: int = 5) -> list[dict]:
    """Find healing retry attempts matching keywords."""
    healing = state.get("healing", {})
    history = healing.get("retryHistory", [])
    if not history:
        return []

    kw_lower = [k.lower() for k in keywords]
    results = []

    for entry in reversed(history):
        combined = " ".join([
            entry.get("errorSummary", ""),
            " ".join(entry.get("failedGates", [])),
        ]).lower()

        if any(k in combined for k in kw_lower) or not keywords:
            results.append(entry)
        if len(results) >= limit:
            break

    return results


def query_episodic(state: dict, keywords: list[str], limit: int = 5, days: int = 30) -> list[dict]:
    """Find recent episodes (taskHistory + healing) matching keywords."""
    cutoff = datetime.now() - timedelta(days=days)

    episodes = []
    # taskHistory episodes
    for entry in state.get("taskHistory", []):
        ts = entry.get("completedAt")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.replace(tzinfo=None) < cutoff:
                    continue
            except ValueError:
                pass
        episodes.append({**entry, "_type": "task"})

    # healing retry episodes
    for entry in state.get("healing", {}).get("retryHistory", []):
        ts = entry.get("timestamp")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.replace(tzinfo=None) < cutoff:
                    continue
            except ValueError:
                pass
        episodes.append({**entry, "_type": "healing"})

    kw_lower = [k.lower() for k in keywords]
    results = []
    for e in reversed(episodes):
        if keywords:
            text = json.dumps(e, ensure_ascii=False).lower()
            if any(k in text for k in kw_lower):
                results.append(e)
        else:
            results.append(e)
        if len(results) >= limit:
            break

    return results


def query_semantic(state: dict) -> dict:
    """Return constraints, patterns, rules from state."""
    out = {"constraints": [], "patterns": [], "rules": []}
    # Memory block
    mem = state.get("memory", {})
    if "semanticCache" in mem:
        for key, vals in mem.get("semanticCache", {}).items():
            out["constraints"].extend(vals)
    return out


def format_task_history(items: list[dict]) -> None:
    print(f"\n  {bold('📋 Task History')} ({len(items)} results)")
    for i, item in enumerate(items, 1):
        ts = item.get("completedAt", "")
        task = item.get("task", "unknown")
        print(f"  {i}. {task}")
        if ts:
            print(f"     Completed: {ts}")


def format_healing_history(items: list[dict]) -> None:
    print(f"\n  {bold('🔧 Healing History')} ({len(items)} results)")
    for i, item in enumerate(items, 1):
        ts = item.get("timestamp", "")
        status = item.get("status", "")
        failed = item.get("failedGates", [])
        error = item.get("errorSummary", "")[:80]
        touched = item.get("filesTouched", [])
        status_icon = f"{GREEN}✓{NC}" if status == "passed" else f"{RED}✗{NC}"
        print(f"  {i}. [{status_icon}] Attempt {item.get('attempt', '?')} — {', '.join(failed)}")
        if error:
            print(f"     Error: {error}")
        if touched:
            print(f"     Files: {', '.join(touched[:3])}")
        if ts:
            print(f"     Time:  {ts}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Memory Retrieval CLI")
    parser.add_argument("project", nargs="?", default=".", help="Project path")
    parser.add_argument("--type", "-t", default="episodic",
                        choices=["episodic", "semantic", "healing", "task"],
                        help="Retrieval type (default: episodic)")
    parser.add_argument("--keywords", "-k", default="",
                        help="Comma-separated keywords")
    parser.add_argument("--limit", "-n", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--days", "-d", type=int, default=30, help="Look back days (default: 30)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    state = load_state(project)
    if not state:
        print(f"{RED}[ERROR]{NC} No harness state.json found in {project}")
        return 1

    keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
    limit = args.limit
    kw_display = ", ".join(keywords) or "(all)"

    print(f"\n{'='*50}")
    print(f"  🔍 Memory Retrieval — {project.name}")
    print(f"  Type: {args.type}  |  Keywords: {kw_display}  |  Limit: {limit}")
    print(f"{'='*50}")

    if args.type == "task":
        results = query_task_history(state, keywords, limit)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            if results:
                format_task_history(results)
            else:
                print(f"\n  No matching tasks found.")
            total = len(state.get("taskHistory", []))
            print(f"\n  Total: {len(results)}/{total} tasks shown")

    elif args.type == "healing":
        results = query_healing_history(state, keywords, limit)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            if results:
                format_healing_history(results)
            else:
                print(f"\n  No healing history found. (Healing enabled: {state.get('healing', {}).get('enabled', True)})")
            total = len(state.get("healing", {}).get("retryHistory", []))
            print(f"\n  Total: {len(results)}/{total} entries shown")

    elif args.type == "episodic":
        results = query_episodic(state, keywords, limit, args.days)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            if not results:
                print(f"\n  No episodes found in last {args.days} days.")
            else:
                # Group by type
                tasks = [r for r in results if r.get("_type") == "task"]
                heals = [r for r in results if r.get("_type") == "healing"]
                if tasks:
                    format_task_history(tasks)
                if heals:
                    format_healing_history(heals)
            total_tasks = len(state.get("taskHistory", []))
            total_heals = len(state.get("healing", {}).get("retryHistory", []))
            print(f"\n  Showing {len(results)} episodes ({total_tasks} tasks, {total_heals} heals in {args.days} days)")

    elif args.type == "semantic":
        results = query_semantic(state)
        if args.json:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        else:
            if results["constraints"]:
                print(f"\n  {bold('📏 Constraints')}")
                for c in results["constraints"][:10]:
                    print(f"    • {c}")
            else:
                print(f"\n  No semantic constraints cached.")
            if not any(results.values()):
                print(f"  Hint: Run CP0/C P1 to populate semantic cache.")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
