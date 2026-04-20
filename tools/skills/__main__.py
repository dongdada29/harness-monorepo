#!/usr/bin/env python3
"""
Skills Hub CLI — Manage harness skills from multiple sources.

Usage:
    python -m tools.skills.cli install <source> <identifier>
    python -m tools.skills.cli list [--source local|github|optional|installed]
    python -m tools.skills.cli search <query>
    python -m tools.skills.cli uninstall <name>
    python -m tools.skills.cli info <name>
    python -m tools.skills.cli audit
    python -m tools.skills.cli tap add <repo>
    python -m tools.skills.cli tap remove <repo>
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.skills.source import (
    SkillSource, LocalSource, GitHubSource, OptionalSource,
    HubLockFile, AuditLog, TRUST_ORDER,
)
from tools.skills.installer import SkillInstaller


def cmd_install(args: argparse.Namespace) -> int:
    # Resolve source
    if args.source == "local":
        source: SkillSource = LocalSource()
    elif args.source == "github":
        source = GitHubSource()
    elif args.source == "optional":
        source = OptionalSource()
    else:
        print(f"Unknown source: {args.source}", file=sys.stderr)
        return 1

    # Fetch meta
    try:
        bundle = source.fetch(args.identifier)
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        return 1

    # Build meta from bundle
    from tools.skills.source import SkillMeta
    meta = SkillMeta(
        name=bundle.name,
        description=bundle.name,
        source=source.name,
        identifier=args.identifier,
        trust_level=bundle.trust_level,
    )

    # Install
    installer = SkillInstaller(source=source)
    ok, msg = installer.install(meta)
    if ok:
        print(f"✅ {msg}")
        return 0
    else:
        print(f"❌ {msg}", file=sys.stderr)
        return 1


def cmd_list(args: argparse.Namespace) -> int:
    if args.source == "installed":
        lock = HubLockFile()
        metas = lock.list_all()
        if not metas:
            print("No installed skills.")
            return 0
        for meta in metas:
            print(f"  {meta.name} [{meta.source}] ({meta.trust_level})")
        return 0

    # List from a specific source
    if args.source == "local":
        source = LocalSource()
    elif args.source == "github":
        source = GitHubSource()
    elif args.source == "optional":
        source = OptionalSource()
    else:
        print(f"Unknown source: {args.source}", file=sys.stderr)
        return 1

    try:
        skills = source.list_all()
    except Exception as e:
        print(f"Failed to list: {e}", file=sys.stderr)
        return 1

    if not skills:
        print(f"No skills found in {args.source}.")
        return 0

    for s in skills:
        trust_marker = "✓" if s.trust_level in (TRUST_ORDER[0], TRUST_ORDER[1]) else "?"
        print(f"  {trust_marker} {s.name} — {s.description[:60]}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    sources: list[SkillSource] = [
        LocalSource(),
        OptionalSource(),
        GitHubSource(),
    ]

    results: list[tuple[str, str]] = []  # (source_name, meta_str)

    for source in sources:
        try:
            matches = source.search(args.query, limit=10)
            for m in matches:
                results.append((source.name, f"  [{source.name}] {m.name} — {m.description[:50]}"))
        except Exception as e:
            print(f"Warning: {source.name} search failed: {e}", file=sys.stderr)

    if not results:
        print(f"No skills matching '{args.query}'.")
        return 0

    print(f"Results for '{args.query}':")
    for _, line in results:
        print(line)
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    installer = SkillInstaller()
    ok, msg = installer.uninstall(args.name)
    if ok:
        print(f"✅ {msg}")
        return 0
    else:
        print(f"❌ {msg}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    lock = HubLockFile()
    entry = lock.get(args.name)
    if not entry:
        print(f"Skill not found: {args.name}", file=sys.stderr)
        return 1

    print(json.dumps(entry, indent=2))
    return 0


def cmd_audit(args: argparse.Namespace) -> int:
    audit = AuditLog()
    if not audit.log_path.exists():
        print("No audit log.")
        return 0

    lines = audit.log_path.read_text().strip().split("\n")
    if not lines:
        print("No audit entries.")
        return 0

    print(f"Total entries: {len(lines)}")
    print()
    for line in reversed(lines[-20:]):
        try:
            entry = json.loads(line)
            ts = entry["ts"][:19]
            result_icon = "✅" if entry["result"] == "ok" else "❌"
            print(f"{result_icon} {ts} {entry['action']:12} {entry['name']:30} {entry['detail'][:40]}")
        except Exception:
            print(line)
    return 0


def cmd_tap(args: argparse.Namespace) -> int:
    from tools.skills.source import HUB_DIR, TAPS_FILE

    HUB_DIR.mkdir(parents=True, exist_ok=True)
    taps = json.loads(TAPS_FILE.read_text()) if TAPS_FILE.exists() else []

    if args.tap_cmd == "add":
        if args.repo in taps:
            print(f"Already tapped: {args.repo}")
        else:
            taps.append(args.repo)
            TAPS_FILE.write_text(json.dumps(taps, indent=2))
            print(f"Added tap: {args.repo}")
    elif args.tap_cmd == "remove":
        if args.repo in taps:
            taps.remove(args.repo)
            TAPS_FILE.write_text(json.dumps(taps, indent=2))
            print(f"Removed tap: {args.repo}")
        else:
            print(f"Not tapped: {args.repo}")
    elif args.tap_cmd == "list":
        if not taps:
            print("No taps. Default repos:")
            for r in GitHubSource.DEFAULT_REPOS:
                print(f"  {r}")
        else:
            print("Tapped repos:")
            for r in taps:
                print(f"  {r}")

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="harness skills hub CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # install
    p = sub.add_parser("install", help="Install a skill")
    p.add_argument("source", choices=["local", "github", "optional"], help="Source type")
    p.add_argument("identifier", help="Skill identifier (template name or repo/path)")
    p.set_defaults(func=cmd_install)

    # list
    p = sub.add_parser("list", help="List skills")
    p.add_argument("--source", default="installed", choices=["local", "github", "optional", "installed"])
    p.set_defaults(func=cmd_list)

    # search
    p = sub.add_parser("search", help="Search across all sources")
    p.add_argument("query", help="Search query")
    p.set_defaults(func=cmd_search)

    # uninstall
    p = sub.add_parser("uninstall", help="Uninstall a skill")
    p.add_argument("name", help="Skill name")
    p.set_defaults(func=cmd_uninstall)

    # info
    p = sub.add_parser("info", help="Show skill info from lock")
    p.add_argument("name", help="Skill name")
    p.set_defaults(func=cmd_info)

    # audit
    p = sub.add_parser("audit", help="Show audit log")
    p.set_defaults(func=cmd_audit)

    # tap
    p = sub.add_parser("tap", help="Manage GitHub taps")
    p.add_argument("tap_cmd", choices=["add", "remove", "list"])
    p.add_argument("repo", nargs="?", help="Repo in owner/name format")
    p.set_defaults(func=cmd_tap)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
