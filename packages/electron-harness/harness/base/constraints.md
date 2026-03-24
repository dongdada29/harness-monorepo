# Electron Harness Constraints

> Platform: Electron  
> Version: 1.0.0  
> 更新: 2026-03-25

---

## 1. Tech Stack

| 组件 | 技术 |
|------|------|
| 桌面 | Electron |
| 前端 | React + Ant Design |
| 语言 | TypeScript |
| 构建 | electron-builder |

---

## 2. Commands

### Auto-Approve
```bash
pnpm dev              # 开发模式
pnpm build            # 构建
pnpm typecheck        # 类型检查
pnpm lint             # Lint
```

### Need Confirm
```bash
pnpm add <pkg>       # 添加包
git commit -m <msg>   # 提交
```

### Blocked
```bash
npm install -g         # 全局安装
```

---

## 3. Gates

```
pnpm lint → pnpm typecheck → pnpm test → pnpm build
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Lint | `pnpm lint` | 0 errors |
| Typecheck | `pnpm typecheck` | 0 errors |
| Test | `pnpm test` | 0 failures |
| Build | `pnpm build` | success |

---

## 4. Testing

| 类型 | 工具 |
|------|------|
| 单元测试 | Vitest |
| E2E 测试 | Playwright |
| 覆盖率目标 | 80%+ |

---

## 5. MCP Tools

| 工具 | 说明 |
|------|------|
| `electron-dev` | Electron 开发工具 |

---

## 6. Skills

| Skill | 说明 |
|-------|------|
| `electron-best-practices` | Electron 最佳实践 |
| `electron-workflow` | Electron 工作流 |
