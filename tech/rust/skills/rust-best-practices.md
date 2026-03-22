# Rust Best Practices Skill

> Tech Stack: Rust + Tauri  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. 错误处理

### 1.1 使用 Result

```rust
// ✅ Good
fn read_file(path: &str) -> Result<String, Error> {
    fs::read_to_string(path)?
}

// ❌ Bad
fn read_file(path: &str) -> String {
    fs::read_to_string(path).unwrap()
}
```

### 1.2 传播错误

```rust
fn get_user(id: i32) -> Result<User, Error> {
    let user = db::find_user(id)?;
    Ok(user)
}
```

---

## 2. 异步编程

### 2.1 Tokio runtime

```rust
#[tokio::main]
async fn main() -> Result<()> {
    Ok(())
}
```

### 2.2 async/await

```rust
async fn fetch_user(id: i32) -> Result<User> {
    let user = db::query_user(id).await?;
    Ok(user)
}
```

---

## 3. 所有权

| 规则 | 说明 |
|------|------|
| 移动语义 | 默认移动 |
| 借用 | 用 `&` 借用 |
| 可变借用 | 用 `&mut` |
| Clone | 需要时显式 Clone |

---

## 4. Cargo.toml

```toml
[dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

[profile.release]
opt-level = 3
lto = true
```

---

## 5. 测试

```rust
#[cfg(test)]
mod tests {
    #[test]
    fn it_works() {
        assert_eq!(2 + 2, 4);
    }
}
```
