# Harness State Schema v2

> **版本**: 2.0.0  
> **日期**: 2026-04-30  
> **规范文件**: `core/schema/state.v2.schema.json`

---

## 概述

`state.json` 是 Harness 的核心持久化文件，记录任务状态、检查点、门禁、Memory 和自愈数据。

---

## 快速参考

```bash
# 验证 state.json 是否符合 schema
python3 tools/validator/state-validator.py <project>/harness/feedback/state/state.json

# 导出当前状态
harness state export
```

---

## 字段说明

### 顶层字段

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `_schema` | string | ✅ | 固定值 `harness-state-v2` |
| `version` | string | ✅ | 固定值 `2.0.0` |
| `project` | string | ✅ | 项目名称 |
| `type` | string | | `business` \| `tech` \| `generic` |
| `platform` | string | | 平台标识，如 `nuwax`、`electron` |
| `currentTask` | string/null | | 当前进行中的任务 |
| `taskStatus` | string/null | | `in_progress` \| `completed` \| `blocked` |
| `lastUpdated` | ISO timestamp | | 最后更新时间 |

---

### checkpoints

```json
"checkpoints": {
  "CP0": "completed",
  "CP1": "completed",
  "CP2": "in_progress",
  "CP3": "pending",
  "CP4": "pending"
}
```

| 值 | 说明 |
|----|------|
| `pending` | 未开始 |
| `in_progress` | 进行中 |
| `completed` | 已完成 |
| `failed` | 失败 |
| `skipped` | 跳过 |

---

### gates

```json
"gates": {
  "init": "passed",
  "plan": "passed",
  "exec": "passed",
  "verify": "failed",
  "complete": "pending"
}
```

支持任意额外 key（如项目自定义 gate）。内置 gate：

| Gate | 说明 |
|------|------|
| `init` | CP0 初始化完成 |
| `plan` | CP1 规划通过 |
| `exec` | CP2 执行完成 |
| `verify` | CP3 验证通过 |
| `complete` | CP4 完成 |

---

### healing — CP4 自愈循环

```json
"healing": {
  "enabled": true,
  "maxAttempts": 3,
  "currentAttempt": 2,
  "lastAttempt": "2026-04-30T14:00:00Z",
  "lastError": "lint: unused variable 'x' in foo.ts",
  "retryHistory": [
    {
      "attempt": 1,
      "timestamp": "2026-04-30T13:00:00Z",
      "failedGates": ["lint"],
      "errorSummary": "unused variable 'x' in foo.ts",
      "filesTouched": ["src/foo.ts"],
      "status": "failed"
    }
  ],
  "autoHeal": true
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用自愈 |
| `maxAttempts` | number | 最大尝试次数 (1-10) |
| `currentAttempt` | number | 当前尝试序号 |
| `lastAttempt` | ISO timestamp/null | 上次尝试时间 |
| `lastError` | string/null | 上次失败的摘要 |
| `retryHistory` | array | 每次尝试的记录 |
| `autoHeal` | boolean | 自动进入下次循环 |

**retryHistory item:**

| 字段 | 说明 |
|------|------|
| `attempt` | 尝试序号 |
| `timestamp` | 时间 |
| `failedGates` | 失败的 gate 列表 |
| `errorSummary` | 错误摘要（限 200 字符） |
| `filesTouched` | 尝试修改的文件列表 |
| `status` | `passed` \| `failed` |

---

### memory

```json
"memory": {
  "lastRetrieval": {
    "timestamp": "2026-04-30T10:00:00Z",
    "type": "cp0_init",
    "episodicHits": 3,
    "semanticHits": 5
  },
  "episodicBuffer": [...],
  "semanticCache": {
    "electron": ["禁止直接调用 node_modules"],
    "nuwax": ["sandbox 内完全信任"]
  }
}
```

| 字段 | 说明 |
|------|------|
| `lastRetrieval` | 最近一次检索记录 |
| `episodicBuffer` | 情景经验缓冲（最近任务片段） |
| `semanticCache` | 语义缓存（约束/规范/模式） |

---

### autonomy

```json
"autonomy": {
  "level": 4,
  "requireApprovalFor": ["delete", "network_request"],
  "autoMergeOnCI": false,
  "lastPR": {
    "number": 42,
    "url": "https://github.com/...",
    "branch": "feat/login",
    "mergedAt": "2026-04-29T15:00:00Z"
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `level` | number | 自主等级 (1-9) |
| `requireApprovalFor` | string[] | 需要人类 approve 的操作 |
| `autoMergeOnCI` | boolean | CI 通过后自动合并 |
| `lastPR` | object | 最近一次 PR 信息 |

**L1-L9 定义：**

| 等级 | 行为 |
|------|------|
| L1 | 人类执行 Agent 的修复方案 |
| L2 | Agent 修复，人类 approve |
| L3 | Agent 修复+验证，人类 approve |
| L4 | Agent 开 PR，人类 merge |
| L5 | Agent 开 PR，CI 通过后自动合并 |
| L6+ | 自动处理更复杂的场景 |

---

### metrics

```json
"metrics": {
  "tasksCompleted": 12,
  "tasksBlocked": 1,
  "mcpToolsInvoked": 84,
  "retrievalHits": 23
}
```

---

### recentChanges

最近 10 条变更记录：

```json
"recentChanges": [
  {
    "timestamp": "2026-04-30T14:00:00Z",
    "type": "checkpoint_update",
    "description": "CP3 verify failed"
  }
]
```

---

### taskHistory

最近 20 条已完成任务：

```json
"taskHistory": [
  {
    "task": "implement login API",
    "completedAt": "2026-04-28T10:00:00Z"
  }
]
```

---

### pr

```json
"pr": {
  "number": 42,
  "url": "https://github.com/...",
  "title": "feat: add login API",
  "branch": "feat/login",
  "status": "open",
  "createdAt": "2026-04-29T10:00:00Z",
  "mergedAt": null
}
```

---

## 验证

```bash
# 验证文件
python3 tools/validator/state-validator.py harness/feedback/state/state.json

# 验证并显示详情
python3 tools/validator/state-validator.py harness/feedback/state/state.json --verbose
```

---

## 迁移

从旧版迁移：

```bash
python3 scripts/migrate-schema.py
```

将所有 `harness-feedback-v1`、`harness-core-v1`、`harness-v2` 统一为 `harness-state-v2`。

---

## 与其他文件的关系

```
state.json
  ├─ healing.retryHistory ← 被 heal 命令写入
  ├─ taskHistory        ← 被 update-state.sh done 命令写入
  ├─ memory             ← 被 CP0/C P1 脚本填充
  └─ gates.verify       ← 被 verify 命令更新

memory-retrieval.md ← 定义何时查 state.json
healing-loop.md    ← 定义自愈循环逻辑
autonomy.md         ← 定义 L1-L9 行为规范
```
