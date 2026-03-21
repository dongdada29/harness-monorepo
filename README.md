# Agent Harness Monorepo

> 所有 AI 编码 Agent 的工程化工作流统一管理

---

## 一站式安装

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
./setup.sh nuwax /path/to/project
```

---

## 支持的 Package

| Package | 说明 | Agent |
|---------|------|-------|
| **nuwax-harness** | Nuwax Agent OS 专用 | Claude Code / Cursor / Codex / OpenCode |
| **electron-harness** | Electron + Ant Design 专用 | Claude Code / Cursor / Codex / OpenCode |
| **generic-harness** | 通用项目模板 | Claude Code / Cursor / Codex / OpenCode |

---

## 快速开始

### 1. 选择项目类型

```bash
./setup.sh nuwax /path/to/project     # Nuwax 项目
./setup.sh electron /path/to/project # Electron 项目
./setup.sh generic /path/to/project  # 通用项目
```

### 2. 检查配置

```bash
./scripts/check.sh /path/to/project
```

### 3. 开始使用

```bash
cd /path/to/project
claude  # Claude Code
# 或打开 Cursor / Codex
```

---

## 脚本工具

| 脚本 | 功能 |
|------|------|
| `./setup.sh <type> <dir>` | 一键安装 |
| `./scripts/check.sh <dir>` | 检查配置完整性 |
| `./scripts/list.sh` | 列出所有 Package |
| `./scripts/init.sh <type> <dir>` | 初始化项目 |

---

## Agent 支持

| Agent | 配置文件 |
|-------|----------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| Codex | `AGENTS.md` |
| OpenCode | `AGENTS.md` |

---

## 工作流

```
CP1 → CP2 → CP3 → CP4 → CP5
任务确认 → 规划分解 → 执行实现 → 质量门禁 → 审查完成
```

---

## 质量门禁

```
Gate 1: npm run lint       → 0 errors
Gate 2: npm run typecheck → 0 errors
Gate 3: npm test           → all pass
Gate 4: npm run build     → 0 errors
```

---

## 约束规则

### 禁止
- ❌ 不读 state 就开始
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 遇到阻塞不汇报

### 必须
- ✅ 开始前读 state
- ✅ 用 /start 开始
- ✅ 每步 /verify

---

## 目录结构

```
harness-monorepo/
├── setup.sh                      # 一键安装脚本
├── scripts/
│   ├── check.sh                # 配置检查
│   ├── list.sh                  # Package 列表
│   └── init.sh                  # 初始化
└── packages/
    ├── nuwax-harness/         # Nuwax 专用
    ├── electron-harness/       # Electron 专用
    └── generic-harness/         # 通用模板
```

---

## GitHub

https://github.com/dongdada29/harness-monorepo

---

## 相关项目

- [harness-monorepo](https://github.com/dongdada29/harness-monorepo)
- [agent-harness](https://github.com/dongdada29/agent-harness)
- [nuwax-harness](https://github.com/dongdada29/nuwax-harness)
