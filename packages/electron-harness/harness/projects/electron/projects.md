# Electron Harness Project

> Platform: Electron  
> Version: 1.0.0

---

## 概述

Electron + React + Ant Design 项目 Harness。

## 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | Electron |
| 前端 | React + Ant Design |
| 语言 | TypeScript |
| 构建 | electron-builder |

## 命令

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 开发模式 |
| `pnpm build` | 构建 |
| `pnpm typecheck` | 类型检查 |
| `pnpm lint` | Lint |

## Gates

```
pnpm lint → pnpm typecheck → pnpm test → pnpm build
```
