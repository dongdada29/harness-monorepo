# OpenCode Agent Configuration

> Agent: OpenCode  
> Version: 1.0.0

---

## 概述

OpenCode 是一个开源的 AI 代码生成工具。

## 配置

```yaml
agent:
  name: opencode
  provider: opencode
  model: opencode
```

## 命令

| 命令 | 说明 |
|------|------|
| `/start` | 开始任务 |
| `/verify` | 验证实现 |

## 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
```

## 约束

- 必须遵循 harness 约束
- 必须更新 state.json
