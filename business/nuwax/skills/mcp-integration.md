# Nuwax MCP Integration Skill

> Business: Nuwax MCP 集成  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. MCP 架构

```
Agent ←→ MCP Proxy ←→ MCP Tools
         ↓
      STDIO
         ↓
    Native Tools
```

---

## 2. MCP Tools

| 工具 | 说明 |
|------|------|
| `agent-execute` | 执行 Agent 任务 |
| `mcp-stdio` | STDIO 通信 |
| `acp-protocol` | ACP 协议 |
| `gui-agent` | GUI Agent |

---

## 3. 安装 MCP 包

```bash
mcp install @nuwax/agent-core
mcp list
mcp invoke <tool> --args <json>
```

---

## 4. 配置

```json
{
  "mcp": {
    "server": "stdio",
    "command": "npx",
    "args": ["-y", "@nuwax/mcp-stdio-proxy"]
  }
}
```

---

## 5. 状态管理

```ts
interface MCPState {
  connected: boolean;
  tools: string[];
  lastInvoke: string;
}

await state.update({
  checkpoint: 'CP2',
  mcp: { connected: true, tools: ['agent-execute'] },
});
```
