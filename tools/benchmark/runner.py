#!/usr/bin/env python3
"""Harness Benchmark Runner"""
import json, sys
from pathlib import Path

DEFAULT_STATE = "harness/feedback/state/state.json"

def run_benchmark(project_path="."):
    state_file = Path(project_path) / DEFAULT_STATE
    if not state_file.exists():
        print("[ERROR] State not found")
        return {"score": 0, "grade": "F"}
    
    with open(state_file) as f:
        state = json.load(f)
    
    checkpoints = state.get("checkpoints", {})
    completed = sum(1 for v in checkpoints.values() if v == "completed")
    total = len(checkpoints) or 1
    score = (completed / total) * 100
    
    grade = "A" if score >= 80 else "B" if score >= 70 else "C" if score >= 60 else "D" if score >= 50 else "F"
    
    print(f"Score: {score:.1f}/100 ({grade})")
    return {"score": score, "grade": grade, "completed": completed, "total": total}

if __name__ == "__main__":
    project = sys.argv[1] if len(sys.argv) > 1 else "."
    run_benchmark(project)
