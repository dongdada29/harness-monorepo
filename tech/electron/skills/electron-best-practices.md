# Electron Best Practices Skill

> Tech Stack: Electron + Node.js  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 项目结构

```
electron-app/
├── src/
│   ├── main/           # 主进程
│   ├── renderer/       # 渲染进程
│   ├── preload/        # 预加载脚本
│   └── shared/         # 共享代码
├── harness/            # Harness 配置
└── package.json
```

---

## 2. IPC 通信

### 主进程

```ts
import { ipcMain } from 'electron';

ipcMain.handle('user:get', async () => {
  return await userService.getUser();
});
```

### 预加载

```ts
contextBridge.exposeInMainWorld('electronAPI', {
  getUser: () => ipcRenderer.invoke('user:get'),
});
```

---

## 3. 安全配置

```json
{
  "webPreferences": {
    "nodeIntegration": false,
    "contextIsolation": true,
    "sandbox": true,
    "preload": "preload.js"
  }
}
```

---

## 4. 构建配置

```json
{
  "scripts": {
    "dev": "electron .",
    "build": "electron-builder",
    "pack": "electron-builder --dir"
  }
}
```

---

## 5. 自动更新

```ts
import { autoUpdater } from 'electron-updater';

autoUpdater.on('update-available', () => {
  mainWindow.webContents.send('update-available');
});
```

---

## 6. 性能优化

| 优化项 | 方案 |
|--------|------|
| 懒加载 | 代码分割 |
| 资源缓存 | 静态资源 CDN |
| 进程通信 | 批量 IPC |
| 内存 | 及时释放资源 |
