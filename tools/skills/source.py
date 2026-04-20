#!/usr/bin/env python3
"""
SkillSource — Multi-source adapter framework for harness skills.

Supports:
  - LocalSource: templates/basic, templates/advanced, templates/sandbox-tasks
  - GitHubSource: GitHub repos via Contents API (clawhub.ai, VoltAgent/awesome-agent-skills, etc.)
  - OptionalSource: Built-in optional skills

Based on Hermes Agent skills_hub.py design.
"""

import hashlib
import json
import logging
import os
import shutil
import tempfile
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Optional
from urllib.parse import urlparse

import yaml

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".harness"))
SKILLS_DIR = HERMES_HOME / "skills"
HUB_DIR = SKILLS_DIR / ".hub"
LOCK_FILE = HUB_DIR / "lock.json"
QUARANTINE_DIR = HUB_DIR / "quarantine"
AUDIT_LOG = HUB_DIR / "audit.log"

# ---------------------------------------------------------------------------
# Trust levels
# ---------------------------------------------------------------------------

TRUST_BUILTIN = "builtin"
TRUST_TRUSTED = "trusted"
TRUST_COMMUNITY = "community"

TRUST_ORDER = [TRUST_BUILTIN, TRUST_TRUSTED, TRUST_COMMUNITY]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SkillMeta:
    """Minimal metadata for a skill."""
    name: str
    description: str
    source: str  # "local", "github", "optional"
    identifier: str  # source-specific ID
    trust_level: str = TRUST_COMMUNITY
    repo: Optional[str] = None
    path: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def install_path(self) -> Path:
        """Where this skill would be installed."""
        return SKILLS_DIR / self.source / self.name

    def lock_entry(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "identifier": self.identifier,
            "source": self.source,
            "trust_level": self.trust_level,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "repo": self.repo,
            "path": self.path,
        }


@dataclass
class SkillBundle:
    """A downloaded skill ready for quarantine/scanning/installation."""
    name: str
    files: dict[str, str]  # relative_path -> file content
    source: str
    identifier: str
    trust_level: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> tuple[bool, list[str]]:
        """Basic validation. Returns (ok, errors)."""
        errors = []
        if not self.name:
            errors.append("Missing name")
        if not self.files:
            errors.append("No files")
        # Check for path traversal
        for path_str in self.files:
            path = PurePosixPath(path_str)
            if ".." in path.parts:
                errors.append(f"Path traversal attempt: {path_str}")
        return len(errors) == 0, errors


# ---------------------------------------------------------------------------
# Lock file
# ---------------------------------------------------------------------------

class HubLockFile:
    """Tracks installed skills and their provenance."""

    def __init__(self, lock_path: Optional[Path] = None):
        self.lock_path = lock_path or LOCK_FILE
        HUB_DIR.mkdir(parents=True, exist_ok=True)

    def read(self) -> dict[str, dict[str, Any]]:
        if self.lock_path.exists():
            return json.loads(self.lock_path.read_text())
        return {}

    def write(self, data: dict[str, dict[str, Any]]) -> None:
        self.lock_path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

    def add(self, meta: SkillMeta) -> None:
        data = self.read()
        data[meta.name] = meta.lock_entry()
        self.write(data)

    def remove(self, name: str) -> bool:
        data = self.read()
        if name in data:
            del data[name]
            self.write(data)
            return True
        return False

    def get(self, name: str) -> Optional[dict[str, Any]]:
        return self.read().get(name)

    def list_all(self) -> list[SkillMeta]:
        result = []
        for name, entry in self.read().items():
            result.append(SkillMeta(
                name=name,
                identifier=entry.get("identifier", ""),
                source=entry.get("source", "unknown"),
                trust_level=entry.get("trust_level", TRUST_COMMUNITY),
                description="",  # not stored in lock
            ))
        return result


# ---------------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------------

class AuditLog:
    """Append-only audit log of all skill operations."""

    def __init__(self, log_path: Optional[Path] = None):
        self.log_path = log_path or AUDIT_LOG
        HUB_DIR.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.write_text("")

    def append(self, action: str, name: str, identifier: str, trust_level: str, result: str, detail: str = "") -> None:
        entry = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "name": name,
            "identifier": identifier,
            "trust_level": trust_level,
            "result": result,
            "detail": detail,
        }
        with open(self.log_path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# SkillSource ABC
# ---------------------------------------------------------------------------

class SkillSource(ABC):
    """Abstract base class for skill registries."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SkillMeta]:
        """Search for skills matching query."""
        ...

    @abstractmethod
    def fetch(self, identifier: str) -> SkillBundle:
        """Fetch a skill bundle by identifier."""
        ...

    def trust_level_for(self, identifier: str) -> str:
        """Determine trust level for a given identifier."""
        return TRUST_COMMUNITY

    def install(self, meta: SkillMeta, bundle: SkillBundle) -> Path:
        """Install bundle to skills dir. Returns installed path."""
        dest = meta.install_path()
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        for rel_path, content in bundle.files.items():
            file_path = dest / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        return dest


# ---------------------------------------------------------------------------
# LocalSource
# ---------------------------------------------------------------------------

class LocalSource(SkillSource):
    """
    Local template directory source.
    Supports: templates/basic, templates/advanced, templates/sandbox-tasks
    """

    TEMPLATE_DIR = Path(__file__).parent.parent.parent / "templates"

    def __init__(self):
        super().__init__("local")

    def search(self, query: str, limit: int = 10) -> list[SkillMeta]:
        results = []
        query_lower = query.lower()
        for template_dir in self.TEMPLATE_DIR.iterdir():
            if not template_dir.is_dir():
                continue
            if query_lower in template_dir.name.lower():
                meta = self._meta_from_dir(template_dir)
                results.append(meta)
                if len(results) >= limit:
                    break
        return results

    def fetch(self, identifier: str) -> SkillBundle:
        template_dir = self.TEMPLATE_DIR / identifier
        if not template_dir.exists():
            raise FileNotFoundError(f"Template not found: {identifier}")

        files: dict[str, str] = {}
        for root, _, filenames in os.walk(template_dir):
            for filename in filenames:
                filepath = Path(root) / filename
                rel = filepath.relative_to(template_dir)
                try:
                    files[str(rel)] = filepath.read_text(encoding="utf-8")
                except Exception:
                    pass  # binary or unreadable, skip

        return SkillBundle(
            name=identifier,
            files=files,
            source="local",
            identifier=identifier,
            trust_level=TRUST_BUILTIN,
        )

    def _meta_from_dir(self, dir_path: Path) -> SkillMeta:
        readme = dir_path / "README.md"
        description = ""
        if readme.exists():
            lines = readme.read_text().split("\n")
            for line in lines:
                if line.startswith(">"):
                    description = line.strip("> ").strip()
                    break

        return SkillMeta(
            name=dir_path.name,
            description=description,
            source="local",
            identifier=dir_path.name,
            trust_level=TRUST_BUILTIN,
        )

    def list_all(self) -> list[SkillMeta]:
        results = []
        for template_dir in self.TEMPLATE_DIR.iterdir():
            if template_dir.is_dir():
                results.append(self._meta_from_dir(template_dir))
        return results


# ---------------------------------------------------------------------------
# GitHubSource
# ---------------------------------------------------------------------------

class GitHubSource(SkillSource):
    """
    GitHub repository source via Contents API.

    Supported repos:
      - clawhubai/awesome-agent-skills
      - VoltAgent/awesome-agent-skills
      - openai/skill-manifests
      - anthropics/skills
    """

    DEFAULT_REPOS = [
        "clawhubai/awesome-agent-skills",
        "VoltAgent/awesome-agent-skills",
    ]

    def __init__(self, repos: Optional[list[str]] = None):
        super().__init__("github")
        self.repos = repos or self.DEFAULT_REPOS
        self._repo_cache: dict[str, dict] = {}
        self._repo_tree_cache: dict[str, float] = {}

    def search(self, query: str, limit: int = 10) -> list[SkillMeta]:
        results = []
        query_lower = query.lower()

        for repo in self.repos:
            tree = self._get_repo_tree(repo)
            for item in tree:
                name = item.get("path", "")
                if not name.endswith(".md") and not name.endswith(".yaml"):
                    continue
                if query_lower in name.lower():
                    skill_name = name.split("/")[0] if "/" in name else name
                    meta = SkillMeta(
                        name=skill_name,
                        description=f"From {repo}/{name}",
                        source="github",
                        identifier=f"{repo}/{name}",
                        trust_level=self.trust_level_for(repo),
                        repo=repo,
                        path=name,
                    )
                    results.append(meta)
                    if len(results) >= limit:
                        break
            if len(results) >= limit:
                break

        return results

    def fetch(self, identifier: str) -> SkillBundle:
        # identifier format: "owner/repo/path" or "owner/repo"
        parts = identifier.split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid GitHub identifier: {identifier}")

        owner, repo = parts[0], parts[1]
        path = "/".join(parts[2:]) if len(parts) > 2 else "SKILL.md"

        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        resp = self._http_get(api_url)

        if isinstance(resp, list):
            # It's a directory — fetch SKILL.md or README.md
            for item in resp:
                if item["name"] in ("SKILL.md", "README.md", "skill.yaml"):
                    return self._fetch_file(owner, repo, item["path"])
            raise FileNotFoundError(f"No skill file found in {identifier}")
        else:
            # It's a file
            return self._fetch_file(owner, repo, path)

    def _fetch_file(self, owner: str, repo: str, path: str) -> SkillBundle:
        api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        resp = self._http_get(api_url)

        if resp.get("encoding") == "base64":
            import base64
            content = base64.b64decode(resp["content"]).decode("utf-8")
        else:
            raise ValueError(f"Unsupported encoding: {resp.get('encoding')}")

        # Fetch sibling files if it's a directory index
        files: dict[str, str] = {path: content}
        dir_path = str(Path(path).parent)

        # Try to fetch the full directory tree for this skill
        try:
            tree = self._get_repo_tree(f"{owner}/{repo}")
            skill_prefix = dir_path if dir_path != "." else Path(path).stem
            for item in tree:
                item_path = item.get("path", "")
                if item_path.startswith(skill_prefix) and item["type"] == "blob":
                    file_rel = item_path[len(skill_prefix):].lstrip("/")
                    if file_rel and file_rel != "SKILL.md":
                        file_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{item_path}"
                        file_resp = self._http_get(file_url)
                        if file_resp.get("encoding") == "base64":
                            import base64
                            files[item_path] = base64.b64decode(file_resp["content"]).decode("utf-8")
        except Exception:
            pass

        skill_name = Path(path).stem
        return SkillBundle(
            name=skill_name,
            files=files,
            source="github",
            identifier=f"{owner}/{repo}/{path}",
            trust_level=self.trust_level_for(f"{owner}/{repo}"),
        )

    def _get_repo_tree(self, repo: str) -> list[dict]:
        """Fetch repository file tree with caching."""
        import time
        now = time.time()
        if repo in self._repo_tree_cache and now - self._repo_tree_cache[repo] < 3600:
            return self._repo_cache.get(repo, [])

        api_url = f"https://api.github.com/repos/{repo}/git/trees/HEAD?recursive=1"
        resp = self._http_get(api_url)
        tree = resp.get("tree", [])
        self._repo_cache[repo] = tree
        self._repo_tree_cache[repo] = now
        return tree

    def _http_get(self, url: str) -> dict:
        import urllib.request
        import urllib.error

        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.v3+json"})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise FileNotFoundError(f"GitHub resource not found: {url}")
            raise

    def trust_level_for(self, identifier: str) -> str:
        trusted = ["clawhubai/awesome-agent-skills", "openai/skills", "anthropics/skills"]
        if identifier in trusted:
            return TRUST_TRUSTED
        return TRUST_COMMUNITY


# ---------------------------------------------------------------------------
# OptionalSource
# ---------------------------------------------------------------------------

class OptionalSource(SkillSource):
    """
    Built-in optional skills — shipped with harness but not activated.
    Lives in templates/sandbox-tasks/ as reusable task templates.
    """

    OPTIONAL_DIR = Path(__file__).parent.parent.parent / "core" / "harness" / "base" / "tasks"

    def __init__(self):
        super().__init__("optional")

    def search(self, query: str, limit: int = 10) -> list[SkillMeta]:
        results = []
        if not self.OPTIONAL_DIR.exists():
            return results

        query_lower = query.lower()
        for f in self.OPTIONAL_DIR.iterdir():
            if f.is_file() and f.suffix == ".md":
                if query_lower in f.stem.lower():
                    content = f.read_text()
                    description = content.split("\n")[0].strip("# ").strip()
                    results.append(SkillMeta(
                        name=f.stem,
                        description=description or f.stem,
                        source="optional",
                        identifier=f.stem,
                        trust_level=TRUST_BUILTIN,
                    ))
                    if len(results) >= limit:
                        break
        return results

    def fetch(self, identifier: str) -> SkillBundle:
        task_file = self.OPTIONAL_DIR / f"{identifier}.md"
        if not task_file.exists():
            raise FileNotFoundError(f"Optional skill not found: {identifier}")

        content = task_file.read_text()
        return SkillBundle(
            name=identifier,
            files={f"{identifier}.md": content},
            source="optional",
            identifier=identifier,
            trust_level=TRUST_BUILTIN,
        )

    def list_all(self) -> list[SkillMeta]:
        results = []
        if self.OPTIONAL_DIR.exists():
            for f in self.OPTIONAL_DIR.iterdir():
                if f.is_file() and f.suffix == ".md":
                    content = f.read_text()
                    description = content.split("\n")[0].strip("# ").strip()
                    results.append(SkillMeta(
                        name=f.stem,
                        description=description or f.stem,
                        source="optional",
                        identifier=f.stem,
                        trust_level=TRUST_BUILTIN,
                    ))
        return results
