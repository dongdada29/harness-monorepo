# Web Tech Harness

> Tech Stack: UmiJS + React + Ant Design  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Tech Stack

| 技术 | 说明 |
|------|------|
| React | UI 框架 |
| UmiJS | React 框架 |
| Ant Design | UI 组件库 |
| TypeScript | 类型系统 |

---

## 2. Commands

### Auto-Approve
```bash
pnpm dev          # 开发服务
pnpm build        # 构建
pnpm test         # 测试
pnpm lint         # Lint
```

### Need Confirm
```bash
pnpm install      # 安装依赖
pnpm add <pkg>    # 添加包
git commit         # 提交
```

### Blocked
```bash
npm install -g    # 全局安装
```

---

## 3. MCP Tools

| 工具 | 说明 |
|------|------|
| `web-file-read` | 读取 Web 文件 |
| `web-file-write` | 写入 Web 文件 |
| `react-component` | 生成 React 组件 |
| `antd-use` | Ant Design 组件 |
| `umi-route` | Umi 路由配置 |

---

## 4. Skills

| Skill | 说明 |
|-------|------|
| `react-best-practices` | React 最佳实践 |
| `antd-usage` | Ant Design 使用指南 |
| `umi-patterns` | UmiJS 模式 |

---

## 5. Tests

| 类型 | 工具 |
|------|------|
| 单元测试 | Jest / Vitest |
| 组件测试 | Testing Library |
| E2E 测试 | Playwright |
| 覆盖率 | 80%+ |

---

## 6. Gates

```
pnpm lint → pnpm typecheck → pnpm test → pnpm build
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Lint | `pnpm lint` | 0 errors |
| Type | `pnpm typecheck` | 0 errors |
| Test | `pnpm test` | 80% coverage |
| Build | `pnpm build` | success |
