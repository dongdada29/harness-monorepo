# 使用示例

## 示例 1: 完整功能开发流程

### 场景
人类要给项目添加用户注册功能。

### 对话

```
👤 给我加上用户注册功能

🤖 /start 用户注册功能

📋 任务确认 (CP1):
请确认任务范围：
- ✅ 后端注册 API
- ✅ 前端注册表单
- ✅ 邮箱验证
- ❌ 不包括：第三方登录（OAuth）

确认开始？

👤 确认，注意使用现有的 validator

🤖 收到，使用现有 validator，开始实现。

[实现代码...]

🤖 /verify

Gate 1: Lint
   └─ npm run lint
   └─ ✅ Passed

Gate 2: Typecheck
   └─ npx tsc --noEmit
   └─ ✅ Passed

Gate 3: Test
   └─ npm test
   └─ ✅ Passed (15 tests)

Gate 4: Build
   └─ npm run build
   └─ ✅ Passed

🎉 All gates passed!

🤖 /review src/services/register.ts

🔍 Review: src/services/register.ts

✅ 通过:
- 错误处理完善
- 有单元测试

❌ 问题:
- [src/services/register.ts:42] [中等] 缺少参数校验

修复中...
✅ 已修复

🤖 /done

✅ 任务完成: 用户注册功能

📁 变更文件:
- src/services/register.ts
- src/components/RegisterForm.tsx
- src/types/auth.ts
- tests/register.test.ts

⏱️ 用时: 25 minutes

📊 状态已更新
```

---

## 示例 2: Bug 修复流程

```
👤 登录按钮点击没反应

🤖 /start 修复登录按钮无响应问题

👤 确认，先看看代码

🤖 收到。

[阅读代码...]

发现问题：onClick={handleLogin} 但 handleLogin 未定义

修复：
- src/components/LoginForm.tsx:42
- onClick={handleLogin} → onClick={handleSubmit}

🤖 /verify

✅ 所有门禁通过

🤖 /done

✅ 任务完成: 修复登录按钮无响应

🔍 根因: onClick 绑定了未定义的函数
```

---

## 示例 3: 阻塞与升级

```
👤 实现文件上传功能

🤖 /start 文件上传功能

[尝试实现...]

🤖 /blocked 遇到技术问题

🚧 任务阻塞: 文件上传功能

原因: 需要接入 S3，但项目未配置 AWS credentials，也没有相关文档。

💡 可能的解决方案:
1. 使用现有的文件存储服务 (lib/storage.ts)
2. 新增 AWS S3 配置 (需要 credentials)
3. 使用 Cloudinary 第三方服务

需要:
- 确认使用哪个方案
- 如果是方案 2，需要提供 AWS credentials

👤 用方案 1，现有的 storage service

🤖 收到，使用 lib/storage.ts 继续实现。
```

---

## 示例 4: 多文件改动（分步执行）

### 场景
需要重构 8 个文件，超过 5 个文件限制。

```
👤 重构整个 auth 模块

🤖 这个任务涉及 8 个文件，超过单次限制。

建议分 3 步：
1. 重构 user 相关 (3 文件)
2. 重构 session 相关 (3 文件)
3. 重构 token 相关 (2 文件)

确认第一步？

👤 可以

🤖 /start 重构 auth 模块 - user 相关

[重写 3 个文件...]

🤖 /verify
✅ 所有门禁通过

🤖 /done

继续第二步？

👤 继续

🤖 /start 重构 auth 模块 - session 相关
...
```

---

## 示例 5: State 状态演进

### 任务开始前
```json
{
  "currentTask": null,
  "taskStatus": "idle",
  "checkpoints": {...},
  "gates": {...}
}
```

### 任务开始后
```json
{
  "currentTask": "用户注册功能",
  "taskStatus": "in_progress",
  "taskStartedAt": "2026-03-21 18:00:00",
  "checkpoints": {
    "CP1": "in_progress",
    "CP2": "pending",
    "CP3": "pending",
    "CP4": "pending",
    "CP5": "pending"
  }
}
```

### 任务完成后
```json
{
  "currentTask": null,
  "taskStatus": "completed",
  "taskCompletedAt": "2026-03-21 18:30:00",
  "recentChanges": [
    {
      "date": "2026-03-21",
      "task": "用户注册功能",
      "status": "completed",
      "duration": 30,
      "by": "agent"
    }
  ],
  "stats": {
    "tasksCompleted": 1,
    "averageTaskDuration": 30
  }
}
```

---

## 示例 6: package.json 配置

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    
    "lint": "eslint src --ext .ts,.tsx --fix",
    "typecheck": "tsc --noEmit",
    
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:integration": "vitest run --config vitest.integration.config.ts",
    "test:e2e": "playwright test",
    
    "verify": "npm run lint && npm run typecheck && npm test && npm run build"
  }
}
```
