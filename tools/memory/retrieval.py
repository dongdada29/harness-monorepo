#!/usr/bin/env python3
"""
Memory Retrieval Engine for harness-monorepo

支持三种检索类型：
- Working Context: 当前任务上下文
- Episodic Memory: 相似历史任务
- Semantic Memory: 技术规范/架构决策/代码规范
"""

import json
import os
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional

from .store import MemoryEntry, MemoryStore

# ---------------------------------------------------------------------------
# Query types
# ---------------------------------------------------------------------------

@dataclass
class WorkingContextQuery:
    """Query for loading current task context."""
    type: str = "working_context"
    task_id: str = ""
    session_id: str = ""
    include_pending: bool = True


@dataclass
class EpisodicQuery:
    """Query for finding similar historical tasks."""
    type: str = "episodic"
    keywords: list[str] = field(default_factory=list)
    limit: int = 5
    time_range: Optional[dict[str, str]] = None  # {start, end} ISO dates
    business: Optional[str] = None
    tech_stack: Optional[list[str]] = None


@dataclass
class SemanticQuery:
    """Query for loading technical specs, architecture decisions, rules."""
    type: str = "semantic"
    scope: str = "project"  # project | tech_stack | business
    entities: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class WorkingContextResult:
    """Result for working context query."""
    task_history: list[dict]
    completed_steps: list[dict]
    pending_steps: list[dict]
    blocked_reason: Optional[str]


@dataclass
class EpisodicResult:
    """Result for episodic memory query."""
    episodes: list[dict]  # {taskId, summary, resolution, success, relevanceScore, timestamp}


@dataclass
class SemanticResult:
    """Result for semantic memory query."""
    constraints: list[str]
    patterns: list[str]
    rules: list[str]


# ---------------------------------------------------------------------------
# State integration
# ---------------------------------------------------------------------------

DEFAULT_STATE_DIR = Path.home() / ".harness" / "state"
STATE_FILE = DEFAULT_STATE_DIR / "state.json"


def _load_state() -> dict[str, Any]:
    """Load harness state file."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def _save_state(state: dict[str, Any]) -> None:
    """Save harness state file."""
    DEFAULT_STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2, ensure_ascii=False))


# ---------------------------------------------------------------------------
# Retrieval engine
# ---------------------------------------------------------------------------

class MemoryRetrieval:
    """Main retrieval engine combining store + state."""

    def __init__(self, store: Optional[MemoryStore] = None):
        self.store = store or MemoryStore()

    # ---------------------------------------------------------------------------
    # Working Context
    # ---------------------------------------------------------------------------

    def query_working_context(self, query: WorkingContextQuery) -> WorkingContextResult:
        """
        Load current task context from state.
        """
        state = _load_state()

        task_history = state.get("taskHistory", [])[-10:]
        current_task = state.get("currentTask", {})
        checkpoints = state.get("checkpoints", {})

        # Find completed/pending steps from current task
        completed = []
        pending = []
        blocked_reason = None

        if checkpoints:
            for cp, status in checkpoints.items():
                if status == "completed":
                    completed.append({"checkpoint": cp, "status": status})
                elif status == "pending":
                    pending.append({"checkpoint": cp, "status": status})
                elif status == "blocked":
                    blocked_reason = f"Checkpoint {cp} is blocked"

        # If current task has steps, use those
        if current_task.get("steps"):
            steps = current_task["steps"]
            completed = [s for s in steps if s.get("status") == "completed"]
            pending = [s for s in steps if s.get("status") in ("pending", "blocked")]
            blocked_reason = next((s.get("reason") for s in steps if s.get("status") == "blocked"), None)

        return WorkingContextResult(
            task_history=task_history,
            completed_steps=completed,
            pending_steps=pending,
            blocked_reason=blocked_reason,
        )

    # ---------------------------------------------------------------------------
    # Episodic Memory
    # ---------------------------------------------------------------------------

    def query_episodic(self, query: EpisodicQuery) -> EpisodicResult:
        """
        Find similar historical tasks by keywords + tech stack.
        """
        entries = self.store.read_entries()

        if not entries:
            return EpisodicResult(episodes=[])

        scored: list[tuple[float, dict]] = []
        query_kw = set(k.lower() for k in query.keywords)

        for entry in entries:
            score = 0.0
            text = f"{entry.title} {entry.content} {' '.join(entry.tags)}".lower()

            # Keyword overlap
            matched_kw = query_kw & set(text.split())
            score += len(matched_kw) * 0.2

            # Exact keyword matches
            for kw in query.keywords:
                if kw.lower() in text:
                    score += 0.15

            # Tech stack match
            if query.tech_stack:
                for tech in query.tech_stack:
                    if tech.lower() in text:
                        score += 0.25

            # Time decay: newer entries score higher
            try:
                entry_time = datetime.fromisoformat(entry.created_at.replace("Z", "+00:00"))
                days_old = (datetime.now(timezone.utc) - entry_time).days
                time_score = max(0, 1.0 - (days_old / 90))  # 90-day decay
                score += time_score * 0.2
            except Exception:
                pass

            # Filter by time range if specified
            if query.time_range:
                try:
                    entry_time = datetime.fromisoformat(entry.created_at.replace("Z", "+00:00"))
                    start = datetime.fromisoformat(query.time_range["start"])
                    end = datetime.fromisoformat(query.time_range["end"])
                    if not (start <= entry_time <= end):
                        continue
                except Exception:
                    pass

            if score > 0:
                scored.append((score, {
                    "taskId": entry.title,
                    "summary": entry.content[:200],
                    "resolution": entry.content,
                    "success": True,
                    "relevanceScore": min(score, 1.0),
                    "timestamp": entry.created_at,
                    "tags": entry.tags,
                }))

        # Sort by score descending, take top N
        scored.sort(key=lambda x: x[0], reverse=True)
        episodes = [ep for _, ep in scored[:query.limit]]

        return EpisodicResult(episodes=episodes)

    # ---------------------------------------------------------------------------
    # Semantic Memory
    # ---------------------------------------------------------------------------

    def query_semantic(self, query: SemanticQuery) -> SemanticResult:
        """
        Load technical constraints, patterns, and rules.
        """
        entries = self.store.read_entries()

        constraints: list[str] = []
        patterns: list[str] = []
        rules: list[str] = []

        # Load harness constraints from well-known paths
        harness_constraints = self._load_harness_constraints()
        constraints.extend(harness_constraints)

        # Filter entries by scope and entities
        for entry in entries:
            text = f"{entry.title} {entry.content}".lower()
            matched = True

            if query.entities:
                matched = any(e.lower() in text for e in query.entities)

            if not matched:
                continue

            # Categorize by tags or content heuristics
            tags_lower = [t.lower() for t in entry.tags]

            if "constraint" in tags_lower or any(k in text for k in ["must", "shall", "禁止", "require"]):
                constraints.append(f"[{entry.title}] {entry.content}")
            elif "pattern" in tags_lower or any(k in text for k in ["when", "优先", "策略"]):
                patterns.append(f"[{entry.title}] {entry.content}")
            elif "rule" in tags_lower or any(k in text for k in ["规则", "always", "never"]):
                rules.append(f"[{entry.title}] {entry.content}")
            else:
                # Default: treat as constraint if short, pattern if long
                if len(entry.content) < 100:
                    constraints.append(f"[{entry.title}] {entry.content}")
                else:
                    patterns.append(f"[{entry.title}] {entry.content}")

        return SemanticResult(
            constraints=constraints[:20],
            patterns=patterns[:20],
            rules=rules[:20],
        )

    # ---------------------------------------------------------------------------
    # CP0 Init — full retrieval pipeline
    # ---------------------------------------------------------------------------

    def cp0_init(self, task: dict[str, Any]) -> dict[str, Any]:
        """
        Full CP0 initialization retrieval pipeline.
        Returns dict with episodic, semantic, and working_context results.
        """
        start_time = time.time()

        keywords = self._extract_keywords(task.get("description", ""))
        tech_stack = task.get("techStack", [])

        # 1. Episodic retrieval
        episodic = self.query_episodic(EpisodicQuery(
            keywords=keywords,
            limit=5,
            tech_stack=tech_stack,
            time_range={
                "start": (datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
                "end": datetime.now(timezone.utc).isoformat(),
            },
        ))

        # 2. Semantic retrieval
        semantic = self.query_semantic(SemanticQuery(
            scope="project",
            entities=tech_stack,
        ))

        # 3. Working context
        wctx = self.query_working_context(WorkingContextQuery(
            task_id=task.get("id", ""),
            session_id=task.get("sessionId", ""),
            include_pending=True,
        ))

        duration_ms = int((time.time() - start_time) * 1000)

        result = {
            "status": "completed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "duration_ms": duration_ms,
            "retrieved": {
                "episodic_count": len(episodic.episodes),
                "semantic_count": len(semantic.constraints) + len(semantic.patterns),
                "has_context": wctx.blocked_reason is not None,
            },
            "episodic": episodic.episodes,
            "semantic": {
                "constraints": semantic.constraints,
                "patterns": semantic.patterns,
                "rules": semantic.rules,
            },
            "working_context": {
                "completed_steps": wctx.completed_steps,
                "pending_steps": wctx.pending_steps,
                "blocked_reason": wctx.blocked_reason,
            },
            "suggestions": [ep["resolution"][:500] for ep in episodic.episodes],
        }

        # Update state with retrieval info
        self._update_retrieval_state(result)

        return result

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _extract_keywords(self, text: str) -> list[str]:
        """Extract keywords from task description."""
        # Simple extraction: technical terms, camelCase, paths
        words = re.findall(r"[A-Z][a-z]+(?<![A-Z]{2})(?<![a-z])[A-Z]*(?=[A-Z]|$)|[a-z]+", text)
        # Filter common words
        stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from"}
        keywords = [w for w in words if len(w) > 2 and w.lower() not in stopwords]
        return list(set(keywords))[:10]

    def _load_harness_constraints(self) -> list[str]:
        """Load constraints from harness core docs."""
        constraints: list[str] = []
        harness_home = Path(os.environ.get("HARNESS_HOME", Path.home() / ".harness"))
        constraint_files = [
            harness_home / "core/harness/base/constraints.md",
            harness_home / "core/constraints.md",
        ]
        for f in constraint_files:
            if f.exists():
                text = f.read_text()
                # Extract lines with constraint patterns
                for line in text.split("\n"):
                    line = line.strip()
                    if line and any(line.startswith(p) for p in ["- ", "* ", "##", "###", "**"]):
                        constraints.append(line[:200])
        return constraints

    def _update_retrieval_state(self, result: dict[str, Any]) -> None:
        """Update state with last retrieval info."""
        state = _load_state()
        if "memory" not in state:
            state["memory"] = {}
        state["memory"]["lastRetrieval"] = {
            "timestamp": result["timestamp"],
            "type": "cp0_init",
            "episodic_hits": result["retrieved"]["episodic_count"],
            "semantic_hits": result["retrieved"]["semantic_count"],
            "duration_ms": result["duration_ms"],
        }
        _save_state(state)
