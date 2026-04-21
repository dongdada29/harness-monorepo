#!/usr/bin/env python3
"""
Harness Tool Execution Engine
==============================
Manages agent task execution with CP0→CP1→CP2→CP3 checkpoint protocol.
Drives real OpenClaw agent via `openclaw agent --local`.

Usage:
    python3 -m tools.execution run --task "fix the login bug"
    python3 -m tools.execution run --task "write a test" --agent openclaw --model glm-5
    python3 -m tools.execution status
    python3 -m tools.execution log --task-id <id>
"""

import argparse
import json
import os
import subprocess
import sys
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.skills.source import LocalSource, GitHubSource, SkillMeta
from tools.skills.installer import SkillInstaller
from tools.benchmark.runner import run_benchmark

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HARNESS_HOME = Path(os.environ.get("HARNESS_HOME", Path.home() / ".harness"))
EXEC_DIR = HARNESS_HOME / "execution"
STATE_DIR = HARNESS_HOME / "feedback" / "state"
MEMORY_SNAPSHOT = HARNESS_HOME / "memory" / ".snapshot.md"

# ---------------------------------------------------------------------------
# Enums (simple values, no typing.Literal needed for Python 3.9)
# ---------------------------------------------------------------------------

class Checkpoint:
    CP0 = "cp0"
    CP1 = "cp1"
    CP2 = "cp2"
    CP3 = "cp3"


AUTONOMY_LEVELS = {
    1: "Assistant — human does all",
    2: "Executor — agent executes, human approves",
    3: "Verifier — agent verifies, human reviews",
    4: "Submitter — agent opens PR, human merges",
    5: "Merger — agent auto-merges on CI",
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ExecutionStep:
    step_id: str
    checkpoint: str
    action: str
    tool: Optional[str] = None
    duration_ms: int = 0
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    error: Optional[str] = None
    timestamp: str = ""


@dataclass
class ExecutionTask:
    task_id: str
    description: str
    status: str
    current_checkpoint: str
    agent: str
    model: Optional[str]
    autonomy_level: int
    created_at: str
    updated_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    steps: List[Dict] = field(default_factory=list)
    result: Optional[Dict] = None
    error: Optional[str] = None
    project_path: str = "."


# ---------------------------------------------------------------------------
# OpenClaw Agent Adapter
# ---------------------------------------------------------------------------

def load_memory_snapshot() -> str:
    """Load current memory snapshot for CP0 injection."""
    if MEMORY_SNAPSHOT.exists():
        return MEMORY_SNAPSHOT.read_text()
    return ""


def run_openclaw_agent(
    prompt: str,
    snapshot: str = "",
    skills_context: str = "",
    session_id: Optional[str] = None,
    cwd: str = ".",
    timeout: int = 120,
    model: Optional[str] = None,
) -> Dict:
    """
    Execute a prompt via `openclaw agent --local --json`.
    Returns dict with: ok, text, duration_ms, error, tool_calls, session_id.
    """
    import uuid

    # Build context prefix
    context_parts = []
    if snapshot:
        context_parts.append("[MEMORY SNAPSHOT]\n" + snapshot)
    if skills_context:
        context_parts.append("[RELEVANT SKILLS]\n" + skills_context)

    full_prompt = prompt
    if context_parts:
        full_prompt = "\n\n".join(context_parts) + "\n\n[TASK]\n" + prompt

    if session_id is None:
        session_id = "harness-" + uuid.uuid4().hex[:8]

    cmd = [
        "openclaw", "agent",
        "--session-id", session_id,
        "--message", full_prompt,
        "--local",
        "--json",
        "--timeout", str(min(timeout, 120)),
    ]

    if model:
        cmd += ["--model", model]

    started = datetime.now()
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(Path(cwd).expanduser().resolve()),
            capture_output=True,
            text=True,
            timeout=timeout + 30,
        )
        duration_ms = int((datetime.now() - started).total_seconds() * 1000)
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "text": "",
            "error": "Timeout after " + str(timeout) + "s",
            "duration_ms": timeout * 1000,
            "tool_calls": [],
            "session_id": session_id,
        }

    stdout = proc.stdout.strip()
    stderr = proc.stderr.strip()

    # JSON comes through stderr in --local mode
    response_text = stderr if stderr else stdout

    if proc.returncode != 0 or not response_text:
        err_msg = ""
        if proc.returncode != 0:
            try:
                err_data = json.loads(stderr or stdout)
                err_msg = err_data.get("error", err_data.get("message", ""))
            except (json.JSONDecodeError, ValueError):
                err_msg = stderr or stdout
        return {
            "ok": False,
            "text": stdout,
            "error": err_msg or "Exit code " + str(proc.returncode),
            "duration_ms": duration_ms,
            "tool_calls": [],
            "session_id": session_id,
        }

    # Parse JSON
    try:
        output = json.loads(response_text)
    except json.JSONDecodeError:
        return {
            "ok": True,
            "text": response_text,
            "duration_ms": duration_ms,
            "tool_calls": [],
            "session_id": session_id,
        }

    # Extract text from payloads
    text = ""
    for p in output.get("payloads", []):
        if isinstance(p, dict) and p.get("text"):
            text += p["text"] + "\n"

    if not text:
        text = output.get("meta", {}).get("finalAssistantVisibleText", "")

    # Extract tool calls
    tool_calls = []
    for tc in output.get("meta", {}).get("toolCalls", []):
        if isinstance(tc, dict):
            tool_calls.append({
                "name": tc.get("name", tc.get("function", {}).get("name", "unknown")),
                "input": tc.get("input", tc.get("arguments", {})),
            })

    return {
        "ok": True,
        "text": text.strip(),
        "duration_ms": output.get("meta", {}).get("durationMs", duration_ms),
        "tool_calls": tool_calls,
        "session_id": session_id,
    }


# ---------------------------------------------------------------------------
# Execution Engine
# ---------------------------------------------------------------------------

class ExecutionEngine:
    """
    Runs task loops with CP0→CP1→CP2→CP3 checkpoint protocol.

    CP0: Load memory snapshot (harness memory, not agent memory)
    CP1: Plan approach (rule-based + optional LLM)
    CP2: Execute via OpenClaw agent (real agent)
    CP3: Verify + score
    """

    def __init__(
        self,
        project_path: str = ".",
        autonomy_level: int = 2,
        agent: str = "openclaw",
        model: Optional[str] = None,
        timeout: int = 120,
    ):
        self.project_path = Path(project_path).expanduser().resolve()
        self.autonomy_level = autonomy_level
        self.agent = agent
        self.model = model
        self.timeout = timeout
        self._tick("Engine initialized (cwd={}, agent={}, model={})".format(
            self.project_path.name, agent, model or "default"))

    def _tick(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        print("  [{}] {}".format(ts, msg))

    def _search_skills(self, description: str) -> str:
        """Search Skills Hub for relevant skills at CP1. Returns formatted skills context."""
        query = description.lower()
        results = []

        # Search local templates
        local = LocalSource()
        results.extend(local.search(query, limit=5))

        # Search GitHub repos (non-blocking, skip on error)
        try:
            github = GitHubSource()
            results.extend(github.search(query, limit=5))
        except Exception:
            pass

        if not results:
            return ""

        # Format skills context
        lines = ["[RELEVANT SKILLS]", ""]
        for meta in results[:8]:
            lines.append(f"## {meta.name}")
            lines.append(f"> {meta.description}" if meta.description else f"> Source: {meta.source}")
            lines.append(f"Tags: {', '.join(meta.tags)}" if meta.tags else "")
            lines.append(f"Location: ~/.harness/skills/{meta.source}/{meta.name}/" if hasattr(meta, 'source') else "")
            lines.append("")

        return "\n".join(lines)

    def _step(self, task: ExecutionTask, cp: str, action: str,
              input_data: Optional[Dict] = None,
              output_data: Optional[Dict] = None,
              error: Optional[str] = None) -> ExecutionStep:
        step = ExecutionStep(
            step_id=uuid.uuid4().hex[:8],
            checkpoint=cp,
            action=action,
            input_data=input_data,
            output_data=output_data,
            error=error,
            timestamp=datetime.now().isoformat(),
        )
        task.steps.append(asdict(step))
        return step

    def run_task(self, description: str) -> ExecutionTask:
        """Run a single task through CP0→CP1→CP2→CP3."""
        task_id = uuid.uuid4().hex[:8]
        now = datetime.now().isoformat()

        task = ExecutionTask(
            task_id=task_id,
            description=description,
            status="running",
            current_checkpoint=Checkpoint.CP0,
            agent=self.agent,
            model=self.model,
            autonomy_level=self.autonomy_level,
            created_at=now,
            updated_at=now,
            started_at=now,
            project_path=str(self.project_path),
        )

        print("")
        print("=" * 60)
        print("  Task: {}".format(description))
        print("=" * 60)
        print("  Task ID:    {}".format(task_id))
        print("  Agent:      {}".format(self.agent))
        print("  Model:      {}".format(self.model or "default"))
        print("  Autonomy:   L{} ({})".format(
            self.autonomy_level, AUTONOMY_LEVELS.get(self.autonomy_level, "")))
        print("  Working:    {}".format(self.project_path))
        print("")

        # ── CP0: Initialize ──────────────────────────────────────
        self._tick("[CP0] Initializing...")
        task.current_checkpoint = Checkpoint.CP0
        cp0_data = {"cwd": str(self.project_path)}
        snapshot = load_memory_snapshot()
        cp0_data["snapshot_loaded"] = len(snapshot) > 0
        cp0_data["snapshot_chars"] = len(snapshot)
        self._step(task, Checkpoint.CP0, "initialize",
                   input_data=cp0_data,
                   output_data={"ok": True, "memory_snapshot_chars": len(snapshot)})
        print("")

        # ── CP1: Plan ───────────────────────────────────────────
        self._tick("[CP1] Planning...")
        task.current_checkpoint = Checkpoint.CP1
        plan = self._plan(description)
        plan_data = {"strategy": plan["strategy"], "steps": plan["steps"]}
        self._step(task, Checkpoint.CP1, "plan", output_data=plan_data)
        self._tick("     Strategy: {}".format(plan["strategy"]))
        for i, s in enumerate(plan["steps"]):
            self._tick("     Step {}: [{}] {}".format(i+1, s.get("tool", "?"), s.get("prompt", "")[:60]))
        print("")

        # ── CP2: Execute ────────────────────────────────────────
        task.current_checkpoint = Checkpoint.CP2
        self._tick("[CP2] Executing via openclaw agent...")

        # Build the agent prompt with plan context
        plan_context = self._format_plan(plan)
        full_prompt = (
            "You are running inside a harness execution engine.\n\n"
            + plan_context
            + "\n\n"
            + (plan.get("skills_context", "") + "\n\n")
            + "TASK: "
            + description
            + "\n\nWork in "
            + str(self.project_path)
            + ". Execute the planned steps. Report what you did."
        )

        cp2_start = datetime.now()
        agent_result = run_openclaw_agent(
            prompt=full_prompt,
            snapshot=snapshot,
            session_id="harness-" + task_id,
            cwd=str(self.project_path),
            timeout=self.timeout,
            model=self.model,
        )
        cp2_ms = agent_result.get("duration_ms", 0)

        cp2_data = {
            "ok": agent_result["ok"],
            "duration_ms": cp2_ms,
            "tool_calls": len(agent_result.get("tool_calls", [])),
        }
        self._step(task, Checkpoint.CP2, "execute",
                   input_data={"prompt": full_prompt[:200], "plan": plan},
                   output_data=cp2_data,
                   error=agent_result.get("error"))

        if agent_result["ok"]:
            self._tick("     Agent completed in {}ms".format(cp2_ms))
            self._tick("     Response ({} chars): {}".format(
                len(agent_result["text"]),
                agent_result["text"][:120].replace("\n", " ")))
        else:
            self._tick("     ERROR: {}".format(agent_result.get("error", "unknown")))
        print("")

        # ── CP3: Verify ────────────────────────────────────────
        task.current_checkpoint = Checkpoint.CP3
        self._tick("[CP3] Verifying...")
        response_text = agent_result.get("text", "")
        score = self._verify(task, description, response_text)
        grade = getattr(task, '_benchmark_grade', 'N/A')
        self._step(task, Checkpoint.CP3, "verify", output_data={"score": score, "grade": grade})

        if score >= 60:
            task.status = "completed"
            task.result = {"score": score, "grade": grade}
            self._tick(f"     Verified. Score: {score:.1f}/100 ({grade})")
        else:
            task.status = "failed"
            task.error = "verification score below threshold"
            self._tick(f"     FAILED: score {score:.1f} below threshold")

        task.completed_at = datetime.now().isoformat()
        task.updated_at = task.completed_at

        print("")
        print("  Result: {} | Checkpoint: {} | Duration: {}ms".format(
            task.status.upper(), task.current_checkpoint, cp2_ms))
        print("=" * 60)

        self._save_task(task)
        return task

    def _plan(self, description: str) -> Dict:
        """Simple rule-based planner with skills search."""
        d = description.lower()
        skills_context = self._search_skills(description)

        if "fix" in d or "bug" in d:
            strategy = "bugfix"
            steps = [
                {"tool": "openclaw_agent", "prompt": "Find the root cause of: " + description},
                {"tool": "openclaw_agent", "prompt": "Fix the identified issue and show the diff"},
            ]
        elif "add" in d or "implement" in d or "new" in d or "create" in d:
            strategy = "feature"
            steps = [
                {"tool": "openclaw_agent", "prompt": "Implement: " + description},
                {"tool": "openclaw_agent", "prompt": "Verify the implementation works and report what was done"},
            ]
        elif "test" in d:
            strategy = "test"
            steps = [
                {"tool": "openclaw_agent", "prompt": "Write tests for: " + description},
            ]
        elif "review" in d or "check" in d:
            strategy = "review"
            steps = [
                {"tool": "openclaw_agent", "prompt": "Review and analyze: " + description},
            ]
        else:
            strategy = "general"
            steps = [
                {"tool": "openclaw_agent", "prompt": description},
            ]

        return {"strategy": strategy, "steps": steps, "skills_context": skills_context}

    def _format_plan(self, plan: Dict) -> str:
        lines = ["[HARNESS PLAN]", "Strategy: " + plan["strategy"], ""]
        for i, s in enumerate(plan["steps"]):
            lines.append("Step {}: [{}] {}".format(i+1, s.get("tool", "?"), s.get("prompt", "")))
        return "\n".join(lines)

    def _verify(self, task: Any, description: str, output: str) -> float:
        """Verify task completion using Benchmark Runner (CP3)."""
        try:
            result = run_benchmark(str(self.project_path), output="json")
            score = result.score

            # Store benchmark result in task for CP3 step (skip if task is None)
            if task is not None:
                task._benchmark_grade = result.grade
                task._benchmark_result = result

            # Print benchmark summary
            self._tick(f"     Benchmark: {score:.1f}/100 ({result.grade})")
            if result.recommendations:
                for rec in result.recommendations[:3]:
                    self._tick(f"       → {rec}")

            return score
        except Exception as e:
            self._tick(f"     Benchmark error: {e}, falling back to quality check")
            # Fallback: simple quality heuristics
            quality = 100
            if len(output) < 50:
                quality -= 30
            if "error" in output.lower() or "fail" in output.lower():
                quality -= 20
            quality = max(0, min(100, quality))
            return float(quality)

    def _save_task(self, task: ExecutionTask):
        EXEC_DIR.mkdir(parents=True, exist_ok=True)
        f = EXEC_DIR / (task.task_id + ".json")
        f.write_text(json.dumps(asdict(task), indent=2))
        latest = EXEC_DIR / "latest.json"
        latest.write_text(json.dumps(asdict(task), indent=2))

    def list_tasks(self) -> List[ExecutionTask]:
        if not EXEC_DIR.exists():
            return []
        tasks = []
        for f in EXEC_DIR.glob("*.json"):
            if f.name == "latest.json":
                continue
            try:
                tasks.append(ExecutionTask(**json.loads(f.read_text())))
            except Exception:
                pass
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_run(project: str, description: str, level: int,
            agent: str, model: Optional[str], timeout: int) -> int:
    engine = ExecutionEngine(
        project_path=project,
        autonomy_level=level,
        agent=agent,
        model=model,
        timeout=timeout,
    )
    task = engine.run_task(description)
    return 0 if task.status == "completed" else 1


def cmd_status() -> int:
    engine = ExecutionEngine()
    tasks = engine.list_tasks()
    if not tasks:
        print("\nNo tasks executed yet.\n")
        return 0

    print("\n" + "=" * 60)
    print("  Recent Tasks ({} total)".format(len(tasks)))
    print("=" * 60 + "\n")

    for t in tasks[:10]:
        icon = {"completed": "✅", "failed": "❌", "running": "⏳"}.get(t.status, "⏹")
        print("  {} [{}] {}".format(icon, t.task_id, t.description[:45]))
        print("       Agent: {} | CP: {} | {}".format(t.agent, t.current_checkpoint, t.created_at[:19]))
        print("")

    return 0


def cmd_log(task_id: str) -> int:
    f = EXEC_DIR / (task_id + ".json")
    if not f.exists():
        print("Task {} not found.".format(task_id))
        return 1
    task = json.loads(f.read_text())
    print(json.dumps(task, indent=2))
    return 0


def cmd_tasks(limit: int) -> int:
    """List recent tasks in compact form."""
    engine = ExecutionEngine()
    tasks = engine.list_tasks()
    if not tasks:
        print("No tasks.")
        return 0
    for t in tasks[:limit]:
        icon = {"completed": "✅", "failed": "❌", "running": "⏳"}.get(t.status, "⏹")
        print("{} [{}] {}  CP={}  {}".format(
            icon, t.task_id, t.description[:40], t.current_checkpoint, t.created_at[:19]))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Harness Execution Engine — CP0→CP3 agent task runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", metavar="COMMAND")

    # run
    run_p = sub.add_parser("run", help="Run a task")
    run_p.add_argument("--task", "-t", required=True, help="Task description")
    run_p.add_argument("--project", "-p", default=".", help="Project path")
    run_p.add_argument("--level", "-l", type=int, default=2, help="Autonomy level (1-5)")
    run_p.add_argument("--agent", default="openclaw", help="Agent type (openclaw/codex/pi/claude)")
    run_p.add_argument("--model", "-m", help="Model override")
    run_p.add_argument("--timeout", type=int, default=120, help="Timeout per step (seconds)")

    # status
    sub.add_parser("status", help="Show recent tasks")

    # tasks (compact list)
    tasks_p = sub.add_parser("tasks", help="Compact task list")
    tasks_p.add_argument("--limit", "-n", type=int, default=10)

    # log
    log_p = sub.add_parser("log", help="Show task details")
    log_p.add_argument("task_id", help="Task ID")

    args = parser.parse_args()

    if args.cmd == "run":
        return cmd_run(args.project, args.task, args.level,
                       args.agent, args.model, args.timeout)
    elif args.cmd == "status":
        return cmd_status()
    elif args.cmd == "tasks":
        return cmd_tasks(args.limit)
    elif args.cmd == "log":
        return cmd_log(args.task_id)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
