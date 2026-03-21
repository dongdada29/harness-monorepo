# Harness Evaluator CLI

> 完整的 Harness 效果评估工具

## 工具列表

| 工具 | 语言 | 说明 |
|------|------|------|
| `evaluator.py` | Python | 完整功能版（推荐） |
| `evaluator.sh` | Shell | 轻量版（无需 Python） |

## 使用方法

### Python 版本（推荐）

```bash
# 安装
pip install -r requirements.txt  # 如需要

# 运行
python3 tools/eval-cli/evaluator.py --project /path/to/project --period weekly
```

### Shell 版本（无需依赖）

```bash
# 运行
bash tools/eval-cli/evaluator.sh /path/to/project
```

## 功能

### 1. 效率指标
- 完成任务数
- 被阻塞数
- 完成率
- 阻塞率
- 平均任务时长
- Gate 通过率

### 2. 质量指标
- Lint 错误数
- Type 错误数
- 测试覆盖率
- Bug 回归率

### 3. 行为指标
- 约束违规数
- 状态更新数

### 4. 自主能力指标
- 人类介入次数
- 自主完成数

## 评估维度

```
Efficiency ──→ Quality ──→ Behavior ──→ Autonomy
    │              │            │            │
    ▼              ▼            ▼            ▼
完成任务率    Lint错误    约束违规    人类介入
Gate通过率    覆盖率      状态更新    自主完成
```

## 输出示例

```
============================================================
Harness 效果评估报告
============================================================
时间: 2026-03-21 23:55
项目: my-project
周期: weekly

一、效率指标
----------------------------------------
  完成任务数: 15
  被阻塞数: 2
  完成率: 88.2%
  阻塞率: 11.8%
  平均时长: 32 分钟
  Gate 通过率: 91.7%

二、质量指标
----------------------------------------
  Lint 错误数: 0
  Type 错误数: 0
  测试覆盖率: 82.5%
  Bug 回归率: 0.0%

三、行为指标
----------------------------------------
  约束违规数: 1
  状态更新数: 15

四、自主能力
----------------------------------------
  人类介入次数: 3
  自主完成数: 12

五、改进建议
----------------------------------------
  1. 完成率较低 (< 85%)，考虑优化任务范围定义
  2. 存在 1 个约束违规，重读 harness/base/constraints.md
```

## 集成到 CI

```yaml
# .github/workflows/eval.yml
name: Harness Evaluation

on:
  schedule:
    - cron: '0 0 * * 1'  # 每周一

jobs:
  evaluate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Evaluator
        run: python3 tools/eval-cli/evaluator.py --period weekly
```

## Benchmark

运行基准测试获得综合评分：

```bash
python3 tools/eval-cli/benchmark.py --project /path/to/project
```

### 评分维度

| 维度 | 权重 | 说明 |
|------|------|------|
| **Harness Structure** | 30% | 必需文件是否完整 |
| **Code Quality** | 30% | console.log、debugger 数量 |
| **Task Metrics** | 40% | 完成任务率、阻塞率 |

### 评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| 90-100 | A | Excellent |
| 80-89 | B | Good |
| 70-79 | C | Fair |
| 60-69 | D | Needs Improvement |
| <60 | F | Poor |

### 示例输出

```
TOTAL SCORE            85.0/100

Grade: B (Good)

Recommendations:
- Complete Harness structure
- Clean up code issues
```
