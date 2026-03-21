#!/usr/bin/env python3
"""
Harness Benchmark - Score Calculator
================================
Usage: python3 benchmark.py --project /path/to/project

Produces a composite score (0-100) for Harness effectiveness.
"""

import argparse
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class MetricScore:
    name: str
    value: float
    weight: float
    direction: str  # "higher" or "lower" is better
    
class HarnessBenchmark:
    """Calculate Harness effectiveness score."""
    
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.scores: List[MetricScore] = []
        self.total_weight = 0
        
    def add_metric(self, name: str, value: float, weight: float, direction: str = "higher"):
        """Add a metric to the benchmark."""
        self.scores.append(MetricScore(name, value, weight, direction))
        self.total_weight += weight
        
    def calculate_score(self) -> float:
        """Calculate weighted composite score."""
        if not self.scores:
            return 0
            
        weighted_sum = 0
        for ms in self.scores:
            if ms.direction == "higher":
                # Higher is better, normalize to 0-100
                normalized = min(100, max(0, ms.value))
            else:
                # Lower is better, invert
                normalized = min(100, max(0, 100 - ms.value))
            weighted_sum += normalized * ms.weight
            
        return weighted_sum / self.total_weight if self.total_weight > 0 else 0
    
    def run_lint_check(self) -> Dict:
        """Run lint check."""
        result = {
            "console_logs": 0,
            "debuggers": 0,
            "todos": 0,
            "score": 100
        }
        
        src_dir = os.path.join(self.project_path, "src")
        if not os.path.exists(src_dir):
            src_dir = self.project_path
            
        try:
            # Count console.log
            r = subprocess.run(
                ["grep", "-r", "console.log", src_dir, "--include=*.ts", "--include=*.tsx", "--include=*.js"],
                capture_output=True, text=True, timeout=10
            )
            result["console_logs"] = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
        except:
            pass
            
        try:
            # Count debugger
            r = subprocess.run(
                ["grep", "-r", "debugger", src_dir, "--include=*.ts", "--include=*.tsx", "--include=*.js"],
                capture_output=True, text=True, timeout=10
            )
            result["debuggers"] = len(r.stdout.strip().split("\n")) if r.stdout.strip() else 0
        except:
            pass
            
        # Score: penalize each issue
        result["score"] = max(0, 100 - (result["console_logs"] * 5) - (result["debuggers"] * 10))
        
        return result
    
    def check_harness_structure(self) -> Dict:
        """Check if harness structure is complete."""
        result = {
            "files_found": [],
            "files_missing": [],
            "score": 0
        }
        
        required_files = [
            "CLAUDE.md",
            ".cursorrules",
            "AGENTS.md",
            "harness/feedback/state/state.json",
            "harness/base/constraints.md",
        ]
        
        for f in required_files:
            path = os.path.join(self.project_path, f)
            if os.path.exists(path):
                result["files_found"].append(f)
            else:
                result["files_missing"].append(f)
                
        result["score"] = (len(result["files_found"]) / len(required_files)) * 100
        return result
        
    def run_benchmark(self) -> Dict:
        """Run full benchmark."""
        print("=" * 60)
        print("Harness Benchmark")
        print("=" * 60)
        print(f"Project: {self.project_path}")
        print()
        
        # 1. Harness Structure (30% weight)
        print("1. Harness Structure (30%)")
        print("-" * 40)
        structure = self.check_harness_structure()
        self.add_metric("Structure", structure["score"], 30, "higher")
        print(f"   Score: {structure['score']:.0f}/100")
        print(f"   Found: {len(structure['files_found'])}/{len(structure['files_found']) + len(structure['files_missing'])} files")
        if structure["files_missing"]:
            print(f"   Missing: {', '.join(structure['files_missing'])}")
        print()
        
        # 2. Code Quality (30% weight)
        print("2. Code Quality (30%)")
        print("-" * 40)
        quality = self.run_lint_check()
        self.add_metric("Quality", quality["score"], 30, "higher")
        print(f"   Score: {quality['score']:.0f}/100")
        print(f"   console.log: {quality['console_logs']}")
        print(f"   debugger: {quality['debuggers']}")
        print()
        
        # 3. Task Metrics (40% weight)
        print("3. Task Metrics (40%)")
        print("-" * 40)
        state_file = os.path.join(self.project_path, "harness/feedback/state/state.json")
        if os.path.exists(state_file):
            with open(state_file) as f:
                state = json.load(f)
            
            tasks_completed = state.get("metrics", {}).get("tasksCompleted", 0)
            tasks_blocked = state.get("metrics", {}).get("tasksBlocked", 0)
            total = tasks_completed + tasks_blocked
            
            if total > 0:
                completion_rate = (tasks_completed / total) * 100
                block_rate = (tasks_blocked / total) * 100
            else:
                completion_rate = 100
                block_rate = 0
                
            self.add_metric("Completion", completion_rate, 20, "higher")
            self.add_metric("Block", block_rate, 20, "lower")
            
            print(f"   Completed: {tasks_completed}")
            print(f"   Blocked: {tasks_blocked}")
            print(f"   Completion Rate: {completion_rate:.0f}%")
            print(f"   Block Rate: {block_rate:.0f}%")
        else:
            print("   No state.json found (using default)")
            self.add_metric("Completion", 100, 20, "higher")
            self.add_metric("Block", 0, 20, "lower")
        print()
        
        # Calculate final score
        final_score = self.calculate_score()
        
        # Print summary
        print("=" * 60)
        print("BENCHMARK RESULTS")
        print("=" * 60)
        print()
        
        # Score breakdown
        for ms in self.scores:
            direction = "↑" if ms.direction == "higher" else "↓"
            print(f"   {ms.name:20} {ms.value:6.1f}/100 {direction}")
        
        print()
        print(f"   {'TOTAL SCORE':20} {final_score:6.1f}/100")
        print()
        
        # Grade
        if final_score >= 90:
            grade = "A"
            desc = "Excellent"
        elif final_score >= 80:
            grade = "B"
            desc = "Good"
        elif final_score >= 70:
            grade = "C"
            desc = "Fair"
        elif final_score >= 60:
            grade = "D"
            desc = "Needs Improvement"
        else:
            grade = "F"
            desc = "Poor"
            
        print(f"   Grade: {grade} ({desc})")
        print()
        
        # Recommendations
        print("   Recommendations:")
        if structure["score"] < 100:
            print(f"   - Complete Harness structure ({len(structure['files_missing'])} files missing)")
        if quality["score"] < 100:
            print(f"   - Clean up code issues ({quality['console_logs']} console.log, {quality['debuggers']} debugger)")
        if final_score >= 90:
            print("   - Keep up the good work!")
        elif final_score >= 70:
            print("   - Consider implementing more harness practices")
        else:
            print("   - Review and implement full harness system")
            
        print()
        print("=" * 60)
        
        return {
            "score": final_score,
            "grade": grade,
            "description": desc,
            "structure": structure,
            "quality": quality
        }


def main():
    parser = argparse.ArgumentParser(description="Harness Benchmark")
    parser.add_argument("--project", "-p", default=".", help="Project path")
    args = parser.parse_args()
    
    benchmark = HarnessBenchmark(args.project)
    result = benchmark.run_benchmark()
    
    # Exit with score as code
    sys.exit(int(100 - result["score"]))


if __name__ == "__main__":
    main()
