# Electron Harness Skill

> Package: electron-harness  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

Electron + React + Ant Design 项目专用 Harness。

---

## 2. 支持的 Agent

- Claude Code
- Cursor
- OpenCode

---

## 3. 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | Electron |
| 前端 | React + Ant Design |
| 语言 | TypeScript |
| 构建 | electron-builder |

---

## 4. 开发命令

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 开发模式 |
| `pnpm build` | 构建 |
| `pnpm typecheck` | 类型检查 |
| `pnpm lint` | Lint |

---

## 5. 质量门禁

```
pnpm lint   → 0 errors
pnpm typecheck → 0 errors
pnpm test   → all pass
pnpm build  → success
```

---

## 6. 测试

| 类型 | 工具 |
|------|------|
| 单元测试 | Vitest |
| E2E 测试 | Playwright |
| 覆盖率目标 | 80%+ |
