#!/usr/bin/env python3
"""
CP4 Self-Healing Loop
=====================
When CP3 benchmark score < 60, automatically retry with failure context injected.

Retry strategy:
  1. Analyze failure → extract root cause from benchmark feedback
  2. Build retry prompt with failure context + explicit guidance
  3. Re-run CP2 with enriched prompt
  4. Re-run CP3; if still < 60 after 2 retries, give up

Max retries: 2 (configurable via HARNESS_MAX_RETRIES env var)
"""

import os
import subprocess
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MAX_RETRIES = int(os.environ.get("HARNESS_MAX_RETRIES", "2"))
RETRY_THRESHOLD = 60.0  # score below this triggers retry

# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

@dataclass
class RetryContext:
    """Context carried across retry attempts."""
    original_task: str
    attempt: int  # 1-based
    prev_score: float
    prev_grade: str
    failure_analysis: str
    retry_prompt: str


@dataclass
class SelfHealingResult:
    ok: bool
    attempt: int
    score: float
    grade: str
    was_retried: bool
    retry_ctx: Optional[RetryContext]
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Failure Analysis
# ---------------------------------------------------------------------------

def _run_benchmark_for_analysis(project_path: Path) -> Dict:
    """Run benchmark in text mode to get readable failure diagnostics."""
    try:
        result = subprocess.run(
            ["python3", "-m", "tools.benchmark.runner", "--project", str(project_path), "--output", "text"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "returncode": -1}


def analyze_failure(score: float, grade: str, project_path: Path,
                    benchmark_output: str = "") -> str:
    """
    Analyze why benchmark score is low and return a human-readable failure summary.
    Returns a short failure analysis string.
    """
    # Common failure patterns keyed by grade
    grade_hints = {
        "F": "Severe failure — agent produced broken code or wrong results",
        "D": "Poor quality — significant issues in completion or correctness",
        "C": "Below standard — partial completion or moderate quality gaps",
        "B": "Near passing — minor issues in efficiency or quality",
    }

    base = grade_hints.get(grade, f"Benchmark score {score}/100 ({grade})")

    # Try to extract component scores if available
    if benchmark_output:
        lines = benchmark_output.split("\n")
        low_components = []
        for line in lines:
            # Look for lines like "Quality: 42" or "Efficiency: 38"
            for prefix in ["Efficiency", "Quality", "Behavior", "Autonomy"]:
                if line.startswith(prefix) and ":" in line:
                    try:
                        val = float(line.split(":")[-1].strip().split("/")[0])
                        if val < 60:
                            low_components.append(f"{prefix}={val}")
                    except Exception:
                        pass
        if low_components:
            base += f" (weak areas: {', '.join(low_components)})"

    return base


def build_retry_prompt(original_task: str, retry_ctx: RetryContext,
                        project_path: Path) -> str:
    """
    Build an enriched prompt for the next retry attempt.
    Injects:
    - Original task
    - Failure analysis
    - What NOT to repeat (from previous attempts)
    - Explicit guidance for improvement
    """
    lines = [
        f"[RETRY ATTEMPT {retry_ctx.attempt + 1}/3 — Previous attempt failed]",
        "",
        f"ORIGINAL TASK: {original_task}",
        "",
        f"PREVIOUS RESULT: Score={retry_ctx.prev_score:.1f}/100, Grade={retry_ctx.prev_grade}",
        "",
        f"FAILURE ANALYSIS: {retry_ctx.failure_analysis}",
        "",
        "IMPORTANT GUIDANCE:",
        "- Do NOT repeat the same approach that produced the low score",
        "- Review what went wrong and take a different strategy",
        "- Pay special attention to the weak areas identified above",
    ]

    # Add project-specific hints if available
    readme = project_path / "README.md"
    if readme.exists():
        lines.append("- Check the project README for architecture/approach guidance")

    package_json = project_path / "package.json"
    if package_json.exists():
        lines.append("- Check package.json for available scripts (build/lint/test)")

    lines.append("")
    lines.append(f"TASK (same as before): {original_task}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Self-Healing Loop
# ---------------------------------------------------------------------------

def run_cp4(
    original_task: str,
    score: float,
    grade: str,
    project_path: Path,
    benchmark_output: str = "",
) -> SelfHealingResult:
    """
    Run CP4 self-healing: retry if score < threshold.

    Returns SelfHealingResult with:
      - ok: True if final score >= 60
      - was_retried: True if any retry was performed
      - attempt: final attempt number (1-3)
      - score/grade: final results
    """
    if score >= RETRY_THRESHOLD:
        return SelfHealingResult(
            ok=True,
            attempt=1,
            score=score,
            grade=grade,
            was_retried=False,
            retry_ctx=None,
        )

    # ── First retry (attempt 2 total) ─────────────────────────────────
    attempt = 2
    failure_analysis = analyze_failure(score, grade, project_path, benchmark_output)

    retry_ctx = RetryContext(
        original_task=original_task,
        attempt=attempt,
        prev_score=score,
        prev_grade=grade,
        failure_analysis=failure_analysis,
        retry_prompt="",  # filled below
    )

    retry_prompt = build_retry_prompt(original_task, retry_ctx, project_path)
    retry_ctx = RetryContext(
        original_task=original_task,
        attempt=attempt,
        prev_score=score,
        prev_grade=grade,
        failure_analysis=failure_analysis,
        retry_prompt=retry_prompt,
    )

    # Re-run agent (CP2 again with enriched prompt)
    from tools.execution import run_openclaw_agent

    response = run_openclaw_agent(
        prompt=retry_prompt,
        cwd=str(project_path),
        timeout=120,
    )

    # Re-run CP3 benchmark
    from tools.benchmark.runner import run_benchmark

    result = run_benchmark(str(project_path), output="json")
    new_score = result.score
    new_grade = result.grade

    if new_score >= RETRY_THRESHOLD:
        return SelfHealingResult(
            ok=True,
            attempt=attempt,
            score=new_score,
            grade=new_grade,
            was_retried=True,
            retry_ctx=retry_ctx,
        )

    # ── Second retry (attempt 3 total) ─────────────────────────────
    if attempt < MAX_RETRIES:
        attempt = 3
        new_failure_analysis = analyze_failure(new_score, new_grade, project_path,
                                              benchmark_output="")
        retry_ctx2 = RetryContext(
            original_task=original_task,
            attempt=attempt,
            prev_score=new_score,
            prev_grade=new_grade,
            failure_analysis=new_failure_analysis,
            retry_prompt="",
        )
        retry_prompt2 = build_retry_prompt(original_task, retry_ctx2, project_path)
        retry_ctx2.retry_prompt = retry_prompt2

        response2 = run_openclaw_agent(
            prompt=retry_prompt2,
            cwd=str(project_path),
            timeout=120,
        )

        result2 = run_benchmark(str(project_path), output="json")
        final_score = result2.score
        final_grade = result2.grade

        return SelfHealingResult(
            ok=final_score >= RETRY_THRESHOLD,
            attempt=attempt,
            score=final_score,
            grade=final_grade,
            was_retried=True,
            retry_ctx=retry_ctx2,
        )

    # Exhausted retries
    return SelfHealingResult(
        ok=False,
        attempt=attempt,
        score=new_score,
        grade=new_grade,
        was_retried=True,
        retry_ctx=retry_ctx,
        error=f"Exhausted {MAX_RETRIES} retries, final score={new_score}",
    )


# ---------------------------------------------------------------------------
# CLI (for testing)
# ---------------------------------------------------------------------------

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CP4 Self-Healing CLI")
    parser.add_argument("--task", "-t", required=True, help="Original task")
    parser.add_argument("--score", type=float, required=True, help="Previous benchmark score")
    parser.add_argument("--grade", required=True, help="Previous benchmark grade")
    parser.add_argument("--project", "-p", default=".", help="Project path")
    args = parser.parse_args()

    project_path = Path(args.project).expanduser().resolve()

    result = run_cp4(
        original_task=args.task,
        score=args.score,
        grade=args.grade,
        project_path=project_path,
    )

    print(f"CP4 Self-Healing Result:")
    print(f"  ok:        {result.ok}")
    print(f"  attempt:   {result.attempt}")
    print(f"  score:     {result.score:.1f}")
    print(f"  grade:     {result.grade}")
    print(f"  was_retried: {result.was_retried}")
    if result.error:
        print(f"  error:     {result.error}")


if __name__ == "__main__":
    main()