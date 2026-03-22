# UniApp Tech Harness

> Tech Stack: UniApp + Vue 3 + TypeScript  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Tech Stack

| 技术 | 说明 |
|------|------|
| UniApp | 跨端框架 |
| Vue 3 | UI 框架 |
| TypeScript | 类型系统 |
| Pinia | 状态管理 |

---

## 2. Commands

### Auto-Approve
```bash
pnpm dev:h5           # H5 开发
pnpm build:app         # App 打包
pnpm typecheck         # 类型检查
```

### Need Confirm
```bash
pnpm add <pkg>         # 添加依赖
pnpm install            # 安装依赖
```

### Blocked
```bash
npm install -g           # 全局安装
```

---

## 3. MCP Tools

| 工具 | 说明 |
|------|------|
| `uniapp-page` | 生成页面 |
| `uniapp-component` | 生成组件 |
| `uniapp-api` | API 调用 |
| `uniapp-store` | 状态管理 |

---

## 4. Skills

| Skill | 说明 |
|-------|------|
| `uniapp-platform` | 平台适配 |
| `uniapp-vue3` | Vue 3 特性 |
| `uniapp-typescript` | TS 最佳实践 |

---

## 5. Tests

| 类型 | 工具 |
|------|------|
| 单元测试 | Vitest |
| 组件测试 | Testing Library |
| E2E 测试 | Playwright |

---

## 6. Gates

```
pnpm typecheck → pnpm lint → pnpm test → pnpm build:app
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Type | `pnpm typecheck` | 0 errors |
| Lint | `pnpm lint` | 0 errors |
| Test | `pnpm test` | 80% coverage |
| Build | `pnpm build:app` | success |

---

## 7. Platform Targets

| 平台 | 说明 |
|------|------|
| H5 | Web |
| App | iOS/Android |
| MiniProgram | 微信小程序 |
| UniApp | 全平台 |
