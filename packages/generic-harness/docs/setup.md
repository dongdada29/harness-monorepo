# 项目接入指南

## 快速接入（复制到你的项目）

```bash
# 1. 克隆 agent-harness 作为模板
git clone https://github.com/dongdada29/agent-harness.git /tmp/agent-harness

# 2. 复制到你的项目（不包含 .git）
rsync -av --exclude='.git' /tmp/agent-harness/ /你的项目/

# 3. 进入项目
cd /你的项目/

# 4. 设置脚本执行权限
chmod +x scripts/*.sh scripts/pre-commit/*.sh

# 5. 初始化 git（如果没有）
git init
git add .
git commit -m "feat: adopt agent-harness workflow"

# 6. 启动 Claude Code
claude
```

## 配置你的项目

### 1. 更新 package.json scripts

```json
{
  "scripts": {
    "lint": "eslint src --ext .ts,.tsx",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "build": "vite build"
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

### 3. 配置 pre-commit hook（可选）

```bash
# 使用 husky
npx husky install
npx husky add .husky/pre-commit "./scripts/pre-commit/pre-commit.sh"
```

## 目录结构说明

```
harness/
├── input/constraints.md    # 约束规则（必读）
├── process/checkpoints.md # 5 个检查点
├── output/quality-gates.md # 4 个质量门禁
└── feedback/state/
    └── state.json         # 状态追踪（真相来源）
```

## 开始使用

```bash
# 启动 Claude Code
claude

# Claude Code 会自动加载 CLAUDE.md
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `/state` | 查看当前状态 |
| `/start <任务>` | 开始新任务 |
| `/verify` | 运行质量门禁 |
| `/done` | 完成任务 |
| `/blocked <原因>` | 报告阻塞 |

## 常见问题

### Q: 可以只使用部分组件吗？

A: 可以。建议至少使用：
- `CLAUDE.md` - Claude Code 入口
- `harness/input/constraints.md` - 约束规则
- `harness/feedback/state/state.json` - 状态追踪

### Q: 如何自定义约束？

A: 编辑 `harness/input/constraints.md`，根据你的项目需求添加/删除规则。

### Q: 可以集成到现有项目吗？

A: 可以。按照上面的"快速接入"步骤操作，不会影响现有代码。
