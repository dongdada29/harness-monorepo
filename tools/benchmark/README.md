# Benchmark Tool

> Harness 效果评分工具
> 版本: 2.0.0
> 更新: 2026-04-20

---

## 1. 概述

Benchmark 通过检查 Harness 配置完整性、实际使用效果来评分。
运行结果保存在 `~/.harness/benchmark/history.jsonl`。

---

## 2. 评分体系

| 等级 | 分数 | 说明 |
|------|------|------|
| S+ | ≥95 | 卓越 |
| S | ≥90 | 优秀 |
| A+ | ≥85 | 很好 |
| A | ≥80 | 良好 |
| B+ | ≥75 | 较好 |
| B | ≥70 | 合格 |
| C+ | ≥65 | 一般 |
| C | ≥60 | 较差 |
| D | ≥50 | 很差 |
| F | <50 | 不合格 |

---

## 3. 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| Efficiency | 40% | 任务完成率、Gate 通过率、吞吐量 |
| Quality | 30% | 代码质量（lint、type check、test、build） |
| Behavior | 15% | state.json 更新频率、变更追踪 |
| Autonomy | 15% | 独立完成率、自我修正 |

---

## 4. 使用方法

```bash
# 评分（默认当前目录）
python3 -m tools.benchmark

# 指定项目
python3 -m tools.benchmark --project /path/to/project

# Markdown 报告
python3 -m tools.benchmark --project . --output markdown

# 查看历史
python3 -m tools.benchmark --history

# 保存结果
python3 -m tools.benchmark --project . --save result.json
```

---

## 5. 输出示例

```
============================================================
  HARNESS BENCHMARK
============================================================
  Project:     /path/to/project
  Time:        2026-04-20T21:04:40
  Run time:    13ms

  FINAL SCORE     75.2/100  B (Satisfactory)

  EFFICIENCY (40%)
    Completion     [██████░░░░░░░░░░░]  67%
    Block Rate     [████████████████░░]  33%
    Gate Pass      [██████████░░░░░░░░]  50%
    First Try      [████░░░░░░░░░░░░░]  40%
    Throughput     3 tasks

  QUALITY (30%)
    Base           [█████████░░░░░░░░░]  86
    Type Check     [--------------------]  FAIL
    Test           [--------------------]  FAIL
    Build          [--------------------]  FAIL
    console.log    2 occurrences
    debugger       2 occurrences

  BEHAVIOR (15%)
    Update Rate    [████████░░░░░░░░░░]  80%
    Tracking       [████░░░░░░░░░░░░░░]  20
    Violations     [████████████████████]  100
    Last Updated   2026-04-18

  AUTONOMY (15%)
    Solo Rate      [███████░░░░░░░░░░░]  70%
    Corrections    [--------------------]  0
    Escalation     [████████████████░░]  95

  RECOMMENDATIONS
    1. Completion rate low (67%) — review task definition
    2. Gate pass rate low (50%) — improve code quality
    3. Code quality issues — run lint fix
    4. Low change tracking — record recentChanges

  HISTORY
    Runs:          5
    Previous:      72.3  → +2.9
    Average:       73.8

============================================================
```

---

## 6. 指标详解

### Efficiency (效率)
- **Completion Rate**: 已完成任务 / 总任务
- **Block Rate**: 阻塞任务 / 总任务
- **Gate Pass Rate**: 通过的 Gate 数量 / 总 Gate
- **First Try Rate**: 首次通过率
- **Throughput**: 任务吞吐量

### Quality (质量)
- **Base**: 100 - console.log×2 - debugger×5
- **Type Check / Test / Build**: state.json gates 记录

### Behavior (行为)
- **Update Rate**: 基于 lastUpdated 距今天数
- **Tracking**: recentChanges 条数 × 20
- **Violations**: 约束违规扣分

### Autonomy (自主)
- **Solo Rate**: 独立完成 / (独立完成 + 人工介入)
- **Corrections**: 自我修正次数
- **Escalation**: 合理升级次数
