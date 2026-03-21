# Electron + Ant Design 工作流指南

> 适用于 Electron + React + Ant Design 项目的完整开发流程

---

## 一、需求开发流程

### 阶段 1: 需求分析

```
👤 给我加上用户管理功能（包括列表、新增、编辑、删除）

🤖 需求分析：

1. 涉及范围：
   - 用户列表页面（Ant Design Table）
   - 用户表单弹窗（Ant Design Modal + Form）
   - IPC 通信（获取用户列表、CRUD 操作）
   
2. 技术方案：
   - 前端：React + Ant Design
   - 后端：现有 API（假设已完成）
   - 通信：Electron IPC

3. 任务分解：
   - Task 1: 搭建用户列表页面（3 文件）
   - Task 2: 搭建用户表单弹窗（2 文件）
   - Task 3: 实现 IPC 通信（3 文件）
   - Task 4: 集成测试（1 文件）

4. 预估时间：约 2-3 小时

确认开始第一个任务？
```

### 阶段 2: 任务执行

#### Task 1: 用户列表页面

```
🤖 /start 用户列表页面

CP1: 确认
- ✅ 列表页面组件
- ✅ 表格列定义
- ✅ 分页功能

CP2: 实现
- src/renderer/pages/UserList.tsx
- src/renderer/components/UserTable.tsx
- src/renderer/hooks/useUserList.ts

CP3: /verify ✅

CP4: /review ✅

CP5: /done ✅

下一个任务？
```

### 场景对话示例

```
👤 加上用户管理功能

🤖 收到。让我先了解一下项目结构。

[阅读代码...]

📋 需求理解：
- 用户列表页面（Table）
- 新增/编辑用户（Modal + Form）
- 删除用户（confirm）
- IPC 通信

📦 涉及模块：
- src/renderer/pages/UserManagement/
- src/renderer/components/
- src/main/ipc/
- src/shared/types/

⚠️ 确认：
1. 用户 CRUD API 是否已完成？
2. 数据库 schema 是否已定义？

👤 API 已完成，schema 需要你定义

🤖 明白。开始设计 schema 和实现。

...

✅ 任务完成：用户管理功能
📁 变更：12 个文件
⏱️ 用时：2.5 小时
🧪 验证：全部通过
```

---

## 二、Bug 调试流程

### 快速定位流程

```
👤 用户列表页面打不开

🤖 /start 调试用户列表问题

🔍 快速诊断：

1. 是哪个进程的问题？
   - [ ] 主进程崩溃
   - [ ] 渲染进程崩溃
   - [ ] IPC 通信失败
   
2. 查看错误日志：
   - [ ] 主进程：~/Library/Logs/electron-app.log
   - [ ] 渲染进程：DevTools Console

3. 可能原因：
   - IPC 通道未注册
   - preload 脚本未加载
   - React 组件渲染失败

👤 重现一下问题

🤖 [重现代码...]

🔍 发现问题：
错误：Uncaught TypeError: Cannot read property 'getList' of undefined

原因：window.electronAPI 未正确定义

修复：检查 preload 脚本和 contextBridge 配置

✅ 已修复

🤖 /verify ✅
```

### Bug 调试检查清单

```
## Bug 诊断流程

### 1. 确定问题范围
- [ ] 主进程问题（看主进程日志）
- [ ] 渲染进程问题（看 Console）
- [ ] IPC 通信问题（两边都看）

### 2. 主进程问题排查
```bash
# 查看日志
tail -f ~/Library/Logs/electron-app.log

# 常见问题：
# - IPC 通道未注册
# - 异步操作未正确处理
# - 内存泄漏
```

### 3. 渲染进程问题排查
```
# 打开 DevTools (Ctrl+Shift+I)
# 查看 Console 错误
# 查看 Network 请求
```

### 4. IPC 问题排查
```typescript
// 检查 preload 是否正确暴露
contextBridge.exposeInMainWorld('electronAPI', {...});

// 检查 IPC 通道是否匹配
ipcMain.handle('channel:name', ...)
ipcRenderer.invoke('channel:name', ...)
```

### 5. 常见 Electron Bug 修复

| Bug | 原因 | 修复 |
|-----|------|------|
| white screen | preload 未加载 | 检查 BrowserWindow 配置 |
| IPC undefined | contextBridge 问题 | 检查 preload 路径 |
| 模块未找到 | __dirname 未定义 | 使用 app.getAppPath() |
| 热更新失效 | 主进程不支持热更新 | 仅渲染进程支持 |
```

---

## 三、Electron 特定命令

### 开发命令

| 命令 | 作用 |
|------|------|
| `/dev` | 启动开发模式 |
| `/dev:renderer` | 仅启动渲染进程开发模式 |
| `/logs` | 查看主进程日志 |
| `/reload` | 重新加载渲染进程 |
| `/kill` | 关闭 Electron 进程 |

### 构建命令

| 命令 | 作用 |
|------|------|
| `/build` | 构建生产版本 |
| `/build:dir` | 构建到目录（不打包） |
| `/pack` | 打包但不签名 |

### 调试命令

| 命令 | 作用 |
|------|------|
| `/debug:main` | 打开主进程调试 |
| `/debug:renderer` | 打开渲染进程 DevTools |
| `/console` | 打开 Electron 控制台 |

---

## 四、Electron 质量门禁

### verify.electron.sh

```bash
#!/bin/bash
# Electron 专用验证脚本

set -e

echo "🔍 Electron Verification..."

# 1. Lint
echo "📝 Linting..."
npm run lint
npm run lint:css

# 2. Typecheck
echo "📦 Type checking..."
npm run typecheck

# 3. Test
echo "🧪 Testing..."
npm test

# 4. Build renderer
echo "🎨 Building renderer..."
npm run build:renderer

# 5. Verify main process
echo "⚡ Checking main process..."
node -e "require('./dist/main/index.js')" 2>/dev/null && echo "Main process OK"

# 6. Package
echo "📦 Packaging..."
npm run build

echo "✅ All Electron gates passed!"
```

---

## 五、项目结构规范

```
electron-app/
├── src/
│   ├── main/                    # Electron 主进程
│   │   ├── index.ts           # 入口
│   │   ├── ipc/               # IPC 处理
│   │   │   ├── index.ts       # 注册所有 handler
│   │   │   ├── user.ts        # 用户相关 IPC
│   │   │   └── channels.ts    # 通道常量
│   │   └── preload/
│   │       └── index.ts        # preload 脚本
│   │
│   ├── renderer/               # React 渲染进程
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   ├── pages/              # 页面
│   │   │   └── UserManagement/
│   │   │       ├── index.tsx
│   │   │       └── components/
│   │   │           ├── UserTable.tsx
│   │   │           └── UserModal.tsx
│   │   ├── components/         # 通用组件
│   │   ├── hooks/              # 自定义 Hooks
│   │   │   └── useUserList.ts
│   │   └── store/              # 状态管理
│   │
│   └── shared/                  # 共享代码
│       ├── types/              # 类型定义
│       │   └── user.ts
│       └── constants/         # 常量
│
├── electron-builder.json
├── vite.config.ts
├── tsconfig.json
└── package.json
```

---

## 六、Ant Design 组件使用规范

### 组件选择

| 功能 | 推荐组件 |
|------|----------|
| 表格列表 | Table + Pagination |
| 表单弹窗 | Modal + Form |
| 确认操作 | Modal.confirm() |
| 消息提示 | message.success/error |
| 下拉选择 | Select |
| 日期选择 | DatePicker |
| 表单验证 | Form.useForm() + rules |

### 常见问题

```
❌ 错误：Form.create() is deprecated
✅ 解决：使用 useForm hook

❌ 错误：Modal inside Table
✅ 解决：在 Table row 上使用 Button，在组件外部渲染 Modal

❌ 错误：Table 样式问题
✅ 解决：使用 Ant Design 的 size 属性，检查 CSS 优先级

❌ 错误：表单提交两次
✅ 解决：使用 htmlType="submit" 和 onFinish，不要同时用 onClick
```
