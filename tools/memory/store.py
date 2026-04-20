#!/usr/bin/env python3
"""
Memory Store — Frozen Snapshot Pattern for harness-monorepo

Session 开始时读取 MEMORY.md 快照注入 System Prompt，
Mid-session 写入不改变 System Prompt，保持 prefix cache 稳定。

基于 Hermes Agent memory_tool.py 设计，适配 harness 场景。
"""

import fcntl
import hashlib
import os
import re
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".harness"))
MEMORY_DIR = HERMES_HOME / "memory"
MEMORY_FILE = MEMORY_DIR / "MEMORY.md"
USER_FILE = MEMORY_DIR / "USER.md"
SNAPSHOT_FILE = MEMORY_DIR / ".snapshot.md"

# Character limits (model-independent)
MAX_MEMORY_CHARS = 40_000
MAX_USER_CHARS = 8_000

# Entry delimiter
ENTRY_DELIMITER = "\n§\n"
ENTRY_START = "## "
ENTRY_END = "\n"

# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class MemoryEntry:
    """A single memory entry."""
    title: str
    content: str
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    embedding: Optional[str] = None  # future use

    def to_text(self) -> str:
        tags_line = f"tags: {', '.join(self.tags)}" if self.tags else ""
        header = f"## {self.title}\n{tags_line}\n"
        return header + self.content.strip()

    @classmethod
    def from_text(cls, text: str) -> "MemoryEntry":
        """Parse a memory entry from text."""
        lines = text.strip().split("\n")
        if not lines:
            raise ValueError("Empty entry")

        # Extract title from first line (## Title)
        if lines[0].startswith(ENTRY_START.strip()):
            title = lines[0][len(ENTRY_START):].strip()
            lines = lines[1:]
        else:
            title = "Untitled"

        # Extract tags from second line if present
        tags = []
        if lines and lines[0].lower().startswith("tags:"):
            tags = [t.strip() for t in lines[0][5:].split(",")]
            lines = lines[1:]

        # Everything else is content
        content = "\n".join(lines).strip()

        return cls(title=title, content=content, tags=tags)


@dataclass
class MemoryStore:
    """File-backed memory store with frozen snapshot support."""

    memory_path: Path = field(default_factory=lambda: MEMORY_FILE)
    user_path: Path = field(default_factory=lambda: USER_FILE)
    snapshot_path: Path = field(default_factory=lambda: SNAPSHOT_FILE)

    _lock_path: Path = field(init=False, repr=False)

    def __post_init__(self):
        self._lock_path = self.memory_path.with_suffix(".lock")
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------------
    # Locking
    # ---------------------------------------------------------------------------

    def _lock(self) -> int:
        """Acquire exclusive lock on memory file. Returns fd."""
        fd = os.open(str(self._lock_path), os.O_CREAT | os.O_RDWR)
        fcntl.flock(fd, fcntl.LOCK_EX)
        return fd

    def _unlock(self, fd: int) -> None:
        """Release lock and close fd."""
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

    def _atomic_write(self, path: Path, content: str) -> None:
        """Write content atomically via rename."""
        tmp = path.with_suffix(f".tmp.{os.getpid()}.{time.time_ns()}")
        tmp.write_text(content, encoding="utf-8")
        os.rename(tmp, path)

    # ---------------------------------------------------------------------------
    # Read
    # ---------------------------------------------------------------------------

    def read_entries(self) -> list[MemoryEntry]:
        """Read all entries from memory file."""
        if not self.memory_path.exists():
            return []

        text = self.memory_path.read_text(encoding="utf-8")
        entries: list[MemoryEntry] = []

        for part in text.split(ENTRY_DELIMITER):
            part = part.strip()
            if not part:
                continue
            # Strip title line
            lines = part.split("\n")
            if lines and lines[0].startswith(ENTRY_START.strip()):
                lines = lines[1:]
            cleaned = "\n".join(lines).strip()
            if cleaned:
                try:
                    entries.append(MemoryEntry.from_text(part))
                except ValueError:
                    # Malformed entry, skip
                    pass

        return entries

    def read_user_entries(self) -> list[MemoryEntry]:
        """Read all entries from user file."""
        if not self.user_path.exists():
            return []

        text = self.user_path.read_text(encoding="utf-8")
        entries: list[MemoryEntry] = []

        for part in text.split(ENTRY_DELIMITER):
            part = part.strip()
            if not part:
                continue
            try:
                entries.append(MemoryEntry.from_text(part))
            except ValueError:
                pass

        return entries

    def get_snapshot(self) -> tuple[str, str]:
        """
        Get frozen snapshot for system prompt injection.
        Returns (memory_text, user_text).
        """
        memory_entries = self.read_entries()
        user_entries = self.read_user_entries()

        # Truncate by character count (model-independent)
        memory_lines = ["# Memory\n"]
        for entry in memory_entries:
            text = entry.to_text()
            if len("\n".join(memory_lines) + text) > MAX_MEMORY_CHARS:
                break
            memory_lines.append(text + ENTRY_DELIMITER)

        user_lines = ["# User Context\n"]
        for entry in user_entries:
            text = entry.to_text()
            if len("\n".join(user_lines) + text) > MAX_USER_CHARS:
                break
            user_lines.append(text + ENTRY_DELIMITER)

        return "\n".join(memory_lines), "\n".join(user_lines)

    # ---------------------------------------------------------------------------
    # Write
    # ---------------------------------------------------------------------------

    def add_entry(
        self,
        title: str,
        content: str,
        tags: Optional[list[str]] = None,
        memory_type: str = "memory",
    ) -> MemoryEntry:
        """Add a new entry (thread-safe)."""
        path = self.user_path if memory_type == "user" else self.memory_path
        entry = MemoryEntry(title=title, content=content, tags=tags or [])

        fd = self._lock()
        try:
            existing = self.read_entries() if path == self.memory_path else self.read_user_entries()
            existing.append(entry)
            self._atomic_write(path, self._entries_to_text(existing))
        finally:
            self._unlock(fd)

        return entry

    def replace_entry(
        self,
        title: str,
        new_content: str,
        memory_type: str = "memory",
    ) -> Optional[MemoryEntry]:
        """Replace entry by title (thread-safe)."""
        path = self.user_path if memory_type == "user" else self.memory_path
        fd = self._lock()
        try:
            entries = self.read_entries() if path == self.memory_path else self.read_user_entries()
            for i, entry in enumerate(entries):
                if entry.title == title:
                    entry.content = new_content
                    entry.updated_at = datetime.now(timezone.utc).isoformat()
                    self._atomic_write(path, self._entries_to_text(entries))
                    return entry
        finally:
            self._unlock(fd)
        return None

    def remove_entry(self, title: str, memory_type: str = "memory") -> bool:
        """Remove entry by title (thread-safe)."""
        path = self.user_path if memory_type == "user" else self.memory_path
        fd = self._lock()
        try:
            entries = self.read_entries() if path == self.memory_path else self.read_user_entries()
            before = len(entries)
            entries = [e for e in entries if e.title != title]
            if len(entries) < before:
                self._atomic_write(path, self._entries_to_text(entries))
                return True
        finally:
            self._unlock(fd)
        return False

    def _entries_to_text(self, entries: list[MemoryEntry]) -> str:
        """Serialize entries to text format."""
        parts = [e.to_text() for e in entries]
        return ENTRY_DELIMITER.join(parts)

    # ---------------------------------------------------------------------------
    # Snapshot management
    # ---------------------------------------------------------------------------

    def refresh_snapshot(self) -> None:
        """Regenerate frozen snapshot from current entries."""
        memory_text, user_text = self.get_snapshot()
        snapshot_text = f"{memory_text}\n\n{user_text}\n"
        self._atomic_write(self.snapshot_path, snapshot_text)

    def get_injection_prompt(self) -> str:
        """Get the full injection prompt for system prompt."""
        if self.snapshot_path.exists():
            return self.snapshot_path.read_text(encoding="utf-8")
        self.refresh_snapshot()
        return self.snapshot_path.read_text(encoding="utf-8")

    # ---------------------------------------------------------------------------
    # Stats
    # ---------------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return memory store statistics."""
        memory_entries = self.read_entries()
        user_entries = self.read_user_entries()

        return {
            "memory_entries": len(memory_entries),
            "user_entries": len(user_entries),
            "memory_chars": sum(len(e.content) for e in memory_entries),
            "user_chars": sum(len(e.content) for e in user_entries),
            "snapshot_exists": self.snapshot_path.exists(),
            "last_updated": str(self.memory_path.stat().st_mtime) if self.memory_path.exists() else None,
        }
