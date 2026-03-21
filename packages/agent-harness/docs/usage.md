# Harness 使用指南

> 从零开始使用 harness-monorepo

---

## 目录

1. [安装](#安装)
2. [配置](#配置)
3. [工作流](#工作流)
4. [最佳实践](#最佳实践)
5. [高级用法](#高级用法)

---

## 安装

### 方式 1: 克隆仓库

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
```

### 方式 2: 下载压缩包

```bash
curl -L https://github.com/dongdada29/harness-monorepo/archive/refs/heads/main.zip -o harness.zip
unzip harness.zip
cd harness-monorepo-main
```

---

## 配置

### 1. 选择项目类型

```bash
# Nuwax Agent OS
./setup.sh nuwax /path/to/nuwax-project

# Electron + Ant Design
./setup.sh electron /path/to/electron-project

# 通用项目
./setup.sh generic /path/to/project
```

### 2. 验证安装

```bash
cd /path/to/your/project

# 检查文件
ls -la CLAUDE.md .cursorrules AGENTS.md harness/

# 检查状态
./scripts/update-state.sh show
```

### 3. 配置 Agent

#### Claude Code

```bash
# CLAUDE.md 已自动创建
# 直接启动即可
claude
```

#### Cursor

```bash
# .cursorrules 已自动创建
# 在 Cursor 中打开项目即可
```

#### Codex/OpenCode

```bash
# AGENTS.md 已自动创建
# 启动 Codex/OpenCode 即可
```

---

## 工作流

### 完整工作流示例

#### CP1: 任务确认

```bash
# 1. 开始任务
/start 添加用户登录功能

# 2. 查看状态
/state

# 3. 确认范围
"需要实现：
- 登录表单组件
- API 调用逻辑
- Token 存储
- 登录状态管理

预计文件数：5 个"
```

#### CP2: 规划分解

```bash
# 分解任务
1. 创建 LoginForm 组件（80 行）
   - src/components/LoginForm.tsx
   - 表单验证逻辑
   
2. 创建 useAuth Hook（60 行）
   - src/hooks/useAuth.ts
   - 登录/登出逻辑
   
3. 创建 API 服务（40 行）
   - src/services/auth.ts
   - HTTP 请求封装
   
4. 更新 App.tsx（20 行）
   - 添加登录路由
   
5. 添加测试（100 行）
   - tests/LoginForm.test.tsx
   - tests/useAuth.test.ts

预计总行数：300 行
预计文件数：5 个（符合约束）"
```

#### CP3: 执行实现

```bash
# 步骤 1: 创建 LoginForm
创建 src/components/LoginForm.tsx

# 验证
/verify

# 步骤 2: 创建 useAuth
创建 src/hooks/useAuth.ts

# 验证
/verify

# ... 继续其他步骤
```

#### CP4: 质量门禁

```bash
# 运行所有门禁
/verify

# 或单独运行
npm run lint       # Gate 1
npm run typecheck  # Gate 2
npm test           # Gate 3
npm run build      # Gate 4
```

#### CP5: 审查完成

```bash
# 1. 自审
/review

# 2. 检查所有门禁通过
/state

# 3. 完成任务
/done
```

---

## 最佳实践

### 1. 任务粒度

```bash
# ✅ 好的任务
/start 添加用户登录功能
/start 修复登录表单验证错误
/start 添加记住密码选项

# ❌ 太大的任务
/start 实现整个用户系统

# ❌ 太小的任务
/start 修改按钮颜色
```

### 2. 文件数量

```bash
# ✅ 符合约束（≤5 个文件）
修改 3 个文件
新增 2 个文件

# ❌ 超过约束
修改 8 个文件  # 需要拆分任务
```

### 3. 验证频率

```bash
# ✅ 每步验证
创建文件 → /verify → 下一步

# ❌ 一次性完成所有工作
创建 5 个文件 → /verify（可能有很多错误）
```

### 4. 阻塞处理

```bash
# ✅ 及时报告
/blocked API 文档缺失，需要澄清登录接口

# ❌ 继续猜测
# 随意假设 API 格式
```

### 5. 状态更新

```bash
# ✅ 保持状态最新
完成步骤 → 立即更新 state.json

# ❌ 忘记更新
# state.json 显示 idle，实际已完成
```

---

## 高级用法

### 1. 自定义约束

编辑 `harness/base/constraints.md`:

```markdown
## 项目特定约束

- 最大函数长度：30 行
- 禁止使用 any
- 必须添加错误处理
```

### 2. 添加项目模板

```bash
# 创建新模板
mkdir -p packages/my-project-harness

# 复制配置
cp -r packages/generic-harness/* packages/my-project-harness/

# 自定义
vim packages/my-project-harness/CLAUDE.md
```

### 3. 集成到 CI/CD

```yaml
# .github/workflows/harness.yml
name: Harness Quality Gates

on: [push, pull_request]

jobs:
  gates:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test
      - run: npm run build
```

### 4. 评估 Agent 效率

```bash
# 运行评估
cd tools/eval-cli
python3 benchmark.py --project /path/to/project

# 查看报告
cat eval-report.json
```

### 5. 团队协作

```bash
# 共享状态（Git）
git add harness/feedback/state/state.json
git commit -m "Update task status"
git push

# 团队成员同步
git pull
```

---

## 常见场景

### 场景 1: Bug 修复

```bash
# 开始
/start 修复登录失败问题

# 定位
检查 API 返回值 → 发现 token 格式错误

# 修复
修改 src/services/auth.ts

# 验证
/verify

# 完成
/done
```

### 场景 2: 功能添加

```bash
# 开始
/start 添加用户头像上传功能

# 规划
1. 创建 AvatarUpload 组件
2. 添加文件上传逻辑
3. 集成到用户设置页
4. 添加测试

# 执行
创建组件 → /verify
添加逻辑 → /verify
集成 → /verify
测试 → /verify

# 完成
/done
```

### 场景 3: 重构

```bash
# 开始
/start 重构状态管理为 Zustand

# 规划
1. 安装依赖
2. 创建 store
3. 迁移组件
4. 删除旧代码

# 执行（小步）
迁移组件 1 → /verify
迁移组件 2 → /verify
...

# 完成
/done
```

---

## 调试技巧

### 1. 查看详细日志

```bash
# 启用详细模式
bash -x ./scripts/update-state.sh show
```

### 2. 手动更新状态

```bash
# 编辑 state.json
vim harness/feedback/state/state.json

# 验证 JSON
jq . harness/feedback/state/state.json
```

### 3. 重置状态

```bash
# 重置所有状态
./scripts/update-state.sh reset
```

---

## 下一步

- 查看 [示例项目](../examples/todo-app)
- 阅读 [故障排查](./troubleshooting.md)
- 学习 [评估系统](../tools/eval-cli/README.md)

---

*最后更新: 2026-03-22*
