# AGENTS.md - Codex / OpenCode 入口

> Codex 和 OpenCode 启动时自动加载

---

## 立即行动

1. 读取 `harness/feedback/state/state.json`
2. 读取 `harness/base/constraints.md`
3. **Memory 检索**：查询 `harness/feedback/state/state.json` 中的 `taskHistory` 和 `healing.retryHistory`，寻找相似任务和历史修复经验

---

## Memory 检索时机

| 时机 | 做什么 |
|------|--------|
| **CP0 INIT** | 必须检索：加载 `taskHistory`（相似任务）和 `healing.retryHistory`（修复经验） |
| **CP1 PLAN** | 可选：查同类任务的实现方案 |
| **CP2 EXEC 阻塞** | 必须：查 `healing.retryHistory` 中的同类失败和修复记录 |
| **CP3 VERIFY 失败** | 必须：查历史同类错误的修复方式 |

---

## 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
Init   Plan   Exec  Verify  Complete
```

---

## 支持的项目

| 项目 | 约束文件 |
|------|----------|
| Nuwax | `harness/projects/nuwax/constraints.md` |
| Electron | `harness/projects/electron/constraints.md` |
| 通用 | `harness/projects/generic/constraints.md` |

---

## 命令

- `/state` - 显示状态
- `/start <任务>` - 开始任务
- `/verify` - 运行门禁
- `/heal` - 运行 CP4 自愈循环
- `/done` - 完成任务
- `/blocked <原因>` - 报告阻塞

---

## 质量门禁

```
Gate 1: npm run lint       → 0 errors
Gate 2: npm run typecheck → 0 errors
Gate 3: npm test           → all pass
Gate 4: npm run build      → 0 errors
```

---

## CP4 自愈循环

当 `harness verify` 失败时：

```
1. 检查 state.json 的 healing.retryHistory（历史修复经验）
2. 尝试修复失败的 gate
3. 运行: harness heal   # 重新验证
4. 通过 → 继续；失败 → 最多重试 3 次
```

控制命令：
- `harness healing status` — 查看自愈状态和历史
- `harness healing off` — 禁用自愈
