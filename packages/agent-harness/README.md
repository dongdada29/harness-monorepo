# Agent Harness - 通用版

> 适用于 Claude Code / Cursor / Codex / OpenCode

---

## 所属仓库

本 Package 属于 [harness-monorepo](https://github.com/dongdada29/harness-monorepo)

---

## 支持的 Agent

| Agent | 配置文件 |
|-------|----------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| Codex | `AGENTS.md` |
| OpenCode | `AGENTS.md` |

---

## 快速开始

```bash
# 复制到项目
cp CLAUDE.md /你的项目/
rsync -av harness/ /你的项目/
```

---

## 内容

- `CLAUDE.md` - Claude Code 入口
- `.cursorrules` - Cursor 入口
- `AGENTS.md` - Codex/OpenCode 入口
- `harness/` - 工作流配置
  - `base/` - 通用基础
  - `projects/` - 项目模板

---

## 相关

- [harness-monorepo](https://github.com/dongdada29/harness-monorepo)
- [nuwax-harness](https://github.com/dongdada29/nuwax-harness)
- [electron-harness](https://github.com/dongdada29/electron-harness)
