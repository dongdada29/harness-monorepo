# Nuwaclaw → Harness-Monorepo 同步报告

> **日期**: 2026-03-23  
> **来源**: nuwaclaw 沙箱项目实战经验  
> **目标**: 同步到 harness-monorepo 作为通用基础

---

## 1. 同步内容

### 1.1 Constraints (已同步)

```markdown
✅ 路径白名单 (Allowed/Blocked paths)
✅ 命令分类 (Auto-approve/Confirm/Block)
✅ 安全机制 (Mistakes/Misfires/Crashes)
✅ 沙箱内完全信任 (Sandbox = Fully Trusted)
```

### 1.2 State Schema (已同步)

```json
✅ _schema 版本标记
✅ checkpoints (CP0-CP5)
✅ memory (taskHistory, patterns)
✅ safety (mode, limits, cost)
✅ recovery (strategies)
✅ metrics (tasks, checkpoints, humanLoop)
```

---

## 2. 核心经验总结

### 2.1 沙箱安全模型

**最重要的决策：沙箱内完全信任**

```
沙箱外 = workspaceOnly = 严格限制
沙箱内 = 完全信任 = 包括 rm -rf
```

**理由：**
- 沙箱提供隔离层
- 误操作不会影响宿主机
- 保持 Agent 开发效率

### 2.2 命令分类

**错误做法：** 禁止所有 rm 命令

**正确做法：** 区分场景

```markdown
# 沙箱外：禁止 rm -rf
# 沙箱内：允许 rm -rf (因为隔离)
```

### 2.3 Checkpoint 系统

**关键：每个 Checkpoint 必须记录**

```json
{
  "status": "completed",
  "timestamp": "2026-03-23T00:00:00Z",
  "duration": 1500,
  "notes": "Task breakdown completed"
}
```

### 2.4 Benchmark 驱动

**使用量化指标推动迭代**

| 维度 | 权重 | 目标 |
|------|------|------|
| Efficiency | 40% | > 90% |
| Quality | 30% | > 95% |
| Behavior | 15% | > 90% |
| Autonomy | 15% | > 85% |

---

## 3. 推荐的 harness-monorepo 更新

### 3.1 更新 Constraints Schema

```markdown
# 建议的 constraints.md 结构

## 1. 核心原则
- Default Deny (默认拒绝)
- 沙箱内信任

## 2. 路径策略
- 白名单 vs 黑名单
- 沙箱边界

## 3. 命令策略
- Auto-approve 列表
- Confirm 列表
- Block 列表
- 沙箱内特殊规则

## 4. 安全机制
- 故障分类
- 恢复策略
- 人工介入

## 5. 成本管理
- Token 限制
- 速率限制
```

### 3.2 更新 State Schema

```json
{
  "_schema": "harness-v2",
  "version": "2.0.0",
  
  "checkpoints": {
    "CP0": { "status": "...", "timestamp": "...", "duration": 0 },
    "CP1": { ... },
    "CP2": { ... },
    "CP3": { ... },
    "CP4": { ... },
    "CP5": { ... }
  },
  
  "memory": {
    "taskHistory": [],
    "patterns": [],
    "learnedActions": []
  },
  
  "safety": {
    "mode": "enforced",
    "sandbox": { "enabled": true },
    "limits": {},
    "cost": {}
  },
  
  "recovery": {
    "enabled": true,
    "strategies": {}
  }
}
```

### 3.3 新增文档

| 文档 | 说明 |
|------|------|
| `SANDBOX-MODEL.md` | 沙箱隔离模型设计 |
| `CHECKPOINT-GUIDE.md` | Checkpoint 使用指南 |
| `BENCHMARK.md` | 如何使用 Benchmark |
| `RECOVERY.md` | 错误恢复策略 |

---

## 4. 实践检验过的模式

### 4.1 成功的模式

| 模式 | 验证结果 |
|------|---------|
| CP1→CP2→CP3→CP4→CP5 | ✅ 清晰的任务流程 |
| Benchmark 量化 | ✅ 推动持续改进 |
| 沙箱隔离 | ✅ 防止破坏性操作 |
| 状态持久化 | ✅ 支持恢复 |

### 4.2 需要避免的

| 模式 | 问题 |
|------|------|
| 禁止所有 rm | ❌ 降低效率 |
| 复杂权限系统 | ❌ 用户体验差 |
| 无 Checkpoint | ❌ 无法恢复 |

---

## 5. 下一步行动

### 5.1 立即同步

- [ ] 更新 `constraints.md` 为 v3 格式
- [ ] 更新 `state.json` 为 v2 schema
- [ ] 添加沙箱内信任模型说明

### 5.2 文档补充

- [ ] 创建 `SANDBOX-MODEL.md`
- [ ] 创建 `CHECKPOINT-GUIDE.md`
- [ ] 更新 `README.md` 包含这些链接

### 5.3 工具增强

- [ ] Benchmark 支持 _schema 解析
- [ ] State 验证工具
- [ ] CP 工作流可视化

---

## 6. 参考

- [nuwaclaw harness](https://github.com/nuwax-ai/nuwaclaw/tree/feat/harness-integration/crates/agent-electron-client/harness)
- [Anthropic: Effective Harnesses](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)
- [OpenAI: Harness Engineering](https://openai.com/index/harness-engineering/)

---

## 7. 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-17 | 1.2.0 | 三阶段完善：HARNESS-SCOPE + Skill三要素 + constraints v4（三层继承+冲突解决） |
| 2026-03-23 | 1.0.0 | 初始版本，从 nuwaclaw 同步 |
