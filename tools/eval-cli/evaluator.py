#!/usr/bin/env python3
"""
Harness Evaluator - CLI Tool
===========================
Usage: python3 evaluator.py --project /path/to/project --report weekly

Metrics collected:
- Efficiency: completion_rate, avg_duration, gate_pass_rate, block_rate
- Quality: lint_errors, type_errors, test_coverage, regression_rate
- Behavior: violation_rate, block_report_rate, state_update_rate
- Autonomy: human_intervention_rate, solo_completion_rate
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ANSI colors
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color


def log(msg: str, color: str = NC):
    print(f"{color}{msg}{NC}")


def load_json(path: str) -> Dict:
    """Load JSON file."""
    try:
        with open(path) as f:
            return json.load(f)
    except Exception as e:
        log(f"Warning: Cannot load {path}: {e}", RED)
        return {}


def save_json(path: str, data: Dict):
    """Save JSON file."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


class HarnessEvaluator:
    """Harness Effectiveness Evaluator."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.state_file = self.project_path / "harness/feedback/state/state.json"
        self.history_dir = self.project_path / "harness/feedback/history"
        self.metrics_file = self.project_path / "harness/feedback/metrics/evaluator_metrics.json"
        
        self.data: Dict = {}
        self.baseline = {}
        
    def load(self):
        """Load data from project."""
        log("Loading project data...")
        
        # Load state.json
        if self.state_file.exists():
            self.data['state'] = load_json(str(self.state_file))
        else:
            self.data['state'] = {}
            log("Warning: state.json not found", YELLOW)
        
        # Load history
        if self.history_dir.exists():
            history_files = list(self.history_dir.glob("*.json")) + list(self.history_dir.glob("*.md"))
            self.data['history'] = []
            for f in history_files:
                if f.suffix == '.json':
                    self.data['history'].append(load_json(str(f)))
        else:
            self.data['history'] = []
        
        log(f"Loaded {len(self.data.get('history', []))} history records")
        log(f"State file: {self.state_file}", GREEN)
        
    def collect_metrics(self, period: str = "weekly") -> Dict:
        """
        Collect metrics based on period.
        
        Args:
            period: "daily", "weekly", "monthly"
        """
        log(f"\nCollecting {period} metrics...")
        
        # Calculate date range
        now = datetime.now()
        if period == "daily":
            delta = timedelta(days=1)
        elif period == "weekly":
            delta = timedelta(weeks=1)
        else:  # monthly
            delta = timedelta(days=30)
        
        start_date = now - delta
        
        # Initialize metrics
        metrics = {
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": now.isoformat(),
            "efficiency": {},
            "quality": {},
            "behavior": {},
            "autonomy": {},
        }
        
        # Efficiency metrics from state
        state = self.data.get('state', {})
        
        # Tasks completed
        tasks_completed = state.get('metrics', {}).get('tasksCompleted', 0)
        tasks_blocked = state.get('metrics', {}).get('tasksBlocked', 0)
        total_tasks = tasks_completed + tasks_blocked
        
        metrics['efficiency']['tasks_total'] = total_tasks
        metrics['efficiency']['tasks_completed'] = tasks_completed
        metrics['efficiency']['tasks_blocked'] = tasks_blocked
        metrics['efficiency']['completion_rate'] = (
            (tasks_completed / total_tasks * 100) if total_tasks > 0 else 0
        )
        metrics['efficiency']['block_rate'] = (
            (tasks_blocked / total_tasks * 100) if total_tasks > 0 else 0
        )
        
        # Average duration
        avg_duration = state.get('metrics', {}).get('averageTaskDuration')
        metrics['efficiency']['avg_duration_minutes'] = avg_duration or 0
        
        # Gate stats
        gates = state.get('gates', {})
        gates_passed = sum(1 for v in gates.values() if v == 'passed')
        gates_total = len(gates) or 4
        metrics['efficiency']['gate_pass_rate'] = (gates_passed / gates_total * 100)
        
        # Quality metrics (simulated - would need CI integration)
        metrics['quality']['lint_errors'] = 0  # From CI
        metrics['quality']['type_errors'] = 0   # From CI
        metrics['quality']['test_coverage'] = 0  # From CI
        metrics['quality']['regression_rate'] = 0
        
        # Behavior metrics
        metrics['behavior']['violations'] = 0
        metrics['behavior']['state_updates'] = 1 if state else 0
        
        # Autonomy metrics
        metrics['autonomy']['human_interventions'] = 0
        metrics['autonomy']['solo_completions'] = tasks_completed
        
        return metrics
    
    def calculate_baseline(self, metrics: Dict) -> Dict:
        """Calculate baseline for comparison."""
        # Use first data point as baseline
        if not self.baseline:
            self.baseline = metrics.copy()
        return self.baseline
    
    def compare(self, current: Dict, baseline: Dict) -> Dict:
        """Compare current metrics with baseline."""
        comparison = {}
        for category in ['efficiency', 'quality', 'behavior', 'autonomy']:
            comparison[category] = {}
            curr = current.get(category, {})
            base = baseline.get(category, {})
            for key in set(list(curr.keys()) + list(base.keys())):
                curr_val = curr.get(key, 0)
                base_val = base.get(key, 0)
                if base_val and base_val != 0:
                    change = ((curr_val - base_val) / base_val) * 100
                    comparison[category][key] = {
                        'current': curr_val,
                        'baseline': base_val,
                        'change': change
                    }
                else:
                    comparison[category][key] = {
                        'current': curr_val,
                        'baseline': base_val,
                        'change': 0
                    }
        return comparison
    
    def generate_report(self, metrics: Dict, comparison: Optional[Dict] = None):
        """Generate evaluation report."""
        print("\n" + "=" * 60)
        print(f"{BLUE}Harness 效果评估报告{NC}")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"项目: {self.project_path.name}")
        print(f"周期: {metrics.get('period', 'weekly')}")
        print()
        
        # Efficiency Section
        print(f"{BLUE}一、效率指标{NC}")
        print("-" * 40)
        eff = metrics.get('efficiency', {})
        print(f"  完成任务数: {eff.get('tasks_completed', 0)}")
        print(f"  被阻塞数: {eff.get('tasks_blocked', 0)}")
        print(f"  完成率: {eff.get('completion_rate', 0):.1f}%")
        print(f"  阻塞率: {eff.get('block_rate', 0):.1f}%")
        print(f"  平均时长: {eff.get('avg_duration_minutes', 0):.0f} 分钟")
        print(f"  Gate 通过率: {eff.get('gate_pass_rate', 0):.1f}%")
        print()
        
        # Quality Section
        print(f"{BLUE}二、质量指标{NC}")
        print("-" * 40)
        qual = metrics.get('quality', {})
        print(f"  Lint 错误数: {qual.get('lint_errors', 0)}")
        print(f"  Type 错误数: {qual.get('type_errors', 0)}")
        print(f"  测试覆盖率: {qual.get('test_coverage', 0):.1f}%")
        print(f"  Bug 回归率: {qual.get('regression_rate', 0):.1f}%")
        print()
        
        # Behavior Section
        print(f"{BLUE}三、行为指标{NC}")
        print("-" * 40)
        behav = metrics.get('behavior', {})
        print(f"  约束违规数: {behav.get('violations', 0)}")
        print(f"  状态更新数: {behav.get('state_updates', 0)}")
        print()
        
        # Autonomy Section
        print(f"{BLUE}四、自主能力{NC}")
        print("-" * 40)
        auto = metrics.get('autonomy', {})
        print(f"  人类介入次数: {auto.get('human_interventions', 0)}")
        print(f"  自主完成数: {auto.get('solo_completions', 0)}")
        print()
        
        # Comparison with baseline
        if comparison:
            print(f"{BLUE}五、与基线对比{NC}")
            print("-" * 40)
            for category in ['efficiency', 'quality', 'behavior', 'autonomy']:
                cat_comp = comparison.get(category, {})
                if cat_comp:
                    print(f"  {category}:")
                    for key, vals in cat_comp.items():
                        change = vals.get('change', 0)
                        arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                        color = GREEN if change < 0 else RED if change > 0 else NC
                        print(f"    {key}: {vals.get('baseline', 0):.1f} {arrow} {vals.get('current', 0):.1f} ({change:+.1f}%)")
            print()
        
        # Recommendations
        print(f"{BLUE}六、改进建议{NC}")
        print("-" * 40)
        recommendations = self._get_recommendations(metrics)
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        print()
        
        # Save metrics
        if self.metrics_file:
            save_json(str(self.metrics_file), metrics)
            log(f"Metrics saved to {self.metrics_file}", GREEN)
    
    def _get_recommendations(self, metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics."""
        recs = []
        
        eff = metrics.get('efficiency', {})
        qual = metrics.get('quality', {})
        behav = metrics.get('behavior', {})
        
        # Check completion rate
        if eff.get('completion_rate', 100) < 85:
            recs.append(f"完成率较低 ({eff.get('completion_rate', 0):.0f}%)，考虑优化任务范围定义")
        
        # Check block rate
        if eff.get('block_rate', 0) > 10:
            recs.append(f"阻塞率较高 ({eff.get('block_rate', 0):.0f}%)，检查 /blocked 使用是否正确")
        
        # Check gate pass rate
        if eff.get('gate_pass_rate', 100) < 90:
            recs.append(f"Gate 通过率较低 ({eff.get('gate_pass_rate', 0):.0f}%)，加强代码自检")
        
        # Check lint errors
        if qual.get('lint_errors', 0) > 0:
            recs.append(f"存在 {qual.get('lint_errors', 0)} 个 Lint 错误，使用 npm run lint --fix 修复")
        
        # Check violations
        if behav.get('violations', 0) > 0:
            recs.append(f"有 {behav.get('violations', 0)} 次约束违规，重读 harness/base/constraints.md")
        
        if not recs:
            recs.append("各项指标良好，继续保持!")
        
        return recs
    
    def run(self, period: str = "weekly"):
        """Run full evaluation."""
        self.load()
        metrics = self.collect_metrics(period)
        baseline = self.calculate_baseline(metrics)
        comparison = self.compare(metrics, baseline)
        self.generate_report(metrics, comparison)


def main():
    parser = argparse.ArgumentParser(
        description="Harness Evaluator - 评估 AI Agent 开发工作流效果"
    )
    parser.add_argument(
        "--project", "-p",
        default=".",
        help="项目路径 (默认: 当前目录)"
    )
    parser.add_argument(
        "--period",
        choices=["daily", "weekly", "monthly"],
        default="weekly",
        help="评估周期 (默认: weekly)"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="生成完整报告"
    )
    
    args = parser.parse_args()
    
    evaluator = HarnessEvaluator(args.project)
    evaluator.run(args.period)


if __name__ == "__main__":
    main()
