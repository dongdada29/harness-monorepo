# Electron + Ant Design 项目接入指南

> 适用于 Electron + React + Ant Design 技术栈

---

## 1. 项目配置

### package.json scripts

```json
{
  "scripts": {
    "dev": "electron .",
    "dev:renderer": "vite",
    "build": "tsc && vite build && electron-builder",
    "build:renderer": "vite build",
    "lint": "eslint src --ext .ts,.tsx --fix",
    "lint:css": "stylelint \"src/**/*.{css,less}\" --fix",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "verify": "npm run lint && npm run typecheck && npm test && npm run build"
  }
}
```

---

## 2. Electron 特定约束

### 约束文件 (harness/input/constraints.electron.md)

```markdown
## Electron 特定约束

### 主进程规则
- ❌ 主进程不能使用 React 组件
- ❌ 不能在主进程直接操作 DOM
- ❌ IPC 通信必须定义类型

### 渲染进程规则
- ✅ 使用 Ant Design 组件库
- ✅ 遵循 Ant Design 设计规范
- ✅ 组件放在 src/renderer/components/

### 文件结构
```
src/
├── main/           # 主进程
│   ├── index.ts   # 入口
│   ├── ipc/       # IPC 处理
│   └── preload/   # 预加载脚本
├── renderer/       # 渲染进程
│   ├── components/# React 组件
│   ├── pages/     # 页面
│   ├── hooks/     # 自定义 Hooks
│   └── store/     # 状态管理
└── shared/        # 共享类型
```

### IPC 通信规则
- 必须定义 Interface
- 使用 contextBridge 暴露 API
- 禁止使用 remote module
```

---

## 3. 任务模板

### 功能开发模板 (prompts/electron-feature.md)

```markdown
## 功能开发

### 任务描述


### 范围

#### 涉及文件
- src/renderer/pages/
- src/main/

#### 组件
- [ ] 需要新增 Ant Design 组件
- [ ] 需要修改现有组件

#### API
- [ ] 需要新增 IPC 通道
- [ ] 需要修改 preload

### 验收标准

1. 功能正常运行
2. 符合 Ant Design 规范
3. 主/渲染进程通信正常
4. 打包后能正常运行

### 检查清单

- [ ] 代码符合 ESLint
- [ ] TypeScript 无错误
- [ ] 有对应单元测试
- [ ] IPC 类型定义完整
- [ ] 打包测试通过
```

### Bug 修复模板 (prompts/electron-bugfix.md)

```markdown
## Bug 修复

### Bug 信息
- Electron 版本：
- 操作系统：
- 问题类型：主进程 / 渲染进程 / IPC

### 问题描述


### 复现步骤
1.
2.
3.

### 错误日志

**主进程日志：**
```
```

**渲染进程控制台：**
```
```

### 根因分析

```
1.
2.
3.
```

### 修复方案

```typescript
// 修改文件：src/main/index.ts
// 修改内容：
```

### 验证

- [ ] 开发模式正常
- [ ] 打包后正常
- [ ] 无回归问题
```

---

## 4. Electron 质量门禁

```bash
#!/bin/bash
# scripts/verify.electron.sh

set -e

echo "🔍 Running Electron verification..."

# 1. Lint
echo "📝 Linting..."
npm run lint
npm run lint:css

# 2. Typecheck
echo "📦 Type checking..."
npm run typecheck

# 3. Test
echo "🧪 Running tests..."
npm test

# 4. Build renderer
echo "🎨 Building renderer..."
npm run build:renderer

# 5. Package
echo "📦 Packaging..."
npm run build

echo "✅ All Electron gates passed!"
```

---

## 5. 完整工作流示例

### 场景：添加用户管理页面

```
👤 给我加上用户管理页面

🤖 /start 添加用户管理页面

📋 确认任务范围：
- ✅ 新增用户列表页面（Ant Design Table）
- ✅ 新增用户表单弹窗（Ant Design Modal + Form）
- ✅ IPC 通信获取用户数据
- ❌ 不包括：用户CRUD API（后端已完成）

🔍 技术约束：
- 使用 Ant Design 组件
- 遵循项目文件结构
- IPC 类型定义完整

确认开始？

👤 确认

🤖 开始实现...

[实现代码...]

🤖 /verify

Gate 1: Lint ✅
Gate 2: Typecheck ✅
Gate 3: Test ✅ (8 tests)
Gate 4: Build ✅

🤖 /done

✅ 用户管理页面完成
📁 变更：6 个文件
⏱️ 用时：45 分钟
```

---

## 6. Electron 特定命令

| 命令 | 作用 |
|------|------|
| `/dev` | 启动开发模式 |
| `/build` | 打包应用 |
| `/logs main` | 查看主进程日志 |
| `/logs renderer` | 查看渲染进程日志 |
| `/reload` | 热重载渲染进程 |
