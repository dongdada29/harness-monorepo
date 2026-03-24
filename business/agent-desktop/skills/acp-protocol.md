# ACP Protocol Skill

> Business: ACP (Agent Communication Protocol)  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 协议概述

ACP 是 Agent 之间的通信协议，支持：
- 任务分发
- 状态同步
- 结果回传

---

## 2. 消息格式

```json
{
  "type": "task",
  "id": "uuid",
  "from": "agent-1",
  "to": "agent-2",
  "payload": {
    "action": "execute",
    "task": "...",
    "params": {}
  }
}
```

---

## 3. Rust 实现

```rust
use acp_protocol::{Message, Agent};

let msg = Message::new_task("agent-2", task)?;
agent.send(msg).await?;
```

---

## 4. 任务状态

| 状态 | 说明 |
|------|------|
| `pending` | 待处理 |
| `running` | 执行中 |
| `completed` | 已完成 |
| `failed` | 失败 |
| `cancelled` | 已取消 |

---

## 5. 超时配置

```toml
[acp]
timeout = 300  # 5分钟
retry = 3
```

---

## 6. 错误处理

```rust
match result {
    Ok(response) => handle(response),
    Err(AcpError::Timeout) => retry().await?,
    Err(e) => return Err(e),
}
```
