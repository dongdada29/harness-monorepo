# Codex Agent Configuration

> Agent: Codex (OpenAI)  
> Version: 1.0.0

---

## 概述

Codex 是 OpenAI 开发的大语言模型，专注于代码生成。

## 配置

```yaml
agent:
  name: codex
  provider: openai
  model: gpt-4o
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
