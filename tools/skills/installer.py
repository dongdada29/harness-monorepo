#!/usr/bin/env python3
"""
SkillInstaller — Quarantine → Scan → Install workflow.

Based on Hermes Agent skills_hub.py quarantine design.
"""

import hashlib
import logging
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .source import SkillSource, SkillMeta, SkillBundle, HubLockFile, AuditLog, QUARANTINE_DIR, HUB_DIR

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Scan result
# ---------------------------------------------------------------------------

@dataclass
class ScanResult:
    """Result of scanning a skill bundle in quarantine."""
    ok: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    content_hash: str = ""


# ---------------------------------------------------------------------------
# SkillInstaller
# ---------------------------------------------------------------------------

class SkillInstaller:
    """
    Installs skills via quarantine → scan → install workflow.

    1. QUARANTINE: Download to quarantine dir
    2. SCAN: Static analysis for unsafe patterns
    3. INSTALL: Copy to skills dir and update lock file
    """

    DANGEROUS_PATTERNS = [
        (re.compile(r'eval\s*\('), "eval() detected — potential code injection"),
        (re.compile(r'exec\s*\('), "exec() detected — potential code injection"),
        (re.compile(r'__import__\s*\('), "__import__() detected — dynamic import"),
        (re.compile(r'subprocess\s*\.\s*call\s*\('), "subprocess.call() detected — shell execution"),
        (re.compile(r'subprocess\s*\.\s*run\s*\([^)]*shell\s*=\s*True'), "subprocess with shell=True detected"),
        (re.compile(r'os\s*\.\s*system\s*\('), "os.system() detected — shell execution"),
        (re.compile(r'chmod\s*0o[0-7]{3,4}'), "chmod with permissive permissions"),
        (re.compile(r'wget|curl.*\|.*sh'), "piping download to shell (curl | sh)"),
        (re.compile(r'rm\s+-rf\s+/(?:\s|--)', re.I), "rm -rf / detected"),
        (re.compile(r'base64.*decode'), "base64 decode — possible payload"),
        (re.compile(r'os\s*\.\s*getcwd\s*\(\).*[^\x00-\x7F]'), "non-ASCII in path construction"),
    ]

    SUSPICIOUS_EXTENSIONS = {".exe", ".bat", ".cmd", ".ps1", ".sh", ".bash"}

    def __init__(self, source: Optional[SkillSource] = None):
        self.source = source
        self.lock = HubLockFile()
        self.audit = AuditLog()
        HUB_DIR.mkdir(parents=True, exist_ok=True)
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------------------------
    # Install flow
    # ---------------------------------------------------------------------------

    def install(self, meta: SkillMeta) -> tuple[bool, str]:
        """
        Full install: fetch → quarantine → scan → install.
        Returns (success, message).
        """
        if not self.source:
            return False, "No source configured"

        try:
            bundle = self.source.fetch(meta.identifier)
        except Exception as e:
            self.audit.append("fetch", meta.name, meta.identifier, meta.trust_level, "fail", str(e))
            return False, f"Fetch failed: {e}"

        # Move to quarantine
        q_dir = QUARANTINE_DIR / meta.name
        if q_dir.exists():
            shutil.rmtree(q_dir)

        try:
            self._write_bundle_to_disk(bundle, q_dir)
        except Exception as e:
            self.audit.append("quarantine", meta.name, meta.identifier, meta.trust_level, "fail", str(e))
            return False, f"Quarantine failed: {e}"

        # Scan
        scan_result = self.scan(q_dir, bundle)
        content_hash = self._compute_hash(bundle)

        if not scan_result.ok:
            shutil.rmtree(q_dir)
            errors = "; ".join(scan_result.errors)
            self.audit.append("scan", meta.name, meta.identifier, meta.trust_level, "fail", errors)
            return False, f"Scan failed: {errors}"

        # Install
        try:
            install_path = meta.install_path()
            if install_path.exists():
                shutil.rmtree(install_path)

            # Copy from quarantine to installed
            shutil.copytree(q_dir, install_path)
            shutil.rmtree(q_dir)

            # Update lock
            self.lock.add(meta)

            # Write metadata
            meta_path = install_path / ".skill-meta.json"
            meta_path.write_text(self._meta_to_json(meta, content_hash), encoding="utf-8")

            self.audit.append("install", meta.name, meta.identifier, meta.trust_level, "ok", f"hash={content_hash}")

            return True, f"Installed to {install_path}"

        except Exception as e:
            self.audit.append("install", meta.name, meta.identifier, meta.trust_level, "fail", str(e))
            return False, f"Install failed: {e}"

    def uninstall(self, name: str) -> tuple[bool, str]:
        """Uninstall a skill by name."""
        # Find the skill
        for meta in self.lock.list_all():
            if meta.name == name:
                path = meta.install_path()
                if path.exists():
                    shutil.rmtree(path)
                self.lock.remove(name)
                self.audit.append("uninstall", name, meta.identifier, meta.trust_level, "ok", "")
                return True, f"Uninstalled {name}"
        return False, f"Skill not found: {name}"

    def list_installed(self) -> list[SkillMeta]:
        """List all installed skills from lock file."""
        return self.lock.list_all()

    # ---------------------------------------------------------------------------
    # Scanning
    # ---------------------------------------------------------------------------

    def scan(self, q_dir: Path, bundle: Optional[SkillBundle] = None) -> ScanResult:
        """
        Static analysis scan for dangerous patterns.
        Returns ScanResult with ok=True if clean.
        """
        errors: list[str] = []
        warnings: list[str] = []

        # Scan all text files
        for root, _, files in os.walk(q_dir):
            for filename in files:
                filepath = Path(root) / filename
                rel = filepath.relative_to(q_dir)

                # Check extension
                if filepath.suffix.lower() in self.SUSPICIOUS_EXTENSIONS:
                    warnings.append(f"Suspicious extension: {rel}")

                # Scan content
                try:
                    content = filepath.read_text(encoding="utf-8", errors="ignore")
                    for pattern, msg in self.DANGEROUS_PATTERNS:
                        if pattern.search(content):
                            errors.append(f"{rel}: {msg}")
                except Exception:
                    pass  # binary file, skip

        # Validate bundle paths
        if bundle:
            bundle_ok, bundle_errors = bundle.validate()
            if not bundle_ok:
                errors.extend(bundle_errors)

        return ScanResult(
            ok=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            content_hash=self._compute_hash(bundle) if bundle else "",
        )

    # ---------------------------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------------------------

    def _write_bundle_to_disk(self, bundle: SkillBundle, dest: Path) -> None:
        dest.mkdir(parents=True, exist_ok=True)
        for rel_path, content in bundle.files.items():
            file_path = dest / rel_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, str):
                file_path.write_text(content, encoding="utf-8")
            else:
                file_path.write_bytes(content)

    def _compute_hash(self, bundle: Optional[SkillBundle]) -> str:
        if not bundle:
            return ""
        hasher = hashlib.sha256()
        for path_str in sorted(bundle.files.keys()):
            hasher.update(path_str.encode())
            hasher.update(bundle.files[path_str].encode() if isinstance(bundle.files[path_str], str) else bundle.files[path_str])
        return hasher.hexdigest()[:16]

    def _meta_to_json(self, meta: SkillMeta, content_hash: str) -> str:
        import json
        data = {
            "name": meta.name,
            "identifier": meta.identifier,
            "source": meta.source,
            "trust_level": meta.trust_level,
            "installed_at": datetime.now(timezone.utc).isoformat(),
            "content_hash": content_hash,
        }
        return json.dumps(data, indent=2)
