# Contributing to Agent Harness

感谢你关注 Agent Harness！

## 如何贡献

### 1. 报告问题

通过 GitHub Issues 报告：
- Bug 描述
- 复现步骤
- 预期行为 vs 实际行为
- 环境信息（Node 版本、操作系统等）

### 2. 提交修改

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/xxx`
3. 提交修改：`git commit -m 'feat: xxx'`
4. 推送：`git push origin feature/xxx`
5. 创建 Pull Request

### 3. PR 规范

- PR 标题清晰描述改动
- 包含改动原因
- 关联相关 Issue
- 通过所有 CI 检查

### 4. 代码规范

- 遵循项目已有的代码风格
- 新增功能需要测试
- 更新相关文档

## 项目结构

```
agent-harness/
├── CLAUDE.md              # Claude Code 入口
├── harness/
│   ├── input/            # 输入约束
│   ├── process/          # 过程检查点
│   ├── output/           # 输出质量门禁
│   └── feedback/         # 反馈状态
├── scripts/              # 自动化脚本
├── docs/                 # 文档
├── prompts/              # 任务模板
└── .claude/commands/     # Claude Code 命令
```

## 命令

```bash
# 安装依赖
npm install

# 验证
./scripts/verify.sh

# 状态管理
./scripts/state.sh show
```

## 许可

MIT License
