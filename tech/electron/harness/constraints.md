# Electron Tech Harness

> Tech Stack: Electron + React + TypeScript  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Tech Stack

| 技术 | 说明 |
|------|------|
| Electron | 桌面框架 |
| React | UI 框架 |
| TypeScript | 类型系统 |
| electron-builder | 打包工具 |

---

## 2. Commands

### Auto-Approve
```bash
pnpm dev              # 开发模式
pnpm build:renderer   # 构建渲染进程
pnpm typecheck        # 类型检查
```

### Need Confirm
```bash
pnpm install          # 安装依赖
pnpm build:main       # 构建主进程
electron-builder       # 打包
```

### Blocked
```bash
npm install -g        # 全局安装
rm -rf node_modules   # 危险
```

---

## 3. MCP Tools

| 工具 | 说明 |
|------|------|
| `electron IPC` | 进程通信 |
| `electron-store` | 数据存储 |
| `electron-log` | 日志 |
| `electron-builder` | 打包 |

---

## 4. Skills

| Skill | 说明 |
|-------|------|
| `electron-ipc-patterns` | IPC 通信模式 |
| `electron-security` | 安全最佳实践 |
| `electron-packaging` | 打包配置 |

---

## 5. Tests

| 类型 | 工具 |
|------|------|
| 单元测试 | Vitest |
| E2E 测试 | Playwright |
| 覆盖率 | 80%+ |

---

## 6. Gates

```
pnpm typecheck → pnpm build:main → pnpm build:renderer → electron-builder
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Type | `pnpm typecheck` | 0 errors |
| Build Main | `pnpm build:main` | success |
| Build Renderer | `pnpm build:renderer` | success |
| Package | `electron-builder` | .dmg/.exe |
