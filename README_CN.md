# Agent Harness Monorepo

> 所有 AI 编码 Agent 的工程化工作流统一管理

[English](./README.md) | 中文

---

## 简介

harness-monorepo 是一个统一的 AI 编码 Agent 工作流管理系统，支持多种 Agent（Claude Code、Cursor、Codex）和多种项目类型（Nuwax、Electron、通用）。

### 核心思想

```
1. 输入决定输出 - 结构化任务定义
2. 约束优于自由 - 明确的禁止和必须
3. 反馈创造智能 - 持续的状态追踪
```

---

## 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
```

### 2. 安装到项目

```bash
# Nuwax 项目
./setup.sh nuwax /path/to/nuwax-project

# Electron 项目
./setup.sh electron /path/to/electron-project

# 通用项目
./setup.sh generic /path/to/project
```

### 3. 开始使用

```bash
cd /path/to/your/project

# 启动 Claude Code
claude

# 查看状态
/state

# 开始任务
/start 添加登录功能

# 验证
/verify

# 完成
/done
```

---

## 功能特性

### ✅ 工作流管理

```
CP1 → CP2 → CP3 → CP4 → CP5
任务确认 → 规划分解 → 执行实现 → 质量门禁 → 审查完成
```

### ✅ 质量门禁

```
Gate 1: npm run lint       → 0 errors
Gate 2: npm run typecheck → 0 errors
Gate 3: npm test           → all pass
Gate 4: npm run build     → 0 errors
```

### ✅ 多 Agent 支持

| Agent | 配置文件 |
|-------|----------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| Codex/OpenCode | `AGENTS.md` |

### ✅ 多项目类型

| 类型 | 说明 |
|------|------|
| `nuwax` | Nuwax Agent OS 项目 |
| `electron` | Electron + Ant Design 项目 |
| `generic` | 通用项目 |

---

## 项目结构

```
harness-monorepo/
├── packages/               # 子包
│   ├── agent-harness/     # 通用版
│   ├── nuwax-harness/     # Nuwax 专用
│   ├── electron-harness/  # Electron 专用
│   └── generic-harness/   # 通用模板
├── scripts/               # 工具脚本
├── tools/                 # 评估工具
├── docs/                  # 文档
├── examples/              # 示例项目
└── setup.sh              # 一键安装
```

---

## 约束规则

### 禁止

- ❌ 不读 state 就开始
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 遇到阻塞不汇报
- ❌ 删除文件（除非明确授权）
- ❌ 提交调试代码

### 必须

- ✅ 开始前读 state
- ✅ 用 /start 开始
- ✅ 每步 /verify
- ✅ 遇到阻塞 /blocked
- ✅ 完成 /done

---

## 常用命令

| 命令 | 说明 |
|------|------|
| `/state` | 查看状态 |
| `/start <任务>` | 开始任务 |
| `/verify` | 运行验证 |
| `/done` | 完成任务 |
| `/blocked <原因>` | 报告阻塞 |

---

## 示例项目

查看 [examples/todo-app](./examples/todo-app) 了解完整工作流。

---

## 文档

- [快速开始](./QUICKSTART.md)
- [使用指南](./packages/agent-harness/docs/usage.md)
- [故障排查](./docs/troubleshooting.md)
- [评估系统](./tools/eval-cli/README.md)

---

## 开发

```bash
# 安装依赖
npm install

# 运行测试
npm test

# 检查代码
npm run lint

# 构建文档
npm run build
```

---

## 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](./CONTRIBUTING.md)。

---

## 许可证

MIT License

---

## 相关项目

- [agent-harness](https://github.com/dongdada29/agent-harness)
- [nuwax-harness](https://github.com/dongdada29/nuwax-harness)
- [harness-test](https://github.com/dongdada29/harness-test)

---

*最后更新: 2026-03-22*
