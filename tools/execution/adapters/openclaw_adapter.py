"""
OpenClaw Agent Adapter — drives real agent execution via `openclaw agent --local`.

CP0 → Load memory snapshot (injected as system context)
CP1 → Search skills (Skills Hub integration, deferred)
CP2 → Execute task via openclaw agent (real agent, not mock)
CP3 → Benchmark score (called separately after run)
"""

import json
import re
import subprocess
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

HARNESS_HOME = Path.home() / ".harness"


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

class AgentType(Enum):
    OPENCLAW = "openclaw"
    CODEX = "codex"
    PI = "pi"
    CLAUDE = "claude"


@dataclass
class AgentResponse:
    ok: bool
    text: str
    tool_calls: List = field(default_factory=list)
    session_id: Optional[str] = None
    duration_ms: int = 0
    error: Optional[str] = None


@dataclass
class TaskResult:
    task_id: str
    ok: bool
    response: AgentResponse
    cp0_snapshot_ms: int = 0
    cp1_skills_ms: int = 0
    cp2_exec_ms: int = 0
    cp3_score: Optional[float] = None
    duration_ms: int = 0


# ---------------------------------------------------------------------------
# Memory integration
# ---------------------------------------------------------------------------

def load_memory_snapshot() -> str:
    """Load current memory snapshot for CP0 injection."""
    snapshot_path = HARNESS_HOME / "memory" / ".snapshot.md"
    if snapshot_path.exists():
        return snapshot_path.read_text()
    return ""


# ---------------------------------------------------------------------------
# Core adapter
# ---------------------------------------------------------------------------

class OpenClawAdapter:
    """
    Drives real agent execution via `openclaw agent --local`.

    Usage:
        adapter = OpenClawAdapter(agent=AgentType.OPENCLAW)
        result = adapter.run("fix the login bug")
    """

    def __init__(
        self,
        agent: AgentType = AgentType.OPENCLAW,
        cwd: str = "~/workspace",
        timeout: int = 300,
        allowed_tools: Optional[List[str]] = None,
        model: Optional[str] = None,
    ):
        self.agent = agent
        self.cwd = Path(cwd).expanduser().resolve()
        self.timeout = timeout
        self.allowed_tools = allowed_tools
        self.model = model

        # Session management (for future multi-turn support)
        self._session_name: Optional[str] = None
        self._session_id: Optional[str] = None

    # ---------------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------------

    def run(self, task: str, max_turns: int = 10) -> TaskResult:
        """Run a full CP0→CP3 task. Returns TaskResult."""
        task_id = str(uuid.uuid4())[:8]
        started_at = datetime.now()

        # CP0: Load memory snapshot
        cp0_start = datetime.now()
        snapshot = load_memory_snapshot()
        cp0_ms = int((datetime.now() - cp0_start).total_seconds() * 1000)

        # CP1: deferred — Skills Hub called separately before run
        cp1_ms = 0
        skills_context = ""

        # CP2: Execute via openclaw agent
        cp2_start = datetime.now()
        response = self._exec_openclaw(task, snapshot, skills_context, max_turns)
        cp2_ms = int((datetime.now() - cp2_start).total_seconds() * 1000)

        total_ms = int((datetime.now() - started_at).total_seconds() * 1000)

        return TaskResult(
            task_id=task_id,
            ok=response.ok,
            response=response,
            cp0_snapshot_ms=cp0_ms,
            cp1_skills_ms=cp1_ms,
            cp2_exec_ms=cp2_ms,
            duration_ms=total_ms,
        )

    def exec(
        self,
        prompt: str,
        snapshot: str = "",
        skills_context: str = "",
        max_turns: int = 1,
    ) -> AgentResponse:
        """One-shot execution. Low-level API."""
        return self._exec_openclaw(prompt, snapshot, skills_context, max_turns)

    # ---------------------------------------------------------------------------
    # Internal
    # ---------------------------------------------------------------------------

    def _exec_openclaw(
        self,
        prompt: str,
        snapshot: str,
        skills_context: str,
        max_turns: int,
    ) -> AgentResponse:
        """Execute via `openclaw agent --local` CLI and parse JSON output."""

        # Build context prefix
        context_parts = []
        if snapshot:
            context_parts.append("[MEMORY SNAPSHOT]\n" + snapshot)
        if skills_context:
            context_parts.append("[RELEVANT SKILLS]\n" + skills_context)

        full_prompt = prompt
        if context_parts:
            context_block = "\n\n".join(context_parts)
            full_prompt = context_block + "\n\n[TASK]\n" + prompt

        # Generate a stable session ID
        session_id = "harness-" + uuid.uuid4().hex[:8]

        # Build command
        cmd = [
            "openclaw", "agent",
            "--session-id", session_id,
            "--message", full_prompt,
            "--local",
            "--json",
            "--timeout", str(min(self.timeout, 120)),
        ]

        if self.model:
            cmd += ["--model", self.model]

        started = datetime.now()
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(self.cwd),
                capture_output=True,
                text=True,
                timeout=self.timeout + 30,
            )
            duration_ms = int((datetime.now() - started).total_seconds() * 1000)
        except subprocess.TimeoutExpired:
            return AgentResponse(
                ok=False,
                text="",
                error="Timeout after " + str(self.timeout) + "s",
                duration_ms=self.timeout * 1000,
            )

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
            return AgentResponse(
                ok=False,
                text=stdout,
                error=err_msg or "Exit code " + str(proc.returncode),
                duration_ms=duration_ms,
            )

        # Parse JSON
        try:
            output = json.loads(response_text)
        except json.JSONDecodeError:
            return AgentResponse(ok=True, text=response_text, duration_ms=duration_ms)

        # Extract text from payloads
        text = ""
        for p in output.get("payloads", []):
            if isinstance(p, dict) and p.get("text"):
                text += p["text"] + "\n"

        if not text:
            text = output.get("meta", {}).get("finalAssistantVisibleText", "")

        # Extract tool calls from meta
        tool_calls = []
        for tc in output.get("meta", {}).get("toolCalls", []):
            if isinstance(tc, dict):
                tool_calls.append({
                    "name": tc.get("name", tc.get("function", {}).get("name", "unknown")),
                    "input": tc.get("input", tc.get("arguments", {})),
                })

        return AgentResponse(
            ok=True,
            text=text.strip(),
            tool_calls=tool_calls,
            session_id=session_id,
            duration_ms=output.get("meta", {}).get("durationMs", duration_ms),
        )


# ---------------------------------------------------------------------------
# Convenience factory
# ---------------------------------------------------------------------------

def create_adapter(
    agent: str = "openclaw",
    cwd: str = "~/workspace",
    timeout: int = 300,
    allowed_tools: Optional[List[str]] = None,
    model: Optional[str] = None,
) -> OpenClawAdapter:
    """Factory with string agent name."""
    try:
        agent_type = AgentType(agent.lower())
    except ValueError:
        agent_type = AgentType.OPENCLAW
    return OpenClawAdapter(
        agent=agent_type,
        cwd=cwd,
        timeout=timeout,
        allowed_tools=allowed_tools,
        model=model,
    )
