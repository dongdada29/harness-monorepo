# Benchmark 指标详解

> 详细解释 harness benchmark 的各项指标

---

## 概述

harness benchmark 是一个综合评估系统，用于量化评估 Agent 使用 harness 的效果。

### 评分维度

| 维度 | 权重 | 重要性 |
|------|------|--------|
| **Efficiency** | 40% | 效率 - 最重要 |
| **Quality** | 30% | 质量 - 次重要 |
| **Behavior** | 15% | 行为 - 辅助 |
| **Autonomy** | 15% | 自主性 - 辅助 |

---

## 1. Efficiency (效率) - 40%

效率是最重要的维度，衡量 Agent 完成任务的能力。

### 指标

#### 1.1 任务完成率 (Task Completion Rate)

**定义**: 成功完成的任务占比

**计算**:
```python
completion_rate = (tasks_completed / total_tasks) * 100
```

**标准**:
- S+: 100%
- S: >= 95%
- A: >= 90%
- B: >= 80%
- C: >= 70%

**影响**:
- 高完成率 = Agent 可靠
- 低完成率 = Agent 经常失败

---

#### 1.2 Gate 通过率 (Gate Pass Rate)

**定义**: 质量门禁通过占比

**计算**:
```python
gate_pass_rate = (gates_passed / total_gates) * 100
```

**标准**:
- S+: 100%
- S: >= 95%
- A: >= 90%
- B: >= 80%
- C: >= 70%

**影响**:
- 高通过率 = 代码质量高
- 低通过率 = 代码问题多

---

#### 1.3 阻塞率 (Block Rate)

**定义**: 被阻塞的任务占比

**计算**:
```python
block_rate = (tasks_blocked / total_tasks) * 100
```

**标准**:
- S+: 0%
- S: <= 5%
- A: <= 10%
- B: <= 20%
- C: <= 30%

**影响**:
- 低阻塞率 = Agent 自主性强
- 高阻塞率 = Agent 经常需要帮助

---

#### 1.4 首次通过率 (First-Try Pass Rate)

**定义**: 第一次就通过 gate 的占比

**计算**:
```python
first_try_rate = (first_try_passes / total_gates) * 100
```

**标准**:
- S+: 100%
- S: >= 90%
- A: >= 80%
- B: >= 70%
- C: >= 60%

**影响**:
- 高首次通过率 = Agent 质量意识强
- 低首次通过率 = Agent 需要多次尝试

---

#### 1.5 吞吐量 (Throughput)

**定义**: 每天完成的任务数

**计算**:
```python
throughput = tasks_completed / days_since_reset
```

**标准**:
- S+: >= 10 tasks/day
- S: >= 8 tasks/day
- A: >= 6 tasks/day
- B: >= 4 tasks/day
- C: >= 2 tasks/day

**影响**:
- 高吞吐量 = Agent 效率高
- 低吞吐量 = Agent 效率低

---

## 2. Quality (质量) - 30%

质量衡量代码的整洁度和可维护性。

### 指标

#### 2.1 console.log 数量

**定义**: 代码中 console.log 的数量

**计算**:
```python
console_log_count = count_pattern("console\\.log", src_dir)
```

**标准**:
- S+: 0
- S: 1-2
- A: 3-5
- B: 6-10
- C: 11-20

**影响**:
- 少 = 代码整洁
- 多 = 调试代码未清理

---

#### 2.2 debugger 数量

**定义**: 代码中 debugger 语句的数量

**计算**:
```python
debugger_count = count_pattern("\\bdebugger\\b", src_dir)
```

**标准**:
- S+: 0
- S: 0
- A: 1
- B: 2-3
- C: 4-5

**影响**:
- 少 = 代码整洁
- 多 = 调试代码未清理

---

#### 2.3 TypeScript 检查

**定义**: TypeScript 类型错误数

**计算**:
```bash
npm run typecheck 2>&1 | grep "error TS" | wc -l
```

**标准**:
- S+: 0 errors
- S: 0 errors
- A: 1-2 errors
- B: 3-5 errors
- C: 6-10 errors

**影响**:
- 少 = 类型安全
- 多 = 类型问题

---

#### 2.4 测试通过率

**定义**: 测试通过的占比

**计算**:
```bash
npm test 2>&1 | grep "passed" | awk '{print $2}'
```

**标准**:
- S+: 100%
- S: >= 95%
- A: >= 90%
- B: >= 80%
- C: >= 70%

**影响**:
- 高 = 代码可靠
- 低 = 代码不可靠

---

#### 2.5 构建成功率

**定义**: 构建成功的次数占比

**计算**:
```bash
npm run build 2>&1 | grep "error" | wc -l
```

**标准**:
- S+: 0 errors
- S: 0 errors
- A: 1-2 errors
- B: 3-5 errors
- C: 6-10 errors

**影响**:
- 高 = 代码可构建
- 低 = 构建失败

---

## 3. Behavior (行为) - 15%

行为衡量 Agent 是否遵循 harness 规范。

### 指标

#### 3.1 State 更新率

**定义**: 任务完成后 state.json 的更新频率

**计算**:
```python
state_update_rate = (state_updates / tasks_completed) * 100
```

**标准**:
- S+: 100%
- S: >= 95%
- A: >= 90%
- B: >= 80%
- C: >= 70%

**影响**:
- 高 = Agent 规范性好
- 低 = Agent 忘记更新状态

---

#### 3.2 变更追踪率

**定义**: 记录变更的频率

**计算**:
```python
change_tracking_rate = (changes_tracked / total_changes) * 100
```

**标准**:
- S+: 100%
- S: >= 90%
- A: >= 80%
- B: >= 70%
- C: >= 60%

**影响**:
- 高 = 可追溯性好
- 低 = 难以追溯

---

#### 3.3 约束违规数

**定义**: 违反约束的次数

**计算**:
```python
violation_count = count_violations()
```

**标准**:
- S+: 0
- S: 0
- A: 1-2
- B: 3-5
- C: 6-10

**影响**:
- 少 = Agent 遵守规范
- 多 = Agent 不遵守规范

---

## 4. Autonomy (自主性) - 15%

自主性衡量 Agent 的独立工作能力。

### 指标

#### 4.1 自主完成率

**定义**: 无需 human intervention 完成的任务占比

**计算**:
```python
autonomy_rate = (tasks_completed_independently / tasks_completed) * 100
```

**标准**:
- S+: >= 95%
- S: >= 90%
- A: >= 85%
- B: >= 80%
- C: >= 70%

**影响**:
- 高 = Agent 独立性强
- 低 = Agent 依赖性高

---

#### 4.2 自我修正率

**定义**: 自行修复错误的频率

**计算**:
```python
self_correction_rate = (errors_self_corrected / total_errors) * 100
```

**标准**:
- S+: >= 90%
- S: >= 80%
- A: >= 70%
- B: >= 60%
- C: >= 50%

**影响**:
- 高 = Agent 自愈能力强
- 低 = Agent 需要帮助

---

#### 4.3 升级率

**定义**: 自行升级约束的频率

**计算**:
```python
upgrade_rate = (constraint_upgrades / tasks_completed) * 100
```

**标准**:
- S+: >= 20%
- S: >= 15%
- A: >= 10%
- B: >= 5%
- C: >= 2%

**影响**:
- 高 = Agent 学习能力强
- 低 = Agent 学习能力弱

---

## 总体评分计算

### Formula

```python
overall = (
    efficiency_score * 0.40 +
    quality_score * 0.30 +
    behavior_score * 0.15 +
    autonomy_score * 0.15
)
```

### 评分标准

| 分数 | 等级 | 描述 |
|------|------|------|
| 95-100 | S+ | World Class |
| 90-94 | S | Excellent |
| 85-89 | A+ | Outstanding |
| 80-84 | A | Very Good |
| 75-79 | B+ | Good |
| 70-74 | B | Satisfactory |
| 60-69 | C | Marginal |
| 50-59 | D | Poor |
| 0-49 | F | Fail |

---

## 示例

### 示例 1: 优秀 Agent

```json
{
  "efficiency": {
    "completion_rate": 98,
    "gate_pass_rate": 95,
    "block_rate": 2,
    "first_try_rate": 92,
    "throughput": 8.5
  },
  "quality": {
    "console_log": 0,
    "debugger": 0,
    "type_errors": 0,
    "test_pass_rate": 98,
    "build_errors": 0
  },
  "behavior": {
    "state_update_rate": 100,
    "change_tracking_rate": 98,
    "violations": 0
  },
  "autonomy": {
    "autonomy_rate": 95,
    "self_correction_rate": 88,
    "upgrade_rate": 12
  },
  "overall": 92.3,
  "grade": "S",
  "grade_desc": "Excellent"
}
```

### 示例 2: 需要改进的 Agent

```json
{
  "efficiency": {
    "completion_rate": 75,
    "gate_pass_rate": 70,
    "block_rate": 25,
    "first_try_rate": 60,
    "throughput": 3.2
  },
  "quality": {
    "console_log": 8,
    "debugger": 3,
    "type_errors": 5,
    "test_pass_rate": 80,
    "build_errors": 2
  },
  "behavior": {
    "state_update_rate": 70,
    "change_tracking_rate": 65,
    "violations": 5
  },
  "autonomy": {
    "autonomy_rate": 72,
    "self_correction_rate": 55,
    "upgrade_rate": 3
  },
  "overall": 71.5,
  "grade": "B",
  "grade_desc": "Satisfactory"
}
```

---

## 相关文档

- [Benchmark README](../../tools/eval-cli/README.md)
- [验证文档](VALIDATION.md)
- [使用指南](../../packages/agent-harness/docs/usage.md)

---

*最后更新: 2026-03-22*
