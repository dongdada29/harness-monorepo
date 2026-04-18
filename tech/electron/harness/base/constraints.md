# Tech Constraints - electron

> **版本**: 1.0.0  
> **日期**: 2026-04-18  
> **继承**: `core/constraints.md`

```yaml
_extends: core
_layer: tech
_owner: electron
```

---

## 1. 技术栈特定约束

### 1.1 Electron 安全规则

| 规则 | 说明 | Override Core |
|------|------|---------------|
| **禁止裸 `eval`** | Electron XSS 风险 | `true` |
| **preload 脚本必须沙箱化** | 使用 `contextBridge` 而非直接暴露 | `true` |
| **禁用 `nodeIntegrationInSubframes`** | 安全最佳实践 | `true` |
| **CSP 必须配置** | `Content-Security-Policy` 必须存在 | `true` |

### 1.2 构建规则

| 规则 | 说明 |
|------|------|
| **electron-builder 签名** | macOS 必须签名，Windows 必须签名 |
| **ASAR 打包** | 生产构建必须使用 ASAR |
| **清理 dist** | 每次构建前清理 `dist/` 目录 |

### 1.3 开发规则

| 规则 | 说明 |
|------|------|
| **devtools 调试** | 开发时允许 DevTools，生产禁用 |
| **自动重载** | `electron-reload` 或 `hot-reload` 必须配置 |
| **多窗口同步** | 多窗口场景必须显式管理生命周期 |

---

## 2. Override 声明

以下规则覆盖了 `core/constraints.md` 和 `business/nuwax/harness/base/constraints.md` 中的对应条款：

| 上游条款 | 覆盖内容 | Override 原因 |
|----------|----------|---------------|
| §4.4 命令分类 | `eval` 加入绝对禁止 | Electron XSS 风险 |
| §4.4 命令分类 | `node` 直接执行加入禁止 | 必须通过 electron 入口 |

---

## 3. 冲突解决

当本文件与上游冲突时：
- **本文件优先**（tech > business > core）

---

## 4. 与 Business 层的关系

- Business 层 (`business/nuwax/`) 定义业务逻辑约束
- Tech 层 (`tech/electron/`) 定义技术实现约束
- **Tech 优先**：当 electron 技术要求与业务需求冲突时，以本文件为准

---

## 5. 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-18 | 1.0.0 | 初始版本，从 core/constraints.md 继承 |
