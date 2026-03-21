# Todo App Example

> 完整的 harness-monorepo 使用示例

---

## 项目概述

这是一个简单的 TypeScript + React Todo 应用，用于演示 harness-monorepo 的完整工作流。

---

## 功能需求

- ✅ 添加待办事项
- ✅ 标记完成
- ✅ 删除待办事项
- ✅ 过滤（全部/进行中/已完成）
- ✅ 本地存储

---

## 工作流演示

### CP1: 任务确认

```bash
# 开始任务
/start 实现添加待办事项功能

# 查看状态
/state

# 确认范围
"需要实现：输入框、提交按钮、添加逻辑、本地存储"
```

### CP2: 规划分解

```bash
# 分解任务
1. 创建 TodoInput 组件（30 行）
2. 实现 addTodo 函数（10 行）
3. 添加 localStorage 逻辑（20 行）
4. 编写测试（40 行）

预计文件数：4 个
```

### CP3: 执行实现

```bash
# 实现步骤
1. 创建 src/components/TodoInput.tsx
2. 更新 src/hooks/useTodos.ts
3. 更新 src/App.tsx
4. 创建 tests/TodoInput.test.tsx

# 每步验证
/verify
```

### CP4: 质量门禁

```bash
# Gate 1: Lint
npm run lint
✅ 0 errors

# Gate 2: Typecheck
npm run typecheck
✅ 0 errors

# Gate 3: Test
npm test
✅ All tests pass

# Gate 4: Build
npm run build
✅ 0 errors
```

### CP5: 审查完成

```bash
# 自审
/review

# 更新 state.json
{
  "currentTask": "实现添加待办事项功能",
  "taskStatus": "completed",
  "checkpoints": {
    "CP1": "completed",
    "CP2": "completed",
    "CP3": "completed",
    "CP4": "completed",
    "CP5": "completed"
  },
  "gates": {
    "lint": "passed",
    "typecheck": "passed",
    "test": "passed",
    "build": "passed"
  }
}

# 完成
/done
```

---

## 项目结构

```
todo-app/
├── src/
│   ├── components/
│   │   ├── TodoInput.tsx
│   │   ├── TodoList.tsx
│   │   └── TodoItem.tsx
│   ├── hooks/
│   │   └── useTodos.ts
│   ├── types/
│   │   └── todo.ts
│   └── App.tsx
├── tests/
│   ├── TodoInput.test.tsx
│   ├── TodoList.test.tsx
│   └── useTodos.test.ts
├── harness/
│   └── feedback/
│       └── state/
│           └── state.json
├── CLAUDE.md
├── .cursorrules
├── AGENTS.md
└── package.json
```

---

## 使用步骤

### 1. 安装 harness

```bash
cd harness-monorepo
./setup.sh generic /path/to/todo-app
```

### 2. 安装依赖

```bash
cd todo-app
npm install
```

### 3. 启动开发

```bash
npm run dev
```

### 4. 开始使用 harness

```bash
# 启动 Claude Code
claude

# 或 Cursor / Codex

# 开始任务
/start 实现添加待办事项功能
```

---

## 质量标准

### 代码规范

- ✅ 函数长度 < 50 行
- ✅ 文件长度 < 300 行
- ✅ 圈复杂度 < 10
- ✅ TypeScript strict mode
- ✅ 无 any 类型

### 测试覆盖

- ✅ 单元测试覆盖率 > 80%
- ✅ 所有组件有测试
- ✅ 所有 hooks 有测试
- ✅ 边界情况测试

### 文档

- ✅ README 完整
- ✅ 代码注释
- ✅ API 文档（如需要）

---

## 常见问题

### Q: 如何更新状态？

```bash
# 手动更新
vim harness/feedback/state/state.json

# 或使用脚本
./scripts/update-state.sh
```

### Q: 遇到阻塞怎么办？

```bash
/blocked 无法理解需求，需要澄清过滤逻辑
```

### Q: 如何跳过某个门禁？

**A: 不允许跳过门禁。必须通过所有门禁才能继续。**

---

## 相关文档

- [harness-monorepo README](../../README.md)
- [Quick Start](../../QUICKSTART.md)
- [Constraints](../../packages/agent-harness/harness/base/constraints.md)
- [Usage Guide](../../packages/agent-harness/docs/usage.md)

---

*最后更新: 2026-03-22*
