# Benchmark Tool

> Harness 效果评分工具  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

Benchmark 通过检查 Harness 配置完整性、实际使用效果来评分。

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
| Efficiency | 40% | 任务完成效率 |
| Quality | 30% | 输出质量 |
| Behavior | 15% | 行为规范 |
| Autonomy | 15% | 自主能力 |

---

## 4. 使用方法

```bash
# 评分
python3 tools/benchmark/benchmark.py --project ./packages/agent-harness

# 对比两次评分
python3 tools/benchmark/benchmark.py --compare before.json after.json

# 查看详细报告
python3 tools/benchmark/benchmark.py --project ./ --verbose
```

---

## 5. 输出示例

```
========================================
       BENCHMARK REPORT
========================================
Project: packages/agent-harness
Date: 2026-03-25
----------------------------------------
EFFICIENCY         75.0/100  [████░░░░░░] Weight: 40%
QUALITY            80.0/100  [████████░░] Weight: 30%
BEHAVIOR           70.0/100  [███████░░░] Weight: 15%
AUTONOMY           75.0/100  [███████░░░] Weight: 15%
----------------------------------------
TOTAL SCORE        75.0/100
GRADE              C (Fair)
========================================
```

---

## 6. 指标详解

### Efficiency (效率)
- 任务完成时间
- Gate 通过率
- 阻塞次数

### Quality (质量)
- 代码规范
- 测试覆盖率
- 文档完整性

### Behavior (行为)
- 遵循约束规则
- 检查点更新
- 审计日志

### Autonomy (自主)
- 自主解决问题
- 避免无效询问
- 主动汇报
