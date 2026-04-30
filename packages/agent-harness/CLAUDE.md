# CLAUDE.md - Agent Harness

> AI 编码 Agent 工程化工作流

---

## 核心原则

1. **输入决定输出** - 结构化任务定义
2. **约束优于自由** - 明确的禁止和必须
3. **反馈创造智能** - 持续的状态追踪 + Memory 检索复用

---

## 立即行动

```
1. cat harness/feedback/state/state.json
   → 关注: taskHistory, healing.retryHistory, checkpoints, autonomy.level
2. cat harness/base/constraints.md
3. cat core/prompts/{feature,bugfix,review}.md  ← 按任务类型选
```

---

## Memory 检索流程 (CP0 INIT)

```
读取 state.json
  ├─ taskHistory[]         → 最近相似任务和解决方案
  ├─ healing.retryHistory[] → 历史修复经验（哪些错、怎么修的）
  └─ memory.episodicBuffer  → 情景经验

如果 taskHistory 有相似任务 → 复用其 resolution
如果 healing.retryHistory 有同类失败 → 复用其修复方案
```

---

## 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
Init   Plan   Exec  Verify  Complete
```

CP0 INIT 必须执行 Memory 检索。CP3 VERIFY 失败后进入 CP4 自愈循环。

---

## 命令

| 命令 | 作用 |
|------|------|
| `harness state show` | 显示状态 |
| `harness state start <task>` | 开始任务 |
| `harness state done` | 完成任务 |
| `harness state blocked <reason>` | 报告阻塞 |
| `harness state gate <name> <status>` | 更新门禁 |
| `harness state cp <CPX> <status>` | 更新检查点 |
| `harness state level <1-9>` | 设置 autonomy level |
| `harness verify` | 运行质量门禁 |
| `harness heal [--dry-run] [--max <n>]` | CP4 自愈循环 |
| `harness healing <on\|off\|status>` | 管理自愈 |
| `harness open-pr -l <level>` | 打开 PR |

---

## 质量门禁

| Gate | 检查 |
|------|------|
| lint | shellcheck / eslint — 0 errors |
| typecheck | tsc --noEmit — 0 errors |
| test | npm test — 全部通过 |
| build | npm run build — 0 errors |

---

## CP4 自愈循环

```
verify 失败
  │
  ├─ healing.enabled === false? → 退出，请求人工
  ├─ autonomy.level < 3?       → 退出，请求人工
  └─ 否则 → 最多重试 3 次
        │
        ├─ attempt 1: 修复 → verify
        ├─ attempt 2: 修复 → verify
        └─ attempt 3: 修复 → verify → 失败则退出
```

---

## Prompt 模板（按任务类型选择）

| 任务 | 模板 |
|------|------|
| 新功能开发 | `core/prompts/feature.md` |
| Bug 修复 | `core/prompts/bugfix.md` |
| Code Review | `core/prompts/review.md` |

---

## Autonomy Levels

| Level | 行为 |
|-------|------|
| L1-L2 | 人类主导，Agent 执行 |
| L3 | Agent 做+验证，人类 approve |
| L4 | Agent 开 PR，人类 merge |
| L5+ | Agent 开 PR，CI 通过后自动 merge |

---

## 详细文档

- `core/constraints.md` - 通用约束
- `core/harness/feedback/memory-retrieval.md` - Memory 检索规范
- `core/harness/feedback/healing-loop.md` - CP4 自愈循环规范
- `core/harness/feedback/autonomy.md` - 自主等级定义
- `core/prompts/feature.md` - 功能开发工作流
- `core/prompts/bugfix.md` - Bug 修复工作流
- `core/prompts/review.md` - Code Review 工作流
- `docs/usage.md` - 使用指南
- `docs/agent-tips.md` - Agent 技巧
