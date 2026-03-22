# Agent Desktop Business Harness

> 业务: agent-desktop  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Business Overview

| 项目 | 说明 |
|------|------|
| **产品** | agent-desktop Agent 桌面应用 |
| **主技术** | Rust + Tauri |
| **核心功能** | Agent Runtime, MCP, ACP 协议 |

---

## 2. Tech Stack

| 组件 | 技术 |
|------|------|
| 桌面 | Tauri + React |
| 核心 | Rust + Tokio |
| Agent | ACP 协议 |
| MCP | MCP Studio |

---

## 3. Commands

### Auto-Approve
```bash
cargo build            # 构建
cargo test            # 测试
cargo check           # 检查
```

### Need Confirm
```bash
cargo add <crate>    # 添加依赖
git commit -m <msg>  # 提交
```

### Blocked
```bash
cargo update         # 更新依赖
rustup update        # 更新 Rust
```

---

## 4. MCP Tools

| 工具 | 说明 |
|------|------|
| `agent-runtime` | Agent 运行时 |
| `mcp-stdio` | STDIO 通信 |
| `acp-protocol` | ACP 协议 |

---

## 5. Skills

| Skill | 说明 |
|-------|------|
| `rust-best-practices` | Rust 最佳实践 |
| `tauri-integration` | Tauri 集成 |
| `acp-protocol` | ACP 协议 |

---

## 6. Gates

```
cargo check → cargo test → cargo build
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Check | `cargo check` | 0 errors |
| Test | `cargo test` | 0 failures |
| Build | `cargo build --release` | success |

---

## 7. 测试方案

| 类型 | 工具 |
|------|------|
| 单元测试 | cargo test |
| 集成测试 | cargo integration-test |
| E2E 测试 | Playwright |
| 覆盖率 | 80%+ |

---

## 8. 项目结构

```
agent-desktop/
├── crates/
│   ├── agent-desktop/      # 主应用
│   └── agent-protocol/     # 协议
├── harness/                # Harness 配置
├── skills/                  # Skills
├── mcp/                   # MCP 工具
└── tests/                  # 测试
```
