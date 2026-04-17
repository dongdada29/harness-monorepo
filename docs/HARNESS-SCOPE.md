# Harness Scope — 边界定义

> **版本**: 1.0.0  
> **日期**: 2026-04-17  
> **目标**: 回答"Harness 管什么、不管什么"这个问题

---

## 1. 核心问题

linlee996 说 Harness = "除了大模型以外的所有辅助和环境构建工程"。  
shyrock2026 的质疑：Harness 缺少一个清晰的边界定义。

这句话太宽泛，需要一张图说清楚。

---

## 2. 边界总览

```
┌─────────────────────────────────────────────────────────────┐
│                        Agent (模型层)                       │
│                                                              │
│   思考 / 决策 / 推理                                         │
│   —— Harness 不干涉这个 ——                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓ 模型输出
┌─────────────────────────────────────────────────────────────┐
│                    Harness (执行环境)                       │
│                                                              │
│  ✓ CP 工作流驱动（CP0→CP1→CP2→CP3→CP4）                     │
│  ✓ 安全门禁（路径/命令/沙箱）                                │
│  ✓ 状态持久化（checkpoints、state.json）                     │
│  ✓ Memory 检索时机（什么时候查、查什么）                     │
│  ✓ Benchmark 评分（量化 Agent 表现）                        │
│  ✓ 自主等级（L1-L9 人类介入边界）                           │
│  ✓ 日志规范（结构化输出）                                   │
│  ✓ Skill 模板（操作过程 + 决策启发 + 规范约束）             │
│                                                              │
│  ✗ 具体业务逻辑                                              │
│  ✗ 代码实现细节                                              │
│  ✗ 运行时错误处理                                            │
│  ✗ 外部 API 调用逻辑                                         │
│  ✗ 用户界面实现                                              │
└─────────────────────────────────────────────────────────────┘
                            ↓ Harness 输出
┌─────────────────────────────────────────────────────────────┐
│                        环境层                                │
│                                                              │
│   文件系统 / Shell / Git / 编辑器                            │
│   —— 这些是 Harness 可以调用的工具 ——                       │
│   —— 但调用的策略由 Harness 定义，调用本身由 Agent 执行 ——  │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Harness 管的七件事

### 3.1 CP 工作流驱动

**管**: 什么时候进入哪个 CP、CP 之间的流转条件

**不管**: 每个 CP 里具体做什么操作

```
CP0 → CP1 → CP2 → CP3 → CP4
 ↑        ↑    ↑    ↑
 │        │    │    └─ Gate: lint → test → build
 │        │    └─ Gate: 验证通过
 │        └─ Gate: 计划被人类 approve
 └─ Gate: state.json 初始化完成
```

### 3.2 安全门禁

**管**: 路径白名单、命令分类（auto-approve/confirm/block）、沙箱规则

**不管**: 具体某个命令执行后返回什么结果

```markdown
# Harness 管
- 路径 ~/workspace/** 和 ~/projects/** 是白名单
- rm -rf 在沙箱内 auto-approve，沙箱外 block
- ~/.ssh/** 永远 block

# Harness 不管
- rm -rf 删除的文件内容是什么
- 删除后业务是否受影响
```

### 3.3 状态持久化

**管**: state.json 的格式、checkpoint 记录时机、Schema 版本

**不管**: 业务层如何解读状态

```json
{
  "_schema": "harness-state-v2",
  "checkpoints": {
    "CP2": { "status": "completed", "timestamp": "..." }
  }
}
```

### 3.4 Memory 检索时机

**管**: 什么时候查、查哪层（Working Context / Episodic / Semantic）

**不管**: 查到什么之后怎么用（那是 Agent 的决策）

| 时机 | Harness 管 | Harness 不管 |
|------|-----------|--------------|
| CP0 INIT | 必须执行 Memory 检索 | 检索结果如何使用 |
| CP1 PLAN | 触发 Semantic 检索加载项目规范 | 规划内容本身 |
| CP2 EXEC | 阻塞时查 Episodic | 如何解决阻塞 |
| CP3 VERIFY | 失败时查同类错误修复记录 | 修复方案 |

参考: `core/harness/feedback/memory-retrieval.md`

### 3.5 Benchmark 评分

**管**: 评分维度、权重、等级定义

**不管**: 具体分怎么算（那是工具的事）

| 维度 | 权重 | Harness 管 | Harness 不管 |
|------|------|-----------|--------------|
| Efficiency | 40% | 目标值定义 | 具体计算公式 |
| Quality | 30% | 目标值定义 | 测试覆盖率怎么算 |
| Behavior | 15% | 目标值定义 | 人力评估细则 |
| Autonomy | 15% | 目标值定义 | L1-L9 行为判定 |

### 3.6 自主等级

**管**: L1-L9 的定义、升级路径、信任边界

**不管**: Agent 在某个等级下具体怎么行动

```
L1: Agent 说"需要这样做"，人类执行
L2: Agent 做，人类 approve
L3: Agent 做+验证，人类 review
L4: Agent 做+验证+PR，人类 merge
L5+: Agent 自主，人类只收到通知
```

### 3.7 日志规范

**管**: 日志格式、级别定义、必须记录的场景

**不管**: 日志内容本身

```typescript
// Harness 管：格式
logger.info('Task completed', {
  taskId: '...',
  duration: 1500,
  filesChanged: ['...'],
});

// Harness 不管：taskId 具体是什么
```

---

## 4. 三层架构中的 Harness 边界

```
┌─────────────────────────────────────────────────────────┐
│                  Business (nuwax / agent-desktop)        │
│                                                          │
│  Harness 边界：业务层可以定制 Skill 模板和约束规则       │
│  但必须通过 Override 机制，不能直接修改 Core            │
└──────────────────────────┬──────────────────────────────┘
                           │ Override
┌──────────────────────────▼──────────────────────────────┐
│                     Core (通用层)                        │
│                                                          │
│  Harness 边界：所有业务和技术栈必须遵守的基础规则        │
│  路径白名单 / 命令分类 / CP 工作流 / Memory 检索时机    │
└──────────────────────────┬──────────────────────────────┘
                           │ Extends
┌──────────────────────────▼──────────────────────────────┐
│                  Tech Stack (技术栈层)                    │
│                                                          │
│  Harness 边界：技术栈特定的工具约束（如 cargo/electron） │
│  Tech 层约束 > Business 层约束 > Core 层                 │
└─────────────────────────────────────────────────────────┘
```

---

## 5. 与其他模块的关系

### 5.1 与 Skills 的关系

```
Skill = Harness 的一部分

Harness 提供：
  + 操作过程（步骤骨架）       → core/harness/base/tasks/*.md
  + 决策启发（分支判断）       → core/harness/feedback/autonomy.md
  + 规范约束（合格标准）       → core/constraints.md

Agent 负责：
  - 具体每一步怎么操作
  - 遇到分支时怎么选
  - 代码怎么写
```

### 5.2 与 MCP Tools 的关系

```
MCP Tools = Harness 的执行工具

Harness 定义：
  + 什么场景用什么工具（Protocol 层）
  + 工具的输入输出规范（mcp/*.md）

MCP 实现：
  - 工具的具体代码
  - 与外部系统的交互
```

### 5.3 与 Memory 的关系

```
Memory = Harness 的持久化层

Harness 定义：
  + 什么时候存（每个 CP 完成时）
  + 存什么格式（state.v2.schema.json）
  + 什么时候查（CP0 INIT / CP1 PLAN / CP2 EXEC / CP3 VERIFY）

Agent 负责：
  - 查到什么之后如何使用
  - 是否采纳检索建议
```

---

## 6. 常见误区

### ❌ 误区 1：Harness 应该管到代码风格

**错**。Harness 只管"有没有通过 lint"，不管"lint 规则是什么"。

lint 规则是 `constraints.md` 里的一个配置项，由项目维护者定义，不是 Harness 核心的一部分。

### ❌ 误区 2：Harness 应该决定用什么技术方案

**错**。技术选型是 Agent 的决策。Harness 只提供"新增依赖需要说明理由"这样的约束，不提供具体方案。

### ❌ 误区 3：Harness 应该捕获并处理所有错误

**错**。运行时错误由应用层处理。Harness 只负责：
1. 记录错误到 state.json
2. 决定是否触发人工介入（autonomy.md L3+）

---

## 7. 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-17 | 1.0.0 | 初始版本，回答"Harness 管什么、不管什么" |
