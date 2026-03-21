#!/usr/bin/env python3
"""
Harness Benchmark - Effectiveness Score
====================================
Measures ACTUAL harness effectiveness, not just structure.

Usage: python3 benchmark.py --project /path/to/project
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class Metric:
    name: str
    value: float
    weight: float
    direction: str  # "higher" or "lower" is better


class HarnessBenchmark:
    """Measure harness effectiveness based on outcomes."""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.metrics: List[Metric] = []
        self.total_weight = 0
        
    def add(self, name: str, value: float, weight: float, direction: str = "higher"):
        self.metrics.append(Metric(name, value, weight, direction))
        self.total_weight += weight
        
    def score(self) -> float:
        if not self.metrics:
            return 0
        weighted = 0
        for m in self.metrics:
            if m.direction == "higher":
                normalized = min(100, max(0, m.value))
            else:
                normalized = min(100, max(0, 100 - m.value))
            weighted += normalized * m.weight
        return weighted / self.total_weight if self.total_weight > 0 else 0
    
    def grade(self, score: float) -> tuple:
        if score >= 90: return "A", "Excellent"
        if score >= 80: return "B", "Good"
        if score >= 70: return "C", "Fair"
        if score >= 60: return "D", "Needs Improvement"
        return "F", "Poor"
    
    # ====================
    # Efficiency Metrics
    # ====================
    def measure_efficiency(self) -> Dict:
        print("1. EFFICIENCY (40%)")
        print("-" * 40)
        
        state_file = os.path.join(self.project_path, "harness/feedback/state/state.json")
        history_dir = os.path.join(self.project_path, "harness/feedback/history")
        
        # Task Completion Rate
        completed = 0
        blocked = 0
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            completed = state.get("metrics", {}).get("tasksCompleted", 0)
            blocked = state.get("metrics", {}).get("tasksBlocked", 0)
        
        total = completed + blocked
        completion_rate = (completed / total * 100) if total > 0 else 100
        block_rate = (blocked / total * 100) if total > 0 else 0
        
        print(f"   Tasks Completed: {completed}")
        print(f"   Tasks Blocked: {blocked}")
        print(f"   Completion Rate: {completion_rate:.0f}%")
        
        self.add("Task Completion", completion_rate, 20, "higher")
        
        # Gate Pass Rate
        if os.path.exists(state_file):
            gates = state.get("gates", {})
            passed = sum(1 for v in gates.values() if v == "passed")
            total_gates = len(gates) or 4
            gate_rate = (passed / total_gates * 100)
        else:
            gate_rate = 100
            
        print(f"   Gate Pass Rate: {gate_rate:.0f}%")
        self.add("Gate Pass Rate", gate_rate, 10, "higher")
        
        # Block Rate (lower is better)
        print(f"   Block Rate: {block_rate:.0f}%")
        self.add("Block Rate", block_rate, 10, "lower")
        
        return {
            "completed": completed,
            "blocked": blocked,
            "completion_rate": completion_rate,
            "gate_rate": gate_rate,
            "block_rate": block_rate
        }
    
    # ====================
    # Quality Metrics
    # ====================
    def measure_quality(self) -> Dict:
        print()
        print("2. QUALITY (30%)")
        print("-" * 40)
        
        src_dirs = ["src", "app", "lib"]
        src_dir = None
        for d in src_dirs:
            path = os.path.join(self.project_path, d)
            if os.path.exists(path):
                src_dir = path
                break
        
        if not src_dir:
            src_dir = self.project_path
            
        # Count issues
        console_logs = 0
        debuggers = 0
        todos = 0
        
        try:
            r = subprocess.run(
                ["grep", "-r", "-l", "console.log", src_dir, 
                 "--include=*.ts", "--include=*.tsx", "--include=*.js"],
                capture_output=True, text=True, timeout=10
            )
            console_logs = len([l for l in r.stdout.strip().split("\n") if l])
        except:
            pass
            
        try:
            r = subprocess.run(
                ["grep", "-r", "-l", "debugger", src_dir,
                 "--include=*.ts", "--include=*.tsx", "--include=*.js"],
                capture_output=True, text=True, timeout=10
            )
            debuggers = len([l for l in r.stdout.strip().split("\n") if l])
        except:
            pass
        
        # Quality score: penalize each issue
        quality_score = max(0, 100 - (console_logs * 5) - (debuggers * 10))
        
        print(f"   console.log count: {console_logs}")
        print(f"   debugger count: {debuggers}")
        print(f"   Quality Score: {quality_score:.0f}")
        
        self.add("Code Quality", quality_score, 30, "higher")
        
        return {
            "console_logs": console_logs,
            "debuggers": debuggers,
            "quality_score": quality_score
        }
    
    # ====================
    # Behavior Metrics
    # ====================
    def measure_behavior(self) -> Dict:
        print()
        print("3. BEHAVIOR (15%)")
        print("-" * 40)
        
        state_file = os.path.join(self.project_path, "harness/feedback/state/state.json")
        
        state_updates = 0
        recent_changes = 0
        
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            recent_changes = len(state.get("recentChanges", []))
            
            # Check if state was updated recently
            last_updated = state.get("lastUpdated", "")
            if last_updated:
                state_updates = 100  # Assume updated if exists
            else:
                state_updates = 0
        else:
            state_updates = 50  # Neutral if no state
        
        print(f"   State Updates: {state_updates:.0f}")
        print(f"   Recent Changes: {recent_changes}")
        
        self.add("State Management", state_updates, 10, "higher")
        self.add("Change Tracking", min(100, recent_changes * 20), 5, "higher")
        
        return {
            "state_updates": state_updates,
            "recent_changes": recent_changes
        }
    
    # ====================
    # Autonomy Metrics
    # ====================
    def measure_autonomy(self) -> Dict:
        print()
        print("4. AUTONOMY (15%)")
        print("-" * 40)
        
        state_file = os.path.join(self.project_path, "harness/feedback/state/state.json")
        
        solo_completion = 0
        human_interventions = 0
        
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            solo_completion = state.get("metrics", {}).get("tasksCompleted", 0)
            human_interventions = state.get("metrics", {}).get("humanInterventions", 0)
        
        total_ops = solo_completion + human_interventions
        autonomy_rate = (solo_completion / total_ops * 100) if total_ops > 0 else 100
        
        print(f"   Solo Completions: {solo_completion}")
        print(f"   Human Interventions: {human_interventions}")
        print(f"   Autonomy Rate: {autonomy_rate:.0f}%")
        
        self.add("Autonomy", autonomy_rate, 15, "higher")
        
        return {
            "solo_completion": solo_completion,
            "human_interventions": human_interventions,
            "autonomy_rate": autonomy_rate
        }
    
    def run(self):
        print("=" * 60)
        print("HARNESS EFFECTIVENESS BENCHMARK")
        print("=" * 60)
        print(f"Project: {self.project_path}")
        print()
        
        # Run all measurements
        efficiency = self.measure_efficiency()
        quality = self.measure_quality()
        behavior = self.measure_behavior()
        autonomy = self.measure_autonomy()
        
        # Calculate final score
        final_score = self.score()
        grade, desc = self.grade(final_score)
        
        print()
        print("=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        print()
        
        # Breakdown
        for m in self.metrics:
            arrow = "↑" if m.direction == "higher" else "↓"
            print(f"   {m.name:22} {m.value:6.1f}% {arrow} (weight: {m.weight:.0f}%)")
        
        print()
        print(f"   {'='*40}")
        print(f"   {'FINAL SCORE':22} {final_score:6.1f}/100")
        print()
        print(f"   Grade: {grade} ({desc})")
        print()
        
        # Recommendations
        print("   Recommendations:")
        if efficiency["completion_rate"] < 85:
            print(f"   - Low completion rate ({efficiency['completion_rate']:.0f}%), improve task definition")
        if efficiency["block_rate"] > 10:
            print(f"   - High block rate ({efficiency['block_rate']:.0f}%), review /blocked usage")
        if quality["quality_score"] < 100:
            print(f"   - Clean up code issues ({quality['console_logs']} console.log, {quality['debuggers']} debugger)")
        if final_score >= 90:
            print("   - Excellent! Keep using harness best practices")
        elif final_score >= 70:
            print("   - Good, continue improving harness adoption")
        else:
            print("   - Consider full harness implementation")
        
        print()
        print("=" * 60)
        
        return {
            "score": final_score,
            "grade": grade,
            "description": desc,
            "efficiency": efficiency,
            "quality": quality,
            "behavior": behavior,
            "autonomy": autonomy
        }


def main():
    parser = argparse.ArgumentParser(description="Harness Effectiveness Benchmark")
    parser.add_argument("--project", "-p", default=".", help="Project path")
    args = parser.parse_args()
    
    benchmark = HarnessBenchmark(args.project)
    result = benchmark.run()
    
    # Exit code = 100 - score (lower is better)
    sys.exit(int(100 - result["score"]))


if __name__ == "__main__":
    main()
