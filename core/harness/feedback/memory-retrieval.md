# Memory Retrieval Specification

> **版本**: 1.0.0  
> **日期**: 2026-04-17  
> **目标**: 给 CP0 初始化提供"查什么、怎么查"的明确规范

---

## 1. 背景问题

当前 `state.json` 只有写入没有检索：
- `taskHistory` 堆着但没人查
- `patterns` 字段存在但没有填充逻辑
- 每次 session 都是"零起点"，历史经验无法复用

---

## 2. 检索时机

| 时机 | 触发条件 | 说明 |
|------|----------|------|
| **CP0_INIT** | 每次任务开始 | 必须执行 Memory 检索 |
| **CP1_PLAN** | 任务规划阶段 | 可选查相似任务 |
| **CP2_EXEC** | 执行阻塞时 | 查历史成功案例 |
| **CP3_VERIFY** | 验证失败时 | 查同类错误的修复记录 |

---

## 3. 检索类型

### 3.1 工作上下文检索 (Working Context)

**目标**: 加载当前任务的上下文

```typescript
interface WorkingContextQuery {
  type: "working_context";
  taskId: string;           // 当前任务 ID
  sessionId: string;         // 当前 session
  includePending: boolean;    // 是否加载 pending 步骤
}
```

**输出**: 
```json
{
  "taskHistory": [...],      // 最近 10 条相关任务
  "completedSteps": [...],  // 当前任务的已完成步骤
  "pendingSteps": [...],    // 当前任务的待处理步骤
  "blockedReason": null     // 或具体的阻塞原因
}
```

### 3.2 情景经验检索 (Episodic Memory)

**目标**: 找到相似的历史任务

```typescript
interface EpisodicQuery {
  type: "episodic";
  keywords: string[];        // 关键词：技术栈 + 错误类型 + 模块名
  limit: 5;                  // 返回最近 5 条
  timeRange?: {
    start: string;           // ISO date
    end: string;
  };
}
```

**匹配优先级**:
1. 相同模块 + 相同错误类型
2. 相同技术栈 + 相似错误
3. 最近 30 天内的任务

**输出**:
```json
{
  "episodes": [
    {
      "taskId": "bugfix-2026-04-10-001",
      "summary": "修复 nuwax-setup wizard 重复点击崩溃",
      "resolution": "加 debounce 300ms",
      "success": true,
      "relevanceScore": 0.95,
      "timestamp": "2026-04-10T14:23:00Z"
    }
  ]
}
```

### 3.3 语义知识检索 (Semantic Memory)

**目标**: 加载技术规范、架构决策、代码规范

```typescript
interface SemanticQuery {
  type: "semantic";
  scope: "project" | "tech_stack" | "business";
  entities: string[];        // 如 ["electron", "mcp", "sandbox"]
}
```

**输出**:
```json
{
  "constraints": [
    "electron-harness: 禁止直接调用 node_modules",
    "nuwax: sandbox 内完全信任"
  ],
  "patterns": [
    "当遇到 IPC timeout，优先检查 channel 是否存在"
  ],
  "rules": [
    "所有 API 调用必须封装到 services/"
  ]
}
```

---

## 4. 检索流程 (CP0 INIT)

```
CP0_START
  │
  ├─→ QUERY_EPISODIC      # 查相似任务 (最近 5 条)
  │     └─→ 如果有相似任务 → 加载 resolution 到 context
  │
  ├─→ QUERY_SEMANTIC      # 加载项目约束和规则
  │     └─→ 追加到 system prompt
  │
  ├─→ LOAD_WORKING_CONTEXT # 加载当前 session 状态
  │     └─→ 如果有 pendingSteps → 设置 blockedReason
  │
  └─→ CP0_COMPLETE
```

### 伪代码

```typescript
async function cp0Init(task: Task): Promise<CP0State> {
  const startTime = Date.now();

  // 1. 情景经验检索
  const episodicResults = await retrieveEpisodic({
    keywords: extractKeywords(task.description),
    limit: 5,
  });

  // 2. 语义知识检索
  const semanticResults = await retrieveSemantic({
    scope: task.business,
    entities: task.techStack,
  });

  // 3. 工作上下文加载
  const workingContext = await loadWorkingContext({
    taskId: task.id,
    sessionId: currentSession.id,
    includePending: true,
  });

  return {
    status: "completed",
    timestamp: new Date().toISOString(),
    duration: Date.now() - startTime,
    retrieved: {
      episodicCount: episodicResults.length,
      semanticCount: semanticResults.length,
      hasContext: workingContext !== null,
    },
    suggestions: episodicResults.map(e => e.resolution),
  };
}
```

---

## 5. State Schema 更新

在 `state.json` 中新增检索结果字段：

```json
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "memory": {
    "lastRetrieval": {
      "timestamp": "2026-04-16T01:45:00Z",
      "type": "cp0_init",
      "episodicHits": 3,
      "semanticHits": 5
    },
    "episodicBuffer": [],
    "semanticCache": {}
  }
}
```

---

## 6. 实施步骤

### Phase 1: 规范定义 (现在)
- [x] 本文档 — Memory 检索规范

### Phase 2: Schema 更新
- [ ] 更新 `state.v1.schema.json` → `state.v2.schema.json`
- [ ] 统一 `_schema` 版本线（消除 harness-core-v1 / v2 并行）

### Phase 3: CP0 集成
- [ ] 在 `scripts/state.sh` 中实现检索逻辑
- [ ] 在 `AGENTS.md` 中添加 Memory 检索 prompt

### Phase 4: 工具实现
- [ ] `tools/cli/memory-retrieval.py` — 检索 CLI
- [ ] `tools/validator/memory-validator.py` — Schema 验证

---

## 7. 与现有文件的关系

```
core/
├── harness/feedback/
│   ├── memory-retrieval.md    ← 本文档
│   ├── logging.md            ← 日志规范
│   ├── autonomy.md           ← 自主等级
│   └── state/state.json      → 待更新 (Schema v2)
│
├── schema/
│   └── state.v1.schema.json  → 待迁移 → state.v2.schema.json
│
└── scripts/
    └── state.sh              → 待更新 (加入检索调用)
```

---

## 8. 参考

- 论文 §3.2: Memory Architecture — Working Context / Episodic Memory / Semantic Memory 三层
- `autonomy.md` L4-L9 的"定期 review"阶段应该调用 Semantic 检索
- `constraints.md` 的规则应该作为 Semantic 检索的结果来源
