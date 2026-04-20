#!/usr/bin/env python3
"""
Memory CLI — Command-line interface for harness memory operations.

Usage:
    python -m tools.memory.cli add <title> <content> [--tags tag1,tag2] [--type memory|user]
    python -m tools.memory.cli list [--type memory|user]
    python -m tools.memory.cli get <title> [--type memory|user]
    python -m tools.memory.cli remove <title> [--type memory|user]
    python -m tools.memory.cli snapshot
    python -m tools.memory.cli stats
    python -m tools.memory.cli retrieve [--query TEXT] [--type episodic|semantic|working_context]
    python -m tools.memory.cli cp0 [--task-id ID] [--description TEXT]
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.memory.store import MemoryStore, MemoryEntry
from tools.memory.retrieval import (
    MemoryRetrieval,
    EpisodicQuery,
    SemanticQuery,
    WorkingContextQuery,
)


def cmd_add(args: argparse.Namespace) -> int:
    store = MemoryStore()
    tags = args.tags.split(",") if args.tags else []
    entry = store.add_entry(
        title=args.title,
        content=args.content,
        tags=tags,
        memory_type=args.type or "memory",
    )
    print(f"Added entry: {entry.title} ({entry.created_at})")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    store = MemoryStore()
    entries = store.read_user_entries() if args.type == "user" else store.read_entries()
    if not entries:
        print("No entries found.")
        return 0
    for i, entry in enumerate(entries, 1):
        tags_str = f" [{', '.join(entry.tags)}]" if entry.tags else ""
        print(f"{i}. {entry.title}{tags_str}")
        print(f"   {entry.content[:100]}{'...' if len(entry.content) > 100 else ''}")
        print()
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    store = MemoryStore()
    entries = store.read_user_entries() if args.type == "user" else store.read_entries()
    for entry in entries:
        if entry.title == args.title:
            print(f"# {entry.title}")
            if entry.tags:
                print(f"tags: {', '.join(entry.tags)}")
            print()
            print(entry.content)
            print()
            print(f"created: {entry.created_at}")
            print(f"updated: {entry.updated_at}")
            return 0
    print(f"Entry not found: {args.title}", file=sys.stderr)
    return 1


def cmd_remove(args: argparse.Namespace) -> int:
    store = MemoryStore()
    if store.remove_entry(args.title, memory_type=args.type or "memory"):
        print(f"Removed: {args.title}")
        return 0
    print(f"Entry not found: {args.title}", file=sys.stderr)
    return 1


def cmd_snapshot(args: argparse.Namespace) -> int:
    store = MemoryStore()
    store.refresh_snapshot()
    text = store.get_injection_prompt()
    print(text)
    print(f"\n[Snapshot saved to {store.snapshot_path}]")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    store = MemoryStore()
    s = store.stats()
    print(json.dumps(s, indent=2))
    return 0


def cmd_retrieve(args: argparse.Namespace) -> int:
    retrieval = MemoryRetrieval()

    if args.query_type == "episodic":
        result = retrieval.query_episodic(EpisodicQuery(
            keywords=args.query.split() if args.query else [],
            limit=args.limit or 5,
        ))
        print(f"Episodic results: {len(result.episodes)}")
        for ep in result.episodes:
            print(f"\n- [{ep['taskId']}] (score={ep['relevanceScore']:.2f})")
            print(f"  {ep['summary'][:200]}")

    elif args.query_type == "semantic":
        result = retrieval.query_semantic(SemanticQuery(
            entities=args.query.split() if args.query else [],
        ))
        print(f"Constraints ({len(result.constraints)}):")
        for c in result.constraints:
            print(f"  • {c[:100]}")
        print(f"\nPatterns ({len(result.patterns)}):")
        for p in result.patterns:
            print(f"  • {p[:100]}")

    elif args.query_type == "working_context":
        result = retrieval.query_working_context(WorkingContextQuery())
        print(f"Completed steps: {len(result.completed_steps)}")
        print(f"Pending steps: {len(result.pending_steps)}")
        if result.blocked_reason:
            print(f"Blocked: {result.blocked_reason}")

    else:
        print("Specify --type episodic|semantic|working_context", file=sys.stderr)
        return 1

    return 0


def cmd_cp0(args: argparse.Namespace) -> int:
    task = {
        "id": args.task_id or "unknown",
        "description": args.description or "",
        "techStack": args.tech_stack.split(",") if args.tech_stack else [],
    }
    retrieval = MemoryRetrieval()
    result = retrieval.cp0_init(task)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="harness memory CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # add
    p = sub.add_parser("add", help="Add memory entry")
    p.add_argument("title", help="Entry title")
    p.add_argument("content", help="Entry content")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--type", choices=["memory", "user"], default="memory")
    p.set_defaults(func=cmd_add)

    # list
    p = sub.add_parser("list", help="List entries")
    p.add_argument("--type", choices=["memory", "user"], default="memory")
    p.set_defaults(func=cmd_list)

    # get
    p = sub.add_parser("get", help="Get entry by title")
    p.add_argument("title", help="Entry title")
    p.add_argument("--type", choices=["memory", "user"], default="memory")
    p.set_defaults(func=cmd_get)

    # remove
    p = sub.add_parser("remove", help="Remove entry by title")
    p.add_argument("title", help="Entry title")
    p.add_argument("--type", choices=["memory", "user"], default="memory")
    p.set_defaults(func=cmd_remove)

    # snapshot
    p = sub.add_parser("snapshot", help="Regenerate frozen snapshot")
    p.set_defaults(func=cmd_snapshot)

    # stats
    p = sub.add_parser("stats", help="Show memory statistics")
    p.set_defaults(func=cmd_stats)

    # retrieve
    p = sub.add_parser("retrieve", help="Query memory")
    p.add_argument("--query", help="Query text")
    p.add_argument("--type", dest="query_type", choices=["episodic", "semantic", "working_context"], default="episodic")
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_retrieve)

    # cp0
    p = sub.add_parser("cp0", help="Run CP0 initialization retrieval")
    p.add_argument("--task-id", help="Task ID")
    p.add_argument("--description", help="Task description")
    p.add_argument("--tech-stack", help="Comma-separated tech stack")
    p.set_defaults(func=cmd_cp0)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
