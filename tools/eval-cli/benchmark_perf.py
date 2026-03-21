#!/usr/bin/env python3
"""
Benchmark Performance Optimizations
====================================
Caching, parallel processing, and memoization for faster benchmarks.
"""

import os
import json
import hashlib
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess


class BenchmarkCache:
    """Simple file-based cache for benchmark results."""
    
    def __init__(self, cache_dir: str = ".benchmark_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_cache_key(self, project_path: str, file_pattern: str = "") -> str:
        """Generate cache key based on project state."""
        key_data = f"{project_path}:{file_pattern}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Dict]:
        """Get cached result."""
        cache_file = self.cache_dir / f"{key}.json"
        if cache_file.exists():
            try:
                return json.loads(cache_file.read_text())
            except:
                pass
        return None
    
    def set(self, key: str, value: Dict) -> None:
        """Cache result."""
        cache_file = self.cache_dir / f"{key}.json"
        cache_file.write_text(json.dumps(value, indent=2))
    
    def clear(self) -> None:
        """Clear all cache."""
        for f in self.cache_dir.glob("*.json"):
            f.unlink()


class ParallelMetrics:
    """Parallel metric collection for faster benchmarks."""
    
    @staticmethod
    def count_files(project_path: str, patterns: list) -> Dict[str, int]:
        """Count files matching multiple patterns in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        results = {}
        
        def count_pattern(pattern: str) -> tuple:
            try:
                result = subprocess.run(
                    ["find", project_path, "-name", pattern, "-type", "f"],
                    capture_output=True, text=True, timeout=10
                )
                count = len([l for l in result.stdout.strip().split("\n") if l])
                return (pattern, count)
            except:
                return (pattern, 0)
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(count_pattern, p) for p in patterns]
            for future in as_completed(futures):
                pattern, count = future.result()
                results[pattern] = count
        
        return results
    
    @staticmethod
    def run_gates_parallel(project_path: str) -> Dict[str, bool]:
        """Run multiple gates in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        gates = {
            "lint": ["npm", "run", "lint", "--silent"],
            "typecheck": ["npm", "run", "typecheck", "--silent"],
            "test": ["npm", "test", "--silent"],
            "build": ["npm", "run", "build", "--silent"]
        }
        
        results = {}
        
        def run_gate(name: str, cmd: list) -> tuple:
            try:
                result = subprocess.run(
                    cmd,
                    cwd=project_path,
                    capture_output=True,
                    timeout=60
                )
                return (name, result.returncode == 0)
            except:
                return (name, False)
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [executor.submit(run_gate, name, cmd) for name, cmd in gates.items()]
            for future in as_completed(futures):
                name, passed = future.result()
                results[name] = passed
        
        return results


# Memoization helpers
@lru_cache(maxsize=128)
def cached_file_count(project_path: str, extension: str) -> int:
    """Cached file counting."""
    try:
        result = subprocess.run(
            ["find", project_path, "-name", f"*{extension}", "-type", "f"],
            capture_output=True, text=True, timeout=10
        )
        return len([l for l in result.stdout.strip().split("\n") if l])
    except:
        return 0


@lru_cache(maxsize=64)
def cached_git_log(project_path: str, count: int) -> str:
    """Cached git log."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--oneline"],
            cwd=project_path,
            capture_output=True, text=True, timeout=5
        )
        return result.stdout
    except:
        return ""


def benchmark_performance_tips():
    """Print performance optimization tips."""
    tips = """
    Benchmark Performance Tips:
    ===========================
    
    1. Use caching for repeated runs:
       cache = BenchmarkCache()
       result = cache.get(key) or compute_expensive_metric()
       cache.set(key, result)
    
    2. Parallelize file counting:
       counts = ParallelMetrics.count_files(path, ["*.ts", "*.tsx", "*.js"])
    
    3. Run gates in parallel:
       gates = ParallelMetrics.run_gates_parallel(path)
    
    4. Use memoization for repeated calls:
       count = cached_file_count(path, ".ts")
    
    5. Clear cache when needed:
       cache.clear()
    """
    print(tips)


if __name__ == "__main__":
    benchmark_performance_tips()
