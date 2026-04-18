# Business Constraints - nuwax

> **版本**: 1.0.0  
> **日期**: 2026-04-18  
> **继承**: `core/constraints.md`

```yaml
_extends: core
_layer: business
_owner: nuwax
```

---

## 1. 业务特定约束

### 1.1 Electron 安全规则

| 规则 | 说明 | Override Core |
|------|------|---------------|
| **禁止裸 `eval`** | Electron 环境下 `eval` 可能导致 XSS | `true` |
| **contextBridge 必须显式声明** | 禁止直接暴露 `window.require` | `true` |
| **nodeIntegration 必须为 false** | 除非显式 override，否则永久禁用 | `true` |

### 1.2 MCP 包管理

| 规则 | 说明 |
|------|------|
| **隔离安装** | MCP 包必须安装到项目独立的 node_modules |
| **禁止全局安装** | `npm install -g` 禁止 |
| **版本锁定** | package-lock.json 必须提交 |

### 1.3 Setup Wizard 规则

| 阶段 | 必须验证 |
|------|----------|
| Login | Token 持久化 + 登出后清理 |
| Wizard | 每步必须完成才能进入下一步 |
| 配置 | 默认值必须覆盖所有必需项 |

---

## 2. Override 声明

以下规则覆盖了 `core/constraints.md` 中的对应条款：

| Core 条款 | 覆盖内容 | Override 原因 |
|-----------|----------|---------------|
| §4.4 命令分类 | `eval` 加入绝对禁止 | Electron XSS 风险 |

---

## 3. 冲突解决

当本文件与 `core/constraints.md` 冲突时：
- **本文件优先**（business > core）
- 但 electron 特定的 Tech 层规则仍然优先于本文件（tech > business > core）

---

## 4. 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-18 | 1.0.0 | 初始版本，从 core/constraints.md 继承 |
