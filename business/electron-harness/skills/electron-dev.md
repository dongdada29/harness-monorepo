# Electron Harness Business Skill

> Business: Electron 开发业务  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 业务概述

Electron 桌面应用开发，集成：
- React + Ant Design
- TypeScript
- MCP Tools

---

## 2. 开发命令

| 命令 | 说明 |
|------|------|
| `pnpm dev` | 开发模式 |
| `pnpm build` | 构建 |
| `pnpm typecheck` | 类型检查 |
| `pnpm lint` | Lint |

---

## 3. MCP 集成

```bash
mcp install electron-dev-tools
mcp invoke build --args '{"platform": "mac"}'
```

---

## 4. 构建目标

| 平台 | 格式 |
|------|------|
| macOS | .dmg, .pkg |
| Windows | .exe, .msi |
| Linux | .AppImage, .deb |

---

## 5. 自动更新

```ts
autoUpdater.on('update-available', () => {
  mainWindow.webContents.send('update-available');
});

autoUpdater.checkForUpdatesAndNotify();
```

---

## 6. 测试

| 类型 | 工具 |
|------|------|
| 单元测试 | Vitest |
| E2E 测试 | Playwright |
| 覆盖率 | 80%+ |
