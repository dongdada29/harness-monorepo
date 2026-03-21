# Electron Harness - Electron + Ant Design 项目专用

> 适用于 Electron + React + Ant Design 项目

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | React + Electron |
| UI 组件 | Ant Design |
| 通信 | IPC |
| 打包 | electron-builder |

---

## 核心约束

### 禁止
- ❌ 主进程使用 React 组件
- ❌ 主进程直接操作 DOM
- ❌ IPC 不用类型定义
- ❌ 不用 contextBridge

### 必须
- ✅ IPC 通信定义 Interface
- ✅ 使用 contextBridge 暴露 API
- ✅ 主/渲染进程分离
- ✅ 打包前测试运行

---

## 目录规范

```
src/
├── main/           # Electron 主进程
│   ├── index.ts
│   └── ipc/
├── renderer/       # React 渲染进程
│   ├── components/
│   └── pages/
└── shared/         # 共享类型
```

---

## 文档

- `docs/electron-antd-guide.md` - Electron 项目接入指南
- `docs/electron-workflow.md` - 完整工作流示例
- `docs/electron-reference.md` - 配置参考

---

## 使用

```bash
rsync -av packages/electron-harness/ /path/to/electron/
```
