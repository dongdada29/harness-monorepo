# Cursor Agent Configuration

> Agent: Cursor (AI IDE)  
> Version: 1.0.0

---

## 概述

Cursor 是基于 AI 的 IDE，集成了代码生成和编辑功能。

## 配置

```yaml
agent:
  name: cursor
  provider: cursor
  model: cursor-3-5-sonnet
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
