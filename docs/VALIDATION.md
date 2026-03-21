# Harness 方案有效性验证

> 如何验证 harness 方案的有效性

---

## 目录

- [验证方法](#验证方法)
- [Benchmark 指标](#benchmark-指标)
- [验证步骤](#验证步骤)
- [预期结果](#预期结果)
- [常见问题](#常见问题)

---

## 验证方法

### 1. 自动化验证脚本

运行自动化验证脚本：

```bash
cd packages/agent-harness
./tests/validate-harness.sh
```

**验证内容**:
- ✅ 子包完整性
- ✅ 示例项目
- ✅ 工具链
- ✅ 文档完整性
- ✅ Benchmark 评分

---

### 2. Benchmark 测试

运行 Benchmark 测试：

```bash
cd packages/agent-harness
./tests/test-benchmark.sh
```

**测试内容**:
- ✅ 基础 Benchmark
- ✅ JSON 输出
- ✅ Markdown 输出
- ✅ 子包 Benchmark
- ✅ 评分系统验证

---

### 3. 手动验证

按照以下步骤手动验证：

#### 步骤 1: 安装 harness

```bash
cd harness-monorepo
./setup.sh generic /tmp/test-project
```

#### 步骤 2: 检查文件

```bash
cd /tmp/test-project
ls -la CLAUDE.md .cursorrules AGENTS.md harness/
```

#### 步骤 3: 查看状态

```bash
./scripts/update-state.sh show
```

#### 步骤 4: 开始任务

```bash
./scripts/update-state.sh start "测试任务"
./scripts/update-state.sh show
```

#### 步骤 5: 运行 Benchmark

```bash
python3 tools/eval-cli/benchmark.py --project /tmp/test-project
```

---

## Benchmark 指标

### 评分维度

| 维度 | 权重 | 指标 |
|------|------|------|
| **Efficiency** | 40% | 任务完成率、Gate 通过率、阻塞率、首次通过率、吞吐量 |
| **Quality** | 30% | console.log、debugger、Type 检查、测试、构建 |
| **Behavior** | 15% | State 更新率、变更追踪、违规数 |
| **Autonomy** | 15% | 自主完成率、自我修正率、升级率 |

### 评分标准

| 分数 | 等级 | 说明 |
|------|------|------|
| S+ >= 95 | World Class | 世界级 |
| S >= 90 | Excellent | 优秀 |
| A+ >= 85 | Outstanding | 杰出 |
| A >= 80 | Very Good | 很好 |
| B+ >= 75 | Good | 好 |
| B >= 70 | Satisfactory | 满意 |
| C >= 60 | Marginal | 及格 |
| D >= 50 | Poor | 差 |
| F < 50 | Fail | 失败 |

### 计算 formula

```python
overall = (
    efficiency_score * 0.40 +
    quality_score * 0.30 +
    behavior_score * 0.15 +
    autonomy_score * 0.15
)
```

---

## 验证步骤

### 1. 准备环境

```bash
# 克隆仓库
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo

# 安装依赖（如需要）
npm install
```

### 2. 运行验证脚本

```bash
# 完整验证
./packages/agent-harness/tests/validate-harness.sh

# Benchmark 测试
./packages/agent-harness/tests/test-benchmark.sh
```

### 3. 查看结果

```bash
# 查看验证报告
cat /tmp/overall_benchmark.json | jq

# 查看详细结果
cat /tmp/benchmark_test.json | jq
```

---

## 预期结果

### 验证通过标准

#### 自动化验证

```
✓ 子包完整性: 所有必需文件存在
✓ 示例项目: 核心文件存在，工作流完整
✓ 工具链: 所有脚本可执行
✓ 文档完整性: 所有文档存在且内容充实
✓ Benchmark: 评分 >= 70 (B)
```

#### Benchmark 评分

```
Overall: >= 70 (B)
Efficiency: >= 70
Quality: >= 70
Behavior: >= 70
Autonomy: >= 70
```

#### 质量评级

```
通过率 >= 95% → S+
通过率 >= 90% → S
通过率 >= 85% → A+
通过率 >= 80% → A
通过率 >= 75% → B+
通过率 >= 70% → B
```

---

## 常见问题

### Q: Benchmark 评分低怎么办？

**A**: 检查以下项目：

1. **Efficiency 低**
   - 检查 state.json 是否更新
   - 检查任务完成率
   - 检查 gate 通过率

2. **Quality 低**
   - 检查代码质量（console.log, debugger）
   - 检查类型定义
   - 检查测试覆盖

3. **Behavior 低**
   - 检查 state 更新频率
   - 检查变更追踪
   - 检查约束违规

4. **Autonomy 低**
   - 检查自主完成率
   - 检查自我修正率

### Q: 如何提高评分？

**A**:

1. **提高 Efficiency**
   - 减少 block 情况
   - 提高首次通过率
   - 增加 throughput

2. **提高 Quality**
   - 移除调试代码
   - 添加类型定义
   - 增加测试覆盖

3. **提高 Behavior**
   - 及时更新 state
   - 记录所有变更
   - 遵守约束

4. **提高 Autonomy**
   - 减少 human intervention
   - 增加自我修正

### Q: 验证脚本失败怎么办？

**A**:

1. **检查依赖**
   ```bash
   which python3 jq
   ```

2. **检查文件路径**
   ```bash
   ls -la packages/agent-harness/tests/
   ```

3. **查看详细错误**
   ```bash
   bash -x ./tests/validate-harness.sh
   ```

---

## 验证报告示例

### 成功示例

```
========================================
  验证报告
========================================

  通过: 45
  失败: 0

✓ 所有验证通过！方案有效！

质量评级:
  A (Very Good)

Benchmark 结果:
  Overall: 82.5
  Efficiency: 85.0
  Quality: 80.0
  Behavior: 82.0
  Autonomy: 81.0
```

### 失败示例

```
========================================
  验证报告
========================================

  通过: 38
  失败: 7

✗ 部分验证失败，请检查

失败项:
  ✗ CLAUDE.md 缺失 (nuwax-harness)
  ✗ benchmark.py 语法错误
  ✗ 示例文件缺失: tests/useTodos.test.ts
```

---

## 下一步

验证通过后，可以：

1. **开始使用**
   ```bash
   ./setup.sh generic /path/to/your/project
   cd /path/to/your/project
   claude  # 或 cursor / codex
   ```

2. **参考示例**
   ```bash
   cd examples/todo-app
   npm install
   npm run dev
   ```

3. **阅读文档**
   - [使用指南](../../packages/agent-harness/docs/usage.md)
   - [故障排查](../../docs/troubleshooting.md)
   - [评估系统](../../tools/eval-cli/README.md)

---

## 相关文档

- [Benchmark README](../../tools/eval-cli/README.md)
- [使用指南](../../packages/agent-harness/docs/usage.md)
- [故障排查](../../docs/troubleshooting.md)

---

*最后更新: 2026-03-22*
