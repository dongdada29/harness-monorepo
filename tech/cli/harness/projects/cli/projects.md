# CLI Tech Project

> Platform: CLI  
> Version: 1.0.0

---

## 概述

CLI 技术栈项目 Harness。

## 技术栈

| 组件 | 技术 |
|------|------|
| 框架 | Node.js / Commander |
| 语言 | TypeScript |
| 构建 | pkg / ncc |

## 命令

| 命令 | 说明 |
|------|------|
| `npm run dev` | 开发 |
| `npm run build` | 构建 |
| `npm test` | 测试 |

## Gates

```
npm run lint → npm run typecheck → npm test → npm run build
```
