# Electron IPC Patterns Skill

> Tech Stack: Electron + TypeScript  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. IPC 架构

```
Renderer Process ←→ IPC ←→ Main Process
```

| 通信 | 说明 |
|------|------|
| `ipcRenderer.invoke` | 渲染→主进程 |
| `ipcMain.handle` | 主进程处理 |
| `contextBridge` | 安全暴露 API |

---

## 2. 模式

### 2.1 主进程处理

```ts
// main.ts
ipcMain.handle('user:get', async () => {
  return await userService.getUser();
});
```

### 2.2 渲染进程调用

```ts
// preload.ts
contextBridge.exposeInMainWorld('electronAPI', {
  getUser: () => ipcRenderer.invoke('user:get'),
});
```

### 2.3 渲染进程使用

```ts
const user = await window.electronAPI.getUser();
```

---

## 3. 类型定义

```ts
// types/ipc.ts
interface ElectronAPI {
  getUser: () => Promise<User>;
  setUser: (user: User) => Promise<void>;
}
```

---

## 4. 安全规则

| 规则 | 说明 |
|------|------|
| contextBridge | 必须用 |
| nodeIntegration: false | 必须 |
| contextIsolation: true | 必须 |
| sandbox: true | 推荐 |

---

## 5. Channels 命名

```
<domain>:<resource>:<action>

user:get
user:set
file:read
file:write
app:close
```
