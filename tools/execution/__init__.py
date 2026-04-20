#!/usr/bin/env python3
"""
Harness Tool Execution Engine
==============================
Manages agent task execution with CP0→CP1→CP2→CP3 checkpoint protocol.

Usage:
    python3 -m tools.execution run --task "fix the login bug"
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
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HARNESS_HOME = Path(os.environ.get("HARNESS_HOME", Path.home() / ".harness"))
EXEC_DIR = HARNESS_HOME / "execution"
STATE_DIR = HARNESS_HOME / "feedback" / "state"


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Checkpoint(str, Enum):
    CP0 = "cp0"   # Initialize
    CP1 = "cp1"   # Plan
    CP2 = "cp2"   # Execute
    CP3 = "cp3"   # Verify
    CP4 = "cp4"   # Complete


class AutonomyLevel(int, Enum):
    L1 = 1  # Assistant — human does all
    L2 = 2  # Executor — agent executes, human approves
    L3 = 3  # Verifier — agent verifies, human reviews
    L4 = 4  # Submitter — agent opens PR, human merges
    L5 = 5  # Merger — agent auto-merges on CI
    L6 = 6  # Auto-respond simple feedback
    L7 = 7  # Human only when judgment needed
    L8 = 8  # Auto-merge all CI-passed
    L9 = 9  # Self-learning + harness optimization


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class TaskStep:
    step_id: str
    checkpoint: str
    action: str
    tool: Optional[str] = None
    input_data: Optional[Dict] = None
    output_data: Optional[Dict] = None
    error: Optional[str] = None
    duration_ms: int = 0
    timestamp: str = ""


@dataclass
class ExecutionTask:
    task_id: str
    description: str
    status: str
    current_checkpoint: str
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
# Tool Registry
# ---------------------------------------------------------------------------

class ToolRegistry:
    """Discovers and manages available tools."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._register_builtin()

    def _register_builtin(self):
        """Register built-in tool implementations."""
        self._tools["exec"] = self._tool_exec
        self._tools["read"] = self._tool_read
        self._tools["write"] = self._tool_write
        self._tools["edit"] = self._tool_edit
        self._tools["grep"] = self._tool_grep

    def list(self) -> List[str]:
        return list(self._tools.keys())

    def execute(self, tool: str, input_data: Dict) -> Dict:
        if tool not in self._tools:
            return {"success": False, "error": f"Unknown tool: {tool}"}
        try:
            return self._tools[tool](input_data)
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_exec(self, data: Dict) -> Dict:
        cmd = data.get("command", "")
        cwd = data.get("cwd", ".")
        timeout = data.get("timeout", 30)
        if not cmd:
            return {"success": False, "error": "No command provided"}
        try:
            r = subprocess.run(
                cmd, shell=True, cwd=cwd,
                capture_output=True, text=True,
                timeout=timeout,
            )
            return {
                "success": r.returncode == 0,
                "exit_code": r.returncode,
                "stdout": r.stdout,
                "stderr": r.stderr,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": f"Timeout after {timeout}s"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_read(self, data: Dict) -> Dict:
        path = data.get("path", "")
        if not path:
            return {"success": False, "error": "No path provided"}
        try:
            p = Path(path).expanduser()
            if not p.exists():
                return {"success": False, "error": "File not found"}
            content = p.read_text()
            return {"success": True, "content": content, "lines": len(content.splitlines())}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_write(self, data: Dict) -> Dict:
        path = data.get("path", "")
        content = data.get("content", "")
        if not path:
            return {"success": False, "error": "No path provided"}
        try:
            p = Path(path).expanduser()
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content)
            return {"success": True, "bytes": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_edit(self, data: Dict) -> Dict:
        path = data.get("path", "")
        old_text = data.get("oldText", "")
        new_text = data.get("newText", "")
        if not path or not old_text:
            return {"success": False, "error": "Missing path or oldText"}
        try:
            p = Path(path).expanduser()
            content = p.read_text()
            if old_text not in content:
                return {"success": False, "error": "oldText not found in file"}
            new_content = content.replace(old_text, new_text, 1)
            p.write_text(new_content)
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _tool_grep(self, data: Dict) -> Dict:
        pattern = data.get("pattern", "")
        path = data.get("path", ".")
        if not pattern:
            return {"success": False, "error": "No pattern provided"}
        try:
            r = subprocess.run(
                ["grep", "-r", "-n", pattern, path,
                 "--include=*.ts", "--include=*.tsx",
                 "--include=*.js", "--include=*.py"],
                capture_output=True, text=True, timeout=30,
            )
            lines = [l for l in r.stdout.split("\n") if l]
            return {"success": True, "matches": lines, "count": len(lines)}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ---------------------------------------------------------------------------
# Execution Engine
# ---------------------------------------------------------------------------

class ExecutionEngine:
    """Runs task loops with CP0→CP1→CP2→CP3 checkpoint protocol."""

    def __init__(self, project_path: str = ".", autonomy_level: int = 2):
        self.project_path = Path(project_path)
        self.autonomy_level = autonomy_level
        self.tools = ToolRegistry()
        self._load_state()

    def _load_state(self):
        state_file = STATE_DIR / "state.json"
        if state_file.exists():
            self.state = json.loads(state_file.read_text())
        else:
            self.state = {"autonomy": {"level": self.autonomy_level}}

    def _save_state(self, updates: Dict):
        state_file = STATE_DIR / "state.json"
        state_file.parent.mkdir(parents=True, exist_ok=True)
        current = {}
        if state_file.exists():
            current = json.loads(state_file.read_text())
        current.update(updates)
        state_file.write_text(json.dumps(current, indent=2))
        self.state.update(updates)

    def _tick(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"  [{ts}] {msg}")

    def run_task(self, description: str) -> ExecutionTask:
        """Run a single task through CP0→CP1→CP2→CP3."""
        task_id = str(uuid.uuid4())[:8]
        now = datetime.now().isoformat()

        task = ExecutionTask(
            task_id=task_id,
            description=description,
            status=TaskStatus.RUNNING.value,
            current_checkpoint=Checkpoint.CP0.value,
            autonomy_level=self.autonomy_level,
            created_at=now,
            updated_at=now,
            project_path=str(self.project_path),
        )

        print(f"\n{'='*56}")
        print(f"  {description}")
        print(f"{'='*56}")
        print(f"  Task ID: {task_id}")
        print(f"  Autonomy: L{self.autonomy_level}")
        print()

        # ── CP0: Initialize ──────────────────────────────────────
        self._tick(f"[CP0] Initializing task...")
        step = self._make_step(Checkpoint.CP0, "initialize", {"description": description})
        self._tick(f"[CP0] State loaded, tools registered: {', '.join(self.tools.list())}")
        step.output_data = {"tools": self.tools.list()}
        task.steps.append(asdict(step))

        # ── CP1: Plan ────────────────────────────────────────────
        task.current_checkpoint = Checkpoint.CP1.value
        self._tick(f"[CP1] Planning approach...")
        step = self._make_step(Checkpoint.CP1, "plan")
        plan = self._plan(description)
        step.output_data = plan
        self._tick(f"[CP1] Planned: {plan.get('strategy', 'unknown')}")
        self._tick(f"[CP1] Steps: {len(plan.get('steps', []))}")
        task.steps.append(asdict(step))

        # ── CP2: Execute ─────────────────────────────────────────
        task.current_checkpoint = Checkpoint.CP2.value
        self._tick(f"[CP2] Executing {len(plan.get('steps', []))} steps...")
        step = self._make_step(Checkpoint.CP2, "execute", plan)
        result = self._execute_plan(plan)
        step.output_data = result
        task.steps.append(asdict(step))

        if not result.get("success"):
            task.status = TaskStatus.FAILED.value
            task.error = result.get("error", "Execution failed")
            self._tick(f"[CP2] FAILED: {task.error}")
        else:
            # ── CP3: Verify ──────────────────────────────────────
            task.current_checkpoint = Checkpoint.CP3.value
            self._tick(f"[CP3] Verifying...")
            step = self._make_step(Checkpoint.CP3, "verify", result)
            verified = self._verify(result)
            step.output_data = verified
            task.steps.append(asdict(step))

            if verified.get("success"):
                task.status = TaskStatus.COMPLETED.value
                self._tick(f"[CP3] ✅ Verified successfully")
            else:
                task.status = TaskStatus.FAILED.value
                task.error = verified.get("error", "Verification failed")
                self._tick(f"[CP3] ❌ Verification failed: {task.error}")

        task.completed_at = datetime.now().isoformat()
        task.updated_at = task.completed_at

        print(f"\n  Status: {task.status}")
        print(f"  Checkpoint: {task.current_checkpoint}")

        self._save_task(task)
        return task

    def _make_step(self, cp: Checkpoint, action: str, input_data: Optional[Dict] = None) -> TaskStep:
        return TaskStep(
            step_id=str(uuid.uuid4())[:8],
            checkpoint=cp.value,
            action=action,
            input_data=input_data,
            timestamp=datetime.now().isoformat(),
        )

    def _plan(self, description: str) -> Dict:
        """Simple rule-based planner (no LLM required)."""
        desc_lower = description.lower()

        if "fix" in desc_lower or "bug" in desc_lower:
            strategy = "bugfix"
        elif "add" in desc_lower or "implement" in desc_lower or "new" in desc_lower:
            strategy = "feature"
        elif "refactor" in desc_lower or "clean" in desc_lower:
            strategy = "refactor"
        elif "test" in desc_lower:
            strategy = "test"
        else:
            strategy = "general"

        steps = []

        if strategy == "bugfix":
            steps = [
                {"tool": "grep", "params": {"pattern": "TODO\\|FIXME\\|BUG", "path": str(self.project_path)}},
                {"tool": "read", "params": {"path": str(self.project_path / "state.json")}},
                {"tool": "exec", "params": {"command": "grep -r 'error\\|Error\\|fail' src/", "cwd": str(self.project_path)}},
            ]
        elif strategy == "feature":
            steps = [
                {"tool": "grep", "params": {"pattern": "export\\|import", "path": str(self.project_path)}},
                {"tool": "read", "params": {"path": str(self.project_path / "README.md")}},
            ]
        else:
            steps = [
                {"tool": "exec", "params": {"command": "ls -la", "cwd": str(self.project_path)}},
            ]

        return {"strategy": strategy, "steps": steps}

    def _execute_plan(self, plan: Dict) -> Dict:
        """Execute planned steps."""
        results = []
        for i, step_def in enumerate(plan.get("steps", [])):
            tool_name = step_def.get("tool", "exec")
            params = step_def.get("params", {})
            self._tick(f"[CP2] Step {i+1}: {tool_name}")
            result = self.tools.execute(tool_name, params)
            results.append({"step": i+1, "tool": tool_name, "result": result})
            if not result.get("success") and tool_name != "grep":
                return {"success": False, "error": f"Step {i+1} failed: {result.get('error')}", "results": results}
        return {"success": True, "results": results}

    def _verify(self, result: Dict) -> Dict:
        """Verify execution results."""
        if not result.get("success"):
            return {"success": False, "error": result.get("error")}
        return {"success": True, "steps_completed": len(result.get("results", []))}

    def _save_task(self, task: ExecutionTask):
        EXEC_DIR.mkdir(parents=True, exist_ok=True)
        f = EXEC_DIR / f"{task.task_id}.json"
        f.write_text(json.dumps(asdict(task), indent=2))

    def list_tasks(self) -> List[ExecutionTask]:
        if not EXEC_DIR.exists():
            return []
        tasks = []
        for f in EXEC_DIR.glob("*.json"):
            try:
                tasks.append(ExecutionTask(**json.loads(f.read_text())))
            except Exception:
                pass
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def cmd_run(project: str, description: str, level: int):
    engine = ExecutionEngine(project, level)
    task = engine.run_task(description)
    return 0 if task.status == TaskStatus.COMPLETED.value else 1


def cmd_status():
    engine = ExecutionEngine()
    tasks = engine.list_tasks()
    if not tasks:
        print("No tasks executed yet.")
        return 0
    print(f"\n{'='*56}")
    print(f"  Recent Tasks ({len(tasks)} total)")
    print(f"{'='*56}\n")
    for t in tasks[:10]:
        status_icon = "✅" if t.status == "completed" else "❌" if t.status == "failed" else "⏳" if t.status == "running" else "⏹"
        print(f"  {status_icon} [{t.task_id}] {t.description[:40]}")
        print(f"       CP: {t.current_checkpoint}  |  Status: {t.status}  |  {t.created_at[:19]}")
        print()
    return 0


def cmd_log(task_id: str):
    f = EXEC_DIR / f"{task_id}.json"
    if not f.exists():
        print(f"Task {task_id} not found.")
        return 1
    task = json.loads(f.read_text())
    print(json.dumps(task, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Harness Execution Engine")
    sub = parser.add_subparsers(dest="cmd")

    run_parser = sub.add_parser("run", help="Run a task")
    run_parser.add_argument("--task", "-t", required=True, help="Task description")
    run_parser.add_argument("--project", "-p", default=".", help="Project path")
    run_parser.add_argument("--level", "-l", type=int, default=2, help="Autonomy level (1-9)")

    sub.add_parser("status", help="Show recent tasks")
    log_parser = sub.add_parser("log", help="Show task log")
    log_parser.add_argument("task_id", help="Task ID")

    args = parser.parse_args()

    if args.cmd == "run":
        return cmd_run(args.project, args.task, args.level)
    elif args.cmd == "status":
        return cmd_status()
    elif args.cmd == "log":
        return cmd_log(args.task_id)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())