# Agent Harness Monorepo

> 所有 Agent 开发工作流的统一管理

---

## Packages

| Package | 说明 | Agent |
|---------|------|-------|
| `agent-harness` | 通用基础版 | Claude Code / Cursor / Codex / OpenCode |
| `nuwax-harness` | Nuwax Agent OS 专用 | Claude Code / Cursor / Codex / OpenCode |
| `electron-harness` | Electron + Ant Design 专用 | Claude Code / Cursor / Codex / OpenCode |
| `generic-harness` | 通用项目模板 | Claude Code / Cursor / Codex / OpenCode |

---

## 快速开始

### 1. 选择 Agent

```bash
# Claude Code
cp packages/agent-harness/CLAUDE.md ./

# Cursor
cp packages/agent-harness/.cursorrules ./

# Codex / OpenCode
cp packages/agent-harness/AGENTS.md ./
```

### 2. 选择项目模板

```bash
# Nuwax Agent OS
rsync -av packages/nuwax-harness/ /path/to/nuwax/

# Electron
rsync -av packages/electron-harness/ /path/to/electron/

# 通用
rsync -av packages/generic-harness/ /path/to/project/
```

---

## Agent 配置文件

每个 Package 都包含：

```
├── CLAUDE.md       # Claude Code
├── .cursorrules   # Cursor
└── AGENTS.md      # Codex / OpenCode
```

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
Gate 4: npm run build    → 0 errors
```

---

## 约束规则

### 通用约束
- ❌ 不读 state.json 就开始
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
├── README.md
├── package.json
├── packages/
│   ├── agent-harness/       # 通用版
│   │   ├── CLAUDE.md
│   │   ├── .cursorrules
│   │   ├── AGENTS.md
│   │   └── harness/
│   │       ├── base/
│   │       └── projects/
│   │
│   ├── nuwax-harness/     # Nuwax 专用
│   │   └── harness/
│   │       └── projects/nuwax/
│   │
│   ├── electron-harness/   # Electron 专用
│   │   └── harness/
│   │       └── projects/electron/
│   │
│   └── generic-harness/    # 通用模板
│       └── harness/
│           └── projects/generic/
```

---

## 使用示例

### Nuwax 项目

```bash
# 克隆
git clone https://github.com/dongdada29/harness-monorepo.git

# 进入目录
cd harness-monorepo

# 复制 Agent 配置
cp packages/agent-harness/CLAUDE.md /path/to/nuwax/

# 复制 Nuwax 专用配置
rsync -av packages/nuwax-harness/ /path/to/nuwax/

# 进入项目
cd /path/to/nuwax

# 启动 Claude Code
claude
```

### Electron 项目

```bash
cp packages/agent-harness/.cursorrules /path/to/electron/
rsync -av packages/electron-harness/ /path/to/electron/
```

---

## GitHub

https://github.com/dongdada29/harness-monorepo

---

## 相关项目

| 项目 | GitHub |
|------|--------|
| agent-harness | github.com/dongdada29/agent-harness |
| nuwax-harness | github.com/dongdada29/nuwax-harness |
| electron-harness | github.com/dongdada29/electron-harness |
