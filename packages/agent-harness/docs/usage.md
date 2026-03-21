# Agent Harness 使用指南

> 让 Claude Code 遵循工程化工作流

---

## 第一步：接入项目

### 已有项目

```bash
# 克隆到临时目录
git clone https://github.com/dongdada29/agent-harness.git /tmp/agent-harness

# 复制到你的项目（排除 .git）
rsync -av --exclude='.git' /tmp/agent-harness/ /你的项目/

cd /你的项目/

# 设置脚本执行权限
chmod +x scripts/*.sh scripts/pre-commit/*.sh

# 初始化
git init
git add .
git commit -m "feat: adopt agent-harness workflow"

# 启动 Claude Code
claude
```

### 新项目

```bash
# 创建项目后直接克隆
git clone https://github.com/dongdada29/agent-harness.git /你的新项目
cd /你的新项目/

# 按提示配置 package.json 和 state.json
```

---

## 第二步：配置项目

### 1. 更新 package.json scripts

```json
{
  "scripts": {
    "lint": "eslint src --ext .ts,.tsx",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "build": "vite build",
    "verify": "npm run lint && npm run typecheck && npm test && npm run build"
  }
}
```

### 2. 更新 state.json

```json
{
  "project": "你的项目名",
  "version": "1.0.0"
}
```

---

## 第三步：日常使用

### 启动

```bash
claude
# Claude Code 会自动加载 CLAUDE.md
```

### 命令速查

| 命令 | 作用 |
|------|------|
| `/state` | 查看当前项目状态 |
| `/start <任务>` | 开始一个新任务 |
| `/verify` | 运行质量门禁（lint + typecheck + test + build） |
| `/test` | 运行测试 |
| `/review <文件>` | 代码审查 |
| `/done` | 完成任务 |
| `/blocked <原因>` | 报告阻塞 |
| `/history` | 查看历史 |

---

## 完整工作流

### 场景：添加新功能

```
👤 给我加上用户注册功能

🤖 /state
📋 查看当前状态...

🤖 /start 用户注册功能

CP1: 请确认任务范围
- ✅ 后端注册 API
- ✅ 前端注册表单  
- ✅ 数据库 schema
- ❌ 不包括：邮箱验证

确认开始？

👤 确认，开始吧

🤖 开始实现...

[写代码...]

🤖 /verify
🔍 Gate 1: Lint ✅
🔍 Gate 2: Typecheck ✅
🔍 Gate 3: Test ✅ (12 tests)
🔍 Gate 4: Build ✅

🤖 /review src/services/register.ts
🔍 无严重问题

👤 /review
🔍 建议：加个 loading state

🤖 收到，添加中...

🤖 /verify ✅

🤖 /done

✅ 任务完成：用户注册功能
📁 变更：4 个文件
⏱️ 用时：25 分钟
```

---

### 场景：Bug 修复

```
👤 登录按钮点击没反应

🤖 /start 修复登录按钮问题

👤 确认，先看看代码

🤖 [阅读代码...]

🔍 发现：onClick={handleLogin} 但函数名是 handleSubmit

🤖 修复：src/components/LoginForm.tsx:42

🤖 /verify ✅

🤖 /done

✅ Bug 已修复
```

---

### 场景：遇到阻塞

```
👤 实现文件上传功能

🤖 /start 文件上传功能

[尝试实现...]

🤖 /blocked 缺少 AWS 配置

🚧 阻塞原因：
- 需要 S3 credentials
- 没有文档

💡 解决方案：
1. 使用现有 storage service
2. 新增 AWS 配置（需要 credentials）

👤 用方案 1

🤖 收到，继续...
```

---

## 质量门禁详解

### /verify 执行顺序

```
Gate 1: npm run lint       → 0 errors
    ↓
Gate 2: npx tsc --noEmit  → 0 errors  
    ↓
Gate 3: npm test           → all pass
    ↓
Gate 4: npm run build      → 0 errors
```

### 失败处理

```
Gate 失败 → 停在当前 Gate → 修复 → 重新 /verify
```

常见修复：
```bash
# Lint 错误
npm run lint -- --fix

# Type 错误
# 检查类型定义

# Test 失败
npm test  # 查看具体失败用例

# Build 失败
# 检查导入和配置
```

---

## 约束规则

### 绝对禁止

- ❌ 不读 state.json 就开始
- ❌ 不确认任务范围
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 不更新 state 就结束
- ❌ 遇到阻塞不汇报

### 必须执行

- ✅ 开始前 `/state`
- ✅ 用 `/start` 开始
- ✅ 每步 `/verify`
- ✅ 完成 `/done`
- ✅ 阻塞 `/blocked`

---

## 状态追踪

### state.json 示例

```json
{
  "project": "my-app",
  "currentTask": "用户注册功能",
  "taskStatus": "in_progress",
  "checkpoints": {
    "CP1": "passed",
    "CP2": "passed",
    "CP3": "passed",
    "CP4": "in_progress",
    "CP5": "pending"
  },
  "gates": {
    "lint": "passed",
    "typecheck": "passed",
    "test": "passed",
    "build": "pending"
  }
}
```

---

## 最佳实践

### 1. 小步提交

不要一次做太多。每个 commit 应该：
- 完成一个独立功能点
- 通过 /verify
- 有清晰的 commit message

### 2. 频繁同步

- 每次完成用 `/done`
- 人类定期 review state.json
- 阻塞立即汇报

### 3. 定期复盘

查看 `/history`，分析：
- 哪些任务耗时长
- 哪些地方容易出问题
- 如何改进流程

---

## 常见问题

### Q: 可以跳过某些 Gate 吗？

A: 原则上不行。特殊情况需要人类明确授权，并在 commit message 注明。

### Q: 5 个文件的限制太严格？

A: 可以分成多步。比如 8 个文件分成：
- Step 1: 重构 A 模块 (3 文件)
- Step 2: 重构 B 模块 (3 文件)
- Step 3: 重构 C 模块 (2 文件)

### Q: 不想用某些命令？

A: 可以禁用。删除 `.claude/commands/` 下的对应 .md 文件即可。

### Q: 如何自定义约束？

A: 编辑 `harness/input/constraints.md`，根据你的项目需求调整。
