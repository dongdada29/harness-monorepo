# Nuwax Business Harness

> 业务: Nuwax AI Agent 平台  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Business Overview

| 项目 | 说明 |
|------|------|
| **产品** | AI Agent 桌面客户端 |
| **主技术** | Electron + Rust |
| **核心功能** | Agent Runtime, MCP, ACP 协议 |

---

## 2. Tech Stack

| 组件 | 技术 |
|------|------|
| 桌面 | Electron |
| 核心 | Rust + Tauri |
| Agent | ACP 协议 |
| MCP | MCP Studio |
| AI | Claude / GLM / MiniMax |

---

## 3. Commands

### Auto-Approve
```bash
pnpm dev              # 开发模式
pnpm build            # 构建
pnpm typecheck        # 类型检查
```

### Need Confirm
```bash
pnpm add <pkg>       # 添加包
git commit -m <msg>   # 提交
```

### Blocked
```bash
npm install -g         # 全局安装
```

---

## 4. MCP Tools

| 工具 | 说明 |
|------|------|
| `agent-runtime` | Agent 运行时 |
| `mcp-stdio` | STDIO 通信 |
| `acp-protocol` | ACP 协议 |
| `gui-agent` | GUI Agent 集成 |

---

## 5. Skills

| Skill | 说明 |
|-------|------|
| `agent-workflow` | Agent 工作流 |
| `mcp-integration` | MCP 集成 |
| `acp-protocol` | ACP 协议 |
| `electron-dev` | Electron 开发 |

---

## 6. Gates

```
pnpm typecheck → pnpm build → electron-builder
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Type | `pnpm typecheck` | 0 errors |
| Build | `pnpm build` | success |
| Package | `electron-builder` | .dmg/.exe |

---

## 7. 测试方案

| 类型 | 工具 |
|------|------|
| 单元测试 | Vitest |
| 集成测试 | Playwright |
| E2E 测试 | Playwright |
| 覆盖率 | 80%+ |

---

## 8. 项目结构

```
nuwax/
├── crates/
│   ├── agent-electron-client/   # Electron 客户端
│   └── nuwax-mcp-stdio-proxy/   # MCP 代理
├── harness/                      # Harness 配置
├── skills/                        # Skills
├── mcp/                         # MCP 工具
└── tests/                        # 测试
```
