# Harness Evaluator CLI

> 完整的 Harness 效果评估工具

---

## 工具列表

| 工具 | 语言 | 说明 |
|------|------|------|
| `evaluator.py` | Python | 评估体系文档 |
| `benchmark.py` | Python | **Benchmark v2** 评分系统 |
| `evaluator.sh` | Shell | 快速检查 |

---

## Benchmark v2

运行基准测试获得综合评分：

```bash
python3 tools/eval-cli/benchmark.py --project /path/to/project
```

### 评分维度

| 维度 | 权重 | 指标 |
|------|------|------|
| **Efficiency** | 40% | 完成任务率、Gate通过率、阻塞率、首次通过率、吞吐量 |
| **Quality** | 30% | console.log、debugger、Type检查、测试、构建 |
| **Behavior** | 15% | State更新率、变更追踪、违规数 |
| **Autonomy** | 15% | 自主完成率、自我修正率、升级率 |

### 评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| S+ >= 95 | World Class |
| S >= 90 | Excellent |
| A+ >= 85 | Outstanding |
| A >= 80 | Very Good |
| B+ >= 75 | Good |
| B >= 70 | Satisfactory |
| C >= 60 | Marginal |
| D >= 50 | Poor |
| F < 50 | Fail |

### 示例输出

```
============================================================
  HARNESS EFFECTIVENESS BENCHMARK v2
============================================================
  Project: my-project
  Time: 2026-03-22 00:52

1. EFFICIENCY (40%)
   Tasks Completed:  15
   Tasks Blocked:    2
   Completion Rate: 88.2%
   Block Rate:      11.8%
   Gate Pass Rate:   91.7%
   First-Try Rate:  85.0%
   Throughput:      0.75 tasks/day

2. QUALITY (30%)
   console.log:     3
   debugger:       0
   Quality Score:  94.0
   Type Check:      PASS
   Test Pass:       PASS
   Build:           PASS

3. BEHAVIOR (15%)
   Last State Update: 2026-03-22
   Update Rate:       100%
   Recent Changes:   12
   Tracking Score:   100%
   Violations:       0

4. AUTONOMY (15%)
   Solo Completions: 13
   Human Interventions: 2
   Autonomy Rate:   86.7%

============================================================
  RESULTS
============================================================

   FINAL SCORE            87.3/100
   GRADE                A (Very Good)

   BREAKDOWN:
   Efficiency            88.2%  (completion)
   Quality               94.0%  (code issues)
   Behavior              80.0%  (state mgmt)
   Autonomy              86.7%  (self-sufficiency)

   RECOMMENDATIONS:
   1. Completion rate (88%) - consider higher targets
   2. State update rate (100%) - excellent!
```

---

## 使用方法

### 基本用法

```bash
# 运行 benchmark
python3 tools/eval-cli/benchmark.py -p /path/to/project

# 保存结果
python3 tools/eval-cli/benchmark.py -p . -s results.json

# 对比基准
python3 tools/eval-cli/benchmark.py -p . -b baseline/
```

### 输出格式

默认是文本格式，也可以输出 JSON：

```bash
python3 tools/eval-cli/benchmark.py -p . -o json
```

---

## CI 集成

```yaml
# .github/workflows/harness-benchmark.yml
name: Harness Benchmark

on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一
  workflow_dispatch:

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Benchmark
        run: python3 tools/eval-cli/benchmark.py -p . -s benchmark.json
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark.json
```

---

## 解读评分

### 高分项目 (>85)

- ✅ 完整使用 harness 工作流
- ✅ 定期更新 state.json
- ✅ Gate 通过率高
- ✅ 代码质量好

### 中等项目 (70-85)

- ⚠️ 部分 harness 功能未使用
- ⚠️ State 更新不及时
- ⚠️ 偶尔违规

### 低分项目 (<70)

- ❌ 未正确使用 harness
- ❌ State 未更新
- ❌ 代码质量问题多
- ❌ 频繁需要人类介入
