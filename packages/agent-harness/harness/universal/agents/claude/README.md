# Claude Agent Configuration

> Agent: Claude (Anthropic)  
> Version: 1.0.0

---

## 概述

Claude 是 Anthropic 开发的大语言模型，擅长代码生成和分析。

## 配置

```yaml
agent:
  name: claude
  provider: anthropic
  model: claude-3-5-sonnet
```

## 命令

| 命令 | 说明 |
|------|------|
| `/start` | 开始任务 |
| `/verify` | 验证实现 |
| `/checkpoint` | 保存检查点 |

## 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
```

## 约束

- 必须遵循 harness 约束
- 必须更新 state.json
- 必须通过 Gate 检查
