# Quick Start

> 5 分钟快速上手 Harness

---

## Step 1: 选择你的 Agent

| Agent | 配置文件 |
|-------|----------|
| Claude Code | `CLAUDE.md` |
| Cursor | `.cursorrules` |
| Codex/OpenCode | `AGENTS.md` |

---

## Step 2: 安装 Harness

```bash
# 克隆
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo

# 安装（选择项目类型）
./setup.sh nuwax /path/to/your/project
```

---

## Step 3: 开始使用

```bash
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

## 工作流

```
CP1 → CP2 → CP3 → CP4 → CP5
任务确认 → 规划分解 → 执行实现 → 质量门禁 → 审查完成
```

---

## 质量门禁

```bash
# Gate 1: Lint
npm run lint

# Gate 2: Type
npm run typecheck

# Gate 3: Test
npm run test

# Gate 4: Build
npm run build
```

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

## 下一步

- 查看 `docs/usage.md` 详细指南
- 查看 `docs/evaluation.md` 效果评估
- 运行 `python3 tools/eval-cli/benchmark.py` 获得评分
