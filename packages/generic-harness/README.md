# Generic Harness - 通用项目模板

> 适用于任何技术栈的项目

---

## 技术栈支持

| 类型 | Lint | Type | Test | Build |
|------|------|------|------|-------|
| TS/React | eslint | tsc | vitest | vite build |
| Python | ruff | mypy | pytest | py_compile |
| Go | golangci-lint | go vet | go test | go build |
| Rust | cargo clippy | cargo check | cargo test | cargo build |

---

## 约束规则

### 禁止
- ❌ 不读 state 就开始
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 遇到阻塞不汇报

### 必须
- ✅ 开始前读 state
- ✅ 用 /start 开始
- ✅ 每步 /verify

---

## 文档

- `docs/getting-started.md` - 快速开始
- `docs/setup.md` - 配置指南
- `docs/usage.md` - 使用指南

---

## 使用

```bash
rsync -av packages/generic-harness/ /path/to/project/
```
