# Nuwax Agent Workflow Skill

> Business: Nuwax AI Agent  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Agent 工作流

### 1.1 CP 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
```

| Checkpoint | 说明 |
|-----------|------|
| CP0 | 初始化 |
| CP1 | 任务规划 |
| CP2 | 执行 |
| CP3 | 验证 |
| CP4 | 完成 |

---

## 2. MCP 集成

### 2.1 MCP 命令

```bash
mcp install @nuwax/agent-core
mcp list
mcp invoke <tool> --args <json>
```

### 2.2 MCP Tools

| 工具 | 说明 |
|------|------|
| `agent-execute` | 执行 Agent 任务 |
| `mcp-stdio` | STDIO 通信 |
| `acp-protocol` | ACP 协议 |

---

## 3. Sandbox 集成

### 3.1 创建沙箱

```ts
const sandbox = await sandboxManager.create({
  type: 'docker',
  workspace: '/tmp/nuwax-agent',
});
```

### 3.2 沙箱配置

```json
{
  "sandbox": {
    "type": "docker",
    "image": "node:20-slim",
    "memory": "2g"
  }
}
```

---

## 4. 状态管理

### 4.1 State 更新

```ts
await state.update({
  checkpoint: 'CP2',
  status: 'in_progress',
});
```

### 4.2 Metrics 上报

```ts
metrics.report({
  tasksCompleted: 1,
  tasksBlocked: 0,
});
```

---

## 5. 权限

| 级别 | 说明 |
|------|------|
| read | 只读操作 |
| write | 写入操作 |
| execute | 命令执行 |
| admin | 完全访问 |
