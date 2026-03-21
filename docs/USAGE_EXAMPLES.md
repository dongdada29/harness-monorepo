# Harness 使用案例集

本文档提供各种真实场景的使用案例，帮助你快速上手 Harness。

---

## 目录

1. [基础案例：个人项目](#1-基础案例个人项目)
2. [团队案例：多人协作](#2-团队案例多人协作)
3. [CI/CD 案例：自动化流程](#3-cicc-案例自动化流程)
4. [多 Agent 案例：Claude Code + Cursor](#4-多-agent-案例claude-code--cursor)
5. [性能优化案例](#5-性能优化案例)
6. [故障排查案例](#6-故障排查案例)

---

## 1. 基础案例：个人项目

### 场景

你有一个个人 React 项目，想用 Claude Code 来辅助开发。

### 步骤

```bash
# 1. 进入项目目录
cd ~/projects/my-react-app

# 2. 安装 harness
curl -fsSL https://raw.githubusercontent.com/dongdada29/harness-monorepo/main/setup.sh | bash

# 3. 生成的文件结构
# .
# ├── CLAUDE.md          # Claude Code 指令文件
# ├── harness/
# │   ├── base/
# │   │   └── constraints.md
# │   └── feedback/
# │       └── state/
# │           └── state.json
# └── scripts/
#     └── update-state.sh

# 4. 在 Claude Code 中打开项目
claude-code .

# Claude Code 会自动读取 CLAUDE.md，遵循约束和流程
```

### 预期效果

- Claude Code 遵循你的项目规范
- 任务有清晰的 CP1-CP5 流程
- 自动通过 4 Gates 质量检查

---

## 2. 团队案例：多人协作

### 场景

团队有 3 人，使用 Cursor 开发，需要统一工作流。

### 步骤

```bash
# 1. 项目负责人设置 harness
cd ~/projects/team-project
curl -fsSL https://raw.githubusercontent.com/dongdada29/harness-monorepo/main/setup.sh | bash

# 2. 自定义约束
vim harness/base/constraints.md

# 添加团队规范：
# - 必须使用 TypeScript strict mode
# - 测试覆盖率 > 80%
# - 禁止直接 push to main
# - PR 必须经过 review

# 3. 提交到 git
git add CLAUDE.md harness/ scripts/
git commit -m "chore: setup harness for team"
git push

# 4. 团队成员克隆项目
git clone <repo-url>
cd team-project

# 5. 在 Cursor 中打开
cursor .
```

### 团队约定

在 `harness/base/constraints.md` 中添加：

```markdown
## 团队约定

### Git 工作流
- 功能开发：feature/xxx
- Bug 修复：fix/xxx
- 发布：release/vX.X.X

### 代码审查
- 所有 PR 至少 1 人 review
- 测试通过才能 merge

### 提交信息
- feat: 新功能
- fix: 修复
- docs: 文档
- refactor: 重构
```

---

## 3. CI/CD 案例：自动化流程

### 场景

在 GitHub Actions 中自动运行 harness 验证。

### 步骤

```yaml
# .github/workflows/harness-ci.yml
name: Harness CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run 4 Gates
        run: |
          npm run lint
          npm run typecheck
          npm test
          npm run build
      
      - name: Run Benchmark
        run: |
          pip install -r tools/eval-cli/requirements.txt
          python3 tools/eval-cli/benchmark.py --project .
```

### 质量门禁

在 `harness/base/constraints.md` 中添加：

```markdown
## CI/CD 质量门禁

### 必须通过
- [ ] ESLint 无错误
- [ ] TypeScript 编译通过
- [ ] 测试全部通过
- [ ] 构建成功

### 可选
- [ ] Benchmark 评分 > 80
- [ ] 测试覆盖率 > 80%
```

---

## 4. 多 Agent 案例：Claude Code + Cursor

### 场景

你在 Claude Code 中做架构设计，然后在 Cursor 中实现。

### Claude Code 专注

```markdown
# CLAUDE.md 调整

## 角色定义

你是架构师，负责：
- 系统设计
- 技术选型
- 代码审查

## 工作流
1. CP1: 设计方案
2. CP2: 技术评审
3. 不直接写实现代码
```

### Cursor 专注

```markdown
# .cursorrules 调整

## 角色定义

你是实现者，负责：
- 编写代码
- 编写测试
- 修复 bug

## 工作流
1. 读取 Claude Code 的设计文档
2. CP3: 实现
3. CP4: 测试
4. CP5: 发布
```

### 协作流程

```
Claude Code          Cursor
     │                  │
     ├─ CP1: 设计 ──────►│
     │                  ├─ CP3: 实现
     ├─ CP2: 评审 ◄─────┤
     │                  ├─ CP4: 测试
     │                  └─ CP5: 发布
     │◄─────────────────┤
     └─ 确认完成          │
```

---

## 5. 性能优化案例

### 场景

你的项目 benchmark 评分只有 65 分 (C 级)，想提升到 85+ (A 级)。

### 诊断

```bash
# 运行 benchmark 获取详细报告
python3 tools/eval-cli/benchmark.py --project . --output markdown

# 查看瓶颈
```

### 常见问题及解决方案

#### 问题 1：任务完成率低 (60%)

```bash
# 检查 state.json
cat harness/feedback/state/state.json

# 解决：更新状态
./scripts/update-state.sh task_complete "Add user authentication"
```

#### 问题 2：Gate 通过率低

```bash
# 检查失败的 gate
npm run lint        # 修复 lint 错误
npm run typecheck   # 修复类型错误
npm test            # 修复测试
npm run build       # 修复构建错误
```

#### 问题 3：违规项多

```bash
# 检查违规
grep -r "console.log" src/
grep -r "debugger" src/

# 解决：删除调试代码
```

### 优化后

```bash
# 再次运行 benchmark
python3 tools/eval-cli/benchmark.py --project .

# 评分：65 → 87 (A 级) ✅
```

---

## 6. 故障排查案例

### 案例 6.1：state.json 损坏

```bash
# 症状
benchmark.py 报错：Invalid JSON

# 诊断
python3 -c "import json; json.load(open('harness/feedback/state/state.json'))"

# 解决：重新生成
curl -fsSL https://raw.githubusercontent.com/dongdada29/harness-monorepo/main/packages/agent-harness/harness/feedback/state/state.json > harness/feedback/state/state.json
```

### 案例 6.2：脚本权限问题

```bash
# 症状
./scripts/update-state.sh: Permission denied

# 解决
chmod +x scripts/update-state.sh
```

### 案例 6.3：Claude Code 不读取 CLAUDE.md

```bash
# 症状
Claude Code 忽略了约束

# 检查
cat CLAUDE.md  # 确保文件存在

# 解决：确保文件在项目根目录
mv CLAUDE.md ../CLAUDE.md  # 如果在错误位置
```

---

## 更多案例

### Electron 项目

```bash
# 使用 electron-harness
setup.sh --type electron

# 特点：
# - 包含 Electron 特定约束
# - 主进程/渲染进程分离
# - IPC 通信规范
```

### Nuwax Agent 项目

```bash
# 使用 nuwax-harness
setup.sh --type nuwax

# 特点：
# - Agent 特定工作流
# - MCP 包管理
# - 会话持久化
```

### Rust + Tauri 项目

```bash
# 自定义约束
cat >> harness/base/constraints.md << 'EOF'

## Rust 特定约束

### 必须遵守
- [ ] 使用 `cargo clippy` 检查
- [ ] 使用 `cargo fmt` 格式化
- [ ] 单元测试覆盖新功能
- [ ] 文档注释 (///)

### 禁止
- [ ] 使用 `unwrap()` 在生产代码
- [ ] 忽略编译警告
EOF
```

---

## 快速参考

### 常用命令

```bash
# 安装
curl -fsSL https://.../setup.sh | bash

# 更新状态
./scripts/update-state.sh task_start "任务描述"
./scripts/update-state.sh task_complete "任务描述"

# 运行 benchmark
python3 tools/eval-cli/benchmark.py --project .

# 快速验证
./scripts/quick-validate.sh

# 单元测试
npm test
```

### 评分标准

| 分数 | 等级 | 描述 |
|------|------|------|
| 95-100 | S+ | World Class |
| 90-94 | S | Excellent |
| 85-89 | A+ | Outstanding |
| 80-84 | A | Very Good |
| 75-79 | B+ | Good |
| 70-74 | B | Satisfactory |
| 60-69 | C | Marginal |
| <60 | D/F | 需要改进 |

---

*Last updated: 2026-03-22*
