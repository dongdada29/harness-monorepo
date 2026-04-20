#!/usr/bin/env python3
"""
Harness Benchmark Runner — Core module
========================================
Measures harness effectiveness with four维度:
  1. Efficiency (40%)     — task completion, gate pass, throughput
  2. Quality (30%)        — lint, type check, test, build
  3. Behavior (15%)       — state freshness, change tracking
  4. Autonomy (15%)       — solo completion, self-correction

Usage:
    python3 runner.py                        # quick score
    python3 runner.py --project .            # specific project
    python3 runner.py --baseline /path       # compare with baseline
    python3 runner.py --output markdown      # markdown report
    python3 runner.py --history              # show historical runs
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

BENCHMARK_DIR = Path.home() / ".harness" / "benchmark"
HISTORY_FILE = BENCHMARK_DIR / "history.jsonl"
HISTORY_INDEX = BENCHMARK_DIR / "history_index.json"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class BenchmarkResult:
    project: str
    score: float
    grade: str
    grade_desc: str
    efficiency: Dict[str, float]
    quality: Dict[str, float]
    behavior: Dict[str, float]
    autonomy: Dict[str, float]
    recommendations: List[str]
    timestamp: str
    run_duration_ms: int


# ---------------------------------------------------------------------------
# ANSI
# ---------------------------------------------------------------------------

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def green(msg: str) -> str: return f"{GREEN}{msg}{NC}"
def red(msg: str) -> str: return f"{RED}{msg}{NC}"
def yellow(msg: str) -> str: return f"{YELLOW}{msg}{NC}"
def cyan(msg: str) -> str: return f"{CYAN}{msg}{NC}"
def bold(msg: str) -> str: return f"{BOLD}{msg}{NC}"


# ---------------------------------------------------------------------------
# State loading
# ---------------------------------------------------------------------------

def load_state(project: str) -> Dict:
    for candidate in [
        Path(project) / "harness/feedback/state/state.json",
        Path(project) / "state.json",
    ]:
        if candidate.exists():
            return json.loads(candidate.read_text())
    return {}


# ---------------------------------------------------------------------------
# Source discovery
# ---------------------------------------------------------------------------

def find_source_dir(project: str) -> str:
    for d in ["src", "app", "lib", "source", "tools"]:
        p = Path(project) / d
        if p.exists():
            return str(p)
    return project


def count_pattern(pattern: str, src_dir: str) -> int:
    try:
        r = subprocess.run(
            ["grep", "-r", "-l", pattern, src_dir,
             "--include=*.ts", "--include=*.tsx",
             "--include=*.js", "--include=*.jsx",
             "--include=*.py", "--include=*.go",
             "--include=*.rs"],
            capture_output=True, text=True, timeout=30,
        )
        return len([l for l in r.stdout.strip().split("\n") if l])
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# Metric measurement
# ---------------------------------------------------------------------------

def measure_efficiency(state: Dict) -> Dict[str, float]:
    metrics = state.get("metrics", {})
    gates = state.get("gates", {})

    completed = metrics.get("tasksCompleted", 0)
    blocked = metrics.get("tasksBlocked", 0)
    total = completed + blocked or 1

    completion_rate = completed / total * 100
    block_rate = blocked / total * 100

    gates_passed = sum(1 for v in gates.values() if v == "passed")
    gates_total = len(gates) or 4
    gate_pass_rate = gates_passed / gates_total * 100
    first_try_rate = (gates_total - sum(1 for v in gates.values() if v == "failed")) / gates_total * 100

    avg_dur = metrics.get("averageTaskDuration", 0)
    throughput = completed  # simplified

    return {
        "completion_rate": completion_rate,
        "block_rate": block_rate,
        "gate_pass_rate": gate_pass_rate,
        "first_try_rate": first_try_rate,
        "avg_duration_min": avg_dur,
        "throughput": throughput,
    }


def measure_quality(state: Dict, src_dir: str) -> Dict[str, float]:
    gates = state.get("gates", {})
    console_logs = count_pattern("console.log", src_dir)
    debuggers = count_pattern("debugger", src_dir)
    quality_base = max(0, 100 - console_logs * 2 - debuggers * 5)

    type_pass = 1 if gates.get("typecheck") == "passed" else 0
    test_pass = 1 if gates.get("test") == "passed" else 0
    build_pass = 1 if gates.get("build") == "passed" else 0

    return {
        "quality_base": quality_base,
        "console_logs": console_logs,
        "debuggers": debuggers,
        "type_rate": type_pass * 100,
        "test_rate": test_pass * 100,
        "build_rate": build_pass * 100,
    }


def measure_behavior(state: Dict) -> Dict[str, float]:
    last_updated = state.get("lastUpdated", "")
    if last_updated:
        try:
            days = (datetime.now() - datetime.fromisoformat(last_updated)).days
            update_rate = 100 if days == 0 else 80 if days == 1 else 50 if days <= 7 else 20
        except Exception:
            update_rate = 50
    else:
        update_rate = 0

    recent = len(state.get("recentChanges", []))
    tracking_score = min(100, recent * 20)
    violations = 0
    violation_score = max(0, 100 - violations * 10)

    return {
        "update_rate": update_rate,
        "tracking_score": tracking_score,
        "violation_score": violation_score,
        "last_updated": last_updated,
    }


def measure_autonomy(state: Dict) -> Dict[str, float]:
    metrics = state.get("metrics", {})
    solo = metrics.get("tasksCompleted", 0)
    interventions = metrics.get("humanInterventions", 0)
    total = solo + interventions or 1
    autonomy_rate = solo / total * 100

    corrections = metrics.get("selfCorrections", 0)
    corrections_rate = min(100, corrections * 20)
    escalations = metrics.get("escalations", 0)
    escalation_score = max(0, 100 - escalations * 5)

    return {
        "autonomy_rate": autonomy_rate,
        "corrections_rate": corrections_rate,
        "escalation_score": escalation_score,
    }


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

WEIGHTS = {
    "completion": 15,
    "gate": 10,
    "block": 5,
    "quality": 20,
    "type": 5,
    "coverage": 5,
    "update": 5,
    "tracking": 5,
    "violation": 5,
    "autonomy": 10,
    "correction": 5,
}


def calculate_score(eff: Dict, qual: Dict, beh: Dict, aut: Dict) -> Tuple[float, str, str]:
    w = WEIGHTS
    total_w = sum(w.values())

    score = (
        min(100, max(0, eff.get("completion_rate", 100))) * w["completion"] +
        min(100, max(0, eff.get("gate_pass_rate", 100))) * w["gate"] +
        min(100, max(0, 100 - eff.get("block_rate", 0))) * w["block"] +
        min(100, max(0, qual.get("quality_base", 100))) * w["quality"] +
        min(100, max(0, qual.get("type_rate", 100))) * w["type"] +
        min(100, max(0, qual.get("test_rate", 100))) * w["coverage"] +
        min(100, max(0, beh.get("update_rate", 100))) * w["update"] +
        min(100, max(0, beh.get("tracking_score", 100))) * w["tracking"] +
        min(100, max(0, beh.get("violation_score", 100))) * w["violation"] +
        min(100, max(0, aut.get("autonomy_rate", 100))) * w["autonomy"] +
        min(100, max(0, aut.get("corrections_rate", 100))) * w["correction"]
    ) / total_w

    if score >= 95: grade, desc = "S+", "World Class"
    elif score >= 90: grade, desc = "S", "Excellent"
    elif score >= 85: grade, desc = "A+", "Outstanding"
    elif score >= 80: grade, desc = "A", "Very Good"
    elif score >= 75: grade, desc = "B+", "Good"
    elif score >= 70: grade, desc = "B", "Satisfactory"
    elif score >= 65: grade, desc = "C+", "Acceptable"
    elif score >= 60: grade, desc = "C", "Marginal"
    elif score >= 50: grade, desc = "D", "Poor"
    else: grade, desc = "F", "Fail"

    return score, grade, desc


def recommend(eff: Dict, qual: Dict, beh: Dict, aut: Dict) -> List[str]:
    recs = []
    if eff.get("completion_rate", 100) < 85:
        recs.append(f"Completion rate low ({eff['completion_rate']:.0f}%) — review task definition")
    if eff.get("block_rate", 0) > 10:
        recs.append(f"Block rate high ({eff['block_rate']:.0f}%) — improve /blocked usage")
    if eff.get("gate_pass_rate", 100) < 90:
        recs.append(f"Gate pass rate low ({eff['gate_pass_rate']:.0f}%) — improve code quality")
    if qual.get("quality_base", 100) < 100:
        recs.append("Code quality issues — run lint fix")
    if beh.get("update_rate", 100) < 80:
        recs.append("State not updated recently — maintain state.json")
    if beh.get("tracking_score", 0) < 50:
        recs.append("Low change tracking — record recentChanges")
    if aut.get("autonomy_rate", 100) < 70:
        recs.append("Human intervention too high — clarify task boundaries")
    return recs


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

def save_result(result: BenchmarkResult) -> None:
    BENCHMARK_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")


def load_history(limit: int = 20) -> List[BenchmarkResult]:
    if not HISTORY_FILE.exists():
        return []
    results = []
    with open(HISTORY_FILE) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(BenchmarkResult(**json.loads(line)))
                except Exception:
                    pass
    return results[-limit:]


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def report_text(result: BenchmarkResult, history: List[BenchmarkResult]) -> str:
    eff = result.efficiency
    qual = result.quality
    beh = result.behavior
    aut = result.autonomy

    score_color = (
        green if result.score >= 80
        else yellow if result.score >= 60
        else red
    )

    lines = [
        "",
        f"{'='*60}",
        f"{bold('  HARNESS BENCHMARK')}",
        f"{'='*60}",
        f"  Project:     {result.project}",
        f"  Time:        {result.timestamp[:19]}",
        f"  Run time:    {result.run_duration_ms}ms",
        "",
        f"  {bold('FINAL SCORE')}   {score_color(f'{result.score:6.1f}/100')}  {bold(result.grade)} ({result.grade_desc})",
        "",
        f"  {bold('EFFICIENCY (40%)')}",
        f"    Completion     {bar(eff.get('completion_rate', 0))}  {eff.get('completion_rate', 0):.0f}%",
        f"    Block Rate     {bar(100-eff.get('block_rate', 0))}  {eff.get('block_rate', 0):.0f}%",
        f"    Gate Pass      {bar(eff.get('gate_pass_rate', 0))}  {eff.get('gate_pass_rate', 0):.0f}%",
        f"    First Try      {bar(eff.get('first_try_rate', 0))}  {eff.get('first_try_rate', 0):.0f}%",
        f"    Throughput     {eff.get('throughput', 0):.0f} tasks",
        "",
        f"  {bold('QUALITY (30%)')}",
        f"    Base           {bar(qual.get('quality_base', 0))}  {qual.get('quality_base', 0):.0f}",
        f"    Type Check     {bar(qual.get('type_rate', 0))}  {'PASS' if qual.get('type_rate') == 100 else 'FAIL'}",
        f"    Test           {bar(qual.get('test_rate', 0))}  {'PASS' if qual.get('test_rate') == 100 else 'FAIL'}",
        f"    Build          {bar(qual.get('build_rate', 0))}  {'PASS' if qual.get('build_rate') == 100 else 'FAIL'}",
        f"    console.log    {qual.get('console_logs', 0)} occurrences",
        f"    debugger       {qual.get('debuggers', 0)} occurrences",
        "",
        f"  {bold('BEHAVIOR (15%)')}",
        f"    Update Rate    {bar(beh.get('update_rate', 0))}  {beh.get('update_rate', 0):.0f}%",
        f"    Tracking       {bar(beh.get('tracking_score', 0))}  {beh.get('tracking_score', 0):.0f}",
        f"    Violations     {bar(beh.get('violation_score', 0))}  {beh.get('violation_score', 0):.0f}",
        f"    Last Updated   {beh.get('last_updated') or 'Never'}",
        "",
        f"  {bold('AUTONOMY (15%)')}",
        f"    Solo Rate      {bar(aut.get('autonomy_rate', 0))}  {aut.get('autonomy_rate', 0):.0f}%",
        f"    Corrections    {bar(aut.get('corrections_rate', 0))}  {aut.get('corrections_rate', 0):.0f}",
        f"    Escalation     {bar(aut.get('escalation_score', 0))}  {aut.get('escalation_score', 0):.0f}",
        "",
    ]

    if result.recommendations:
        lines.append(f"  {bold('RECOMMENDATIONS')}")
        for i, rec in enumerate(result.recommendations, 1):
            lines.append(f"    {i}. {rec}")
        lines.append("")

    if len(history) > 1:
        scores = [r.score for r in history]
        delta = result.score - scores[-2] if len(scores) >= 2 else 0
        arrow = "↑" if delta > 0 else "↓" if delta < 0 else "→"
        lines += [
            f"  {bold('HISTORY')}",
            f"    Runs:          {len(history)}",
            f"    Previous:      {scores[-2]:.1f}  {arrow} {delta:+.1f}",
            f"    Average:       {sum(scores)/len(scores):.1f}",
            "",
        ]

    lines.append(f"{'='*60}")
    return "\n".join(lines)


def bar(value: float, width: int = 20) -> str:
    filled = int(value / 100 * width)
    return f"[{'#'*filled}{'-'*(width-filled)}]"


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def report_markdown(result: BenchmarkResult, history: List[BenchmarkResult]) -> str:
    eff = result.efficiency
    qual = result.quality
    beh = result.behavior
    aut = result.autonomy

    lines = [
        f"# Harness Benchmark Report",
        "",
        f"**Project:** {result.project}",
        f"**Time:** {result.timestamp[:19]}",
        f"**Score:** {result.score:.1f}/100 ({result.grade}) — {result.grade_desc}",
        "",
        "## Scores",
        "",
        "| Dimension | Score | Weight |",
        "|-----------|-------|--------|",
        f"| Efficiency | {eff.get('completion_rate', 0):.0f}% | 40% |",
        f"| Quality | {qual.get('quality_base', 0):.0f} | 30% |",
        f"| Behavior | {beh.get('update_rate', 0):.0f}% | 15% |",
        f"| Autonomy | {aut.get('autonomy_rate', 0):.0f}% | 15% |",
        "",
        "## Details",
        "",
        f"- **Completion Rate:** {eff.get('completion_rate', 0):.1f}%",
        f"- **Block Rate:** {eff.get('block_rate', 0):.1f}%",
        f"- **Gate Pass Rate:** {eff.get('gate_pass_rate', 0):.1f}%",
        f"- **console.log count:** {qual.get('console_logs', 0)}",
        f"- **debugger count:** {qual.get('debuggers', 0)}",
        f"- **Last state update:** {beh.get('last_updated') or 'Never'}",
        f"- **Autonomy rate:** {aut.get('autonomy_rate', 0):.1f}%",
        "",
    ]

    if result.recommendations:
        lines += ["## Recommendations", ""]
        for rec in result.recommendations:
            lines.append(f"- {rec}")
        lines.append("")

    if len(history) > 1:
        scores = [r.score for r in history]
        lines += [
            "## Historical",
            "",
            f"- **Runs:** {len(history)}",
            f"- **Average:** {sum(scores)/len(scores):.1f}",
            "",
        ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main run
# ---------------------------------------------------------------------------

def run_benchmark(project: str, output: str = "text") -> BenchmarkResult:
    t0 = datetime.now()
    state = load_state(project)
    src_dir = find_source_dir(project)

    eff = measure_efficiency(state)
    qual = measure_quality(state, src_dir)
    beh = measure_behavior(state)
    aut = measure_autonomy(state)

    score, grade, desc = calculate_score(eff, qual, beh, aut)
    recs = recommend(eff, qual, beh, aut)
    duration_ms = int((datetime.now() - t0).total_seconds() * 1000)

    result = BenchmarkResult(
        project=project,
        score=score,
        grade=grade,
        grade_desc=desc,
        efficiency=eff,
        quality=qual,
        behavior=beh,
        autonomy=aut,
        recommendations=recs,
        timestamp=datetime.now().isoformat(),
        run_duration_ms=duration_ms,
    )

    save_result(result)

    history = load_history(10)
    if output == "markdown":
        print(report_markdown(result, history))
    else:
        print(report_text(result, history))

    return result


def show_history(limit: int = 20) -> None:
    history = load_history(limit)
    if not history:
        print("No benchmark history yet.")
        return
    print(f"\n{bold('Recent Benchmark Runs')}\n")
    print(f"  {'Score':>6}  {'Grade':>4}  {'Project':<40}  {'Time'}")
    print(f"  {'-'*6}  {'-'*4}  {'-'*40}  {'-'*20}")
    for r in history:
        score_color = green if r.score >= 80 else yellow if r.score >= 60 else red
        print(f"  {score_color(f'{r.score:>6.1f}'):>6}  {r.grade:>4}  {r.project[:40]:<40}  {r.timestamp[:19]}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Benchmark Runner")
    parser.add_argument("project", nargs="?", default=".", help="Project path")
    parser.add_argument("--project", "-p", dest="project_dash", help="Project path (alt)")
    parser.add_argument("--baseline", "-b", help="Baseline path (reserved)")
    parser.add_argument("--output", "-o", choices=["text", "json", "markdown"], default="text")
    parser.add_argument("--history", action="store_true", help="Show history")
    parser.add_argument("--limit", type=int, default=20, help="History limit")
    parser.add_argument("--save", "-s", help="Save result to file")
    args = parser.parse_args()

    project = args.project_dash or args.project

    if args.history:
        show_history(args.limit)
        return 0

    result = run_benchmark(project, args.output)

    if args.save:
        Path(args.save).write_text(json.dumps(asdict(result), indent=2))
        print(f"\n  Saved to {args.save}")

    # Exit code: 0 = S/A, 1 = B/C, 2 = D, 3 = F
    exit_code = 0 if result.score >= 80 else 1 if result.score >= 60 else 2 if result.score >= 50 else 3
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
