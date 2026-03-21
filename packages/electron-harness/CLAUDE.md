# CLAUDE.md - Agent Harness

> Claude Code 启动时**自动加载**

---

## 什么是 Agent Harness？

一套适用于**所有 AI 编码 Agent**的工程化工作流。

```
Input ──→ Process ──→ Output ──→ Feedback
```

---

## 支持的 Agent

| Agent | 配置文件 |
|-------|----------|
| Claude Code | `CLAUDE.md` (本文件) |
| Cursor | `.cursorrules` |
| Codex | `AGENTS.md` |
| OpenCode | `AGENTS.md` |

---

## 支持的项目类型

| 项目 | 配置目录 |
|------|----------|
| Nuwax Agent OS | `harness/projects/nuwax/` |
| Electron + Ant Design | `harness/projects/electron/` |
| 通用项目 | `harness/projects/generic/` |

---

## 立即行动

```
1. 读取 harness/base/constraints.md
2. 读取 harness/projects/{项目类型}/constraints.md
3. 读取 harness/feedback/state/state.json
```

---

## 工作流

```
CP1 → CP2 → CP3 → CP4 → CP5
任务确认 → 规划分解 → 执行实现 → 质量门禁 → 审查完成
```

---

## 命令

| 命令 | 作用 |
|------|------|
| `/state` | 显示状态 |
| `/start <任务>` | 开始任务 |
| `/verify` | 运行门禁 |
| `/done` | 完成任务 |
| `/blocked <原因>` | 报告阻塞 |

---

## 质量门禁

```
Gate 1: npm run lint       → 0 errors
Gate 2: npm run typecheck → 0 errors
Gate 3: npm test           → all pass
Gate 4: npm run build    → 0 errors
```

---

## 目录结构

```
agent-harness/
├── CLAUDE.md                    # Claude Code 入口
├── .cursorrules                # Cursor 入口
├── AGENTS.md                   # Codex/OpenCode 入口
├── harness/
│   ├── base/                  # 通用基础
│   │   ├── constraints.md     # 通用约束
│   │   └── tasks/             # 通用任务模板
│   ├── universal/              # 通用配置
│   │   └── agents/            # Agent 专用
│   │       ├── claude/
│   │       ├── codex/
│   │       ├── cursor/
│   │       └── opencode/
│   └── projects/               # 项目专用
│       ├── nuwax/             # Nuwax
│       ├── electron/           # Electron
│       └── generic/           # 通用
├── docs/
└── scripts/
```

---

## 快速开始

### 1. 选择项目类型

```bash
# Nuwax
rsync -av harness/projects/nuwax/ /你的nuwax项目/

# Electron
rsync -av harness/projects/electron/ /你的electron项目/

# 通用
rsync -av harness/projects/generic/ /你的项目/
```

### 2. 选择 Agent

```bash
# Claude Code
cp CLAUDE.md /你的项目/

# Cursor
cp .cursorrules /你的项目/

# Codex/OpenCode
cp AGENTS.md /你的项目/
```

### 3. 开始

```bash
claude
```

---

## 详细文档

- `docs/getting-started.md` - 快速开始
- `docs/usage.md` - 详细使用指南
- `harness/base/constraints.md` - 通用约束
- `harness/projects/{项目}/` - 项目专用配置
