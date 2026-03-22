# Rust Tech Harness

> Tech Stack: Rust + Tauri + Tokio  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Tech Stack

| 技术 | 说明 |
|------|------|
| Rust | 系统编程 |
| Tauri | 桌面框架 |
| Tokio | 异步运行时 |
| Cargo | 包管理 |

---

## 2. Commands

### Auto-Approve
```bash
cargo check          # 检查
cargo build          # 构建
cargo test           # 测试
cargo clippy         # Lint
```

### Need Confirm
```bash
cargo add <crate>    # 添加依赖
cargo run            # 运行
```

### Blocked
```bash
cargo update         # 更新依赖
rustup update        # 更新 Rust
```

---

## 3. MCP Tools

| 工具 | 说明 |
|------|------|
| `cargo-build` | 构建项目 |
| `cargo-test` | 运行测试 |
| `cargo-clippy` | Lint |
| `tauri-dev` | Tauri 开发 |

---

## 4. Gates

```
cargo check → cargo test → cargo build
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Check | `cargo check` | 0 errors |
| Test | `cargo test` | 0 failures |
| Clippy | `cargo clippy` | 0 warnings |
| Build | `cargo build --release` | success |
