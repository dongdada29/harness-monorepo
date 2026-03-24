# Nuwax MCP Tools

> MCP Tools 文档  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

MCP (Model Context Protocol) Tools 是 Nuwax Agent 的核心工具集。

---

## 2. 工具列表

| 工具 | 说明 |
|------|------|
| `agent-runtime` | Agent 运行时 |
| `mcp-stdio` | STDIO 通信 |
| `acp-protocol` | ACP 协议 |
| `gui-agent` | GUI Agent |

---

## 3. agent-runtime

### 功能
- 创建/管理 Agent 会话
- 执行任务
- 获取结果

### 使用

```bash
mcp invoke agent-runtime.create --args '{"type": "claude"}'
mcp invoke agent-runtime.execute --args '{"session": "xxx", "task": "..."}'
```

---

## 4. mcp-stdio

### 功能
- STDIO 通信
- 命令执行
- 进程管理

### 使用

```bash
mcp invoke mcp-stdio.run --args '{"command": "pnpm dev"}'
mcp invoke mcp-stdio.stop --args '{"pid": 1234}'
```

---

## 5. acp-protocol

### 功能
- Agent 间通信
- 任务分发
- 状态同步

### 使用

```bash
mcp invoke acp-protocol.send --args '{"to": "agent-2", "message": "..."}'
mcp invoke acp-protocol.sync --args '{"state": "..."}'
```

---

## 6. gui-agent

### 功能
- GUI 自动化
- 截图分析
- 操作执行

### 使用

```bash
mcp invoke gui-agent.screenshot --args '{}'
mcp invoke gui-agent.click --args '{"x": 100, "y": 200}'
```

---

## 7. 配置

```json
{
  "mcp": {
    "server": "stdio",
    "command": "npx",
    "args": ["-y", "@nuwax/mcp-stdio-proxy"],
    "env": {
      "DEBUG": "false"
    }
  }
}
```
