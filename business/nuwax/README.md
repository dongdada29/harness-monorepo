# Nuwax Harness - Nuwax Agent OS 专用

> 适用于 Nuwax Agent OS 项目

---

## 所属仓库

本 Package 属于 [harness-monorepo](https://github.com/dongdada29/harness-monorepo)

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | React 18 + UmiJS Max |
| UI 组件 | Ant Design (优先 ProComponents) |
| 图形引擎 | AntV X6 |
| 状态管理 | Zustand / UmiJS model |
| 通信 | SSE |
| 包管理 | pnpm |

---

## 模块

| 模块 | 说明 |
|------|------|
| AppDev | Web IDE 开发环境 |
| Chat | AI 聊天对话 |
| Workflow | 工作流编排 |
| Agent | Agent 管理 |
| Skills | Skills 市场 |

---

## 内容

- `harness/projects/nuwax/` - Nuwax 专用配置
  - `nuwax.md` - 项目规范
  - `modules.md` - 模块开发规范
  - `workflow-guide.md` - 工作流指南
  - `constraints.md` - 约束规则

---

## 使用

```bash
rsync -av /path/to/nuwax/
```

---

## 相关

- [harness-monorepo](https://github.com/dongdada29/harness-monorepo)
- [agent-harness](https://github.com/dongdada29/agent-harness)
