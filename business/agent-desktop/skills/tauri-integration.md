# Agent Desktop Tauri Integration Skill

> Business: Agent Desktop Tauri 集成  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. Tauri 命令

```bash
cargo tauri dev         # 开发模式
cargo tauri build       # 构建
cargo tauri icon        # 生成图标
cargo tauri info        # 信息
```

---

## 2. Rust 命令

| 命令 | 说明 |
|------|------|
| `cargo build` | 编译 |
| `cargo test` | 测试 |
| `cargo clippy` | Lint |
| `cargo fmt` | 格式化 |

---

## 3. IPC 通信

```rust
#[tauri::command]
async fn execute_agent(task: String) -> Result<AgentResult, Error> {
    // 调用 Agent Runtime
}
```

---

## 4. ACP 协议

```rust
use acp_protocol::{Agent, Message};

let agent = Agent::new();
let response = agent.send(task).await?;
```

---

## 5. 构建配置

```json
{
  "build": {
    "devtools": true
  },
  "bundle": {
    "identifier": "com.agent.desktop",
    "targets": "all"
  }
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
