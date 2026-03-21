# Contributing to Harness

感谢你的贡献！

---

## 如何贡献

### 1. 报告问题

通过 GitHub Issues 报告：
- Bug 描述 + 复现步骤
- 期望 vs 实际行为
- 环境信息

### 2. 提交改进

1. Fork 本仓库
2. 创建分支：`git checkout -b feat/xxx`
3. 提交：`git commit -m 'feat: xxx'`
4. 推送：`git push origin feature/xxx`
5. 创建 Pull Request

### 3. PR 规范

- PR 标题清晰描述改动
- 说明改动原因
- 关联相关 Issue
- 通过 CI 检查

---

## 代码规范

- 遵循现有代码风格
- 新增功能需要测试
- 更新相关文档

---

## Package 结构

每个 Package 应包含：

```
├── CLAUDE.md       # Claude Code 入口
├── .cursorrules   # Cursor 入口
├── harness/       # 工作流配置
│   ├── base/constraints.md
│   ├── feedback/
│   └── projects/
├── scripts/
└── prompts/
```
