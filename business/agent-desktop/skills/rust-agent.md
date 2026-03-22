# Agent Desktop Skill

> Business: Agent Desktop (Rust + Tauri)  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. 项目结构

```
agent-desktop/
├── src/                  # Rust 源码
├── src-tauri/            # Tauri 配置
├── harness/              # Harness 配置
└── skills/              # Skills
```

---

## 2. Rust 命令

| 命令 | 说明 |
|------|------|
| `cargo build` | 构建 |
| `cargo test` | 测试 |
| `cargo clippy` | Lint |
| `cargo fmt` | 格式化 |

---

## 3. Tauri 命令

```bash
cargo tauri dev         # 开发
cargo tauri build       # 打包
cargo tauri icon        # 生成图标
```

---

## 4. ACP 协议

```rust
#[tauri::command]
async fn execute_agent(
    task: String,
) -> Result<AgentResult, Error> {
    // 调用 Agent Runtime
}
```

---

## 5. MCP 集成

```rust
#[tauri::command]
async fn mcp_invoke(
    tool: String,
    args: Value,
) -> Result<Value, Error> {
    // 调用 MCP 工具
}
```

---

## 6. 状态管理

```rust
#[derive(Default)]
pub struct AppState {
    pub agent: AgentState,
    pub sandbox: SandboxState,
}
```

| 状态 | 说明 |
|------|------|
| AgentState | Agent 运行时状态 |
| SandboxState | 沙箱状态 |
| TaskState | 任务状态 |
