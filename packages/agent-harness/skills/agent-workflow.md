# Agent Harness Universal Skill

> Package: agent-harness  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 支持的 Agent

| Agent | 说明 |
|-------|------|
| Claude Code | Anthropic |
| Cursor | AI IDE |
| Codex | OpenAI |
| OpenCode | 通用 |
| Copilot | GitHub |

---

## 2. 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
初始化 → 规划 → 执行 → 验证 → 完成
```

---

## 3. 命令

| 命令 | Agent | 说明 |
|------|-------|------|
| `/start` | All | 开始任务 |
| `/verify` | All | 验证实现 |
| `/checkpoint` | All | 保存检查点 |
| `/review` | All | 代码审查 |

---

## 4. 约束规则

### 禁止
- ❌ 不读 state 就开始
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件

### 必须
- ✅ 开始前读 state
- ✅ 每步 /verify
- ✅ 更新 checkpoint

---

## 5. 质量门禁

| Gate | 检查项 |
|------|--------|
| Gate 1 | Lint 通过 |
| Gate 2 | Typecheck 通过 |
| Gate 3 | 测试通过 |
| Gate 4 | 构建成功 |

---

## 6. Benchmark

```bash
benchmark.py --project .
# 输出: Score /100, Grade A-F
```
