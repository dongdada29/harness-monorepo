# Nuwax Harness Skill

> Package: nuwax-harness  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

Nuwax Agent OS 专用 Harness，集成 MCP Studio。

---

## 2. 支持的 Agent

- Nuwax Agent
- MCP Studio Tools

---

## 3. 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
初始化 → 任务解析 → MCP 调用 → 验证 → 完成
```

---

## 4. MCP Tools

| 工具 | 说明 |
|------|------|
| `agent-runtime` | Agent 运行时 |
| `mcp-stdio` | STDIO 通信 |
| `acp-protocol` | ACP 协议 |

---

## 5. 约束规则

```json
{
  "autoApprove": ["pnpm dev", "pnpm build", "pnpm typecheck"],
  "needConfirm": ["pnpm add", "git commit"],
  "blocked": ["npm install -g"]
}
```

---

## 6. Sandbox 配置

```json
{
  "sandbox": {
    "type": "docker",
    "image": "node:20-slim",
    "memory": "2g"
  }
}
```
