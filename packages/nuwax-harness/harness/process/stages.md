# Process Stages

> Platform: Nuwax  
> Version: 1.0.0

---

## 开发流程

```
CP0 → CP1 → CP2 → CP3 → CP4
初始化 → 规划 → 执行 → 验证 → 完成
```

## 阶段说明

| 阶段 | Checkpoint | 说明 |
|------|-----------|------|
| 初始化 | CP0 | 环境检查、依赖安装 |
| 规划 | CP1 | 任务分解、方案设计 |
| 执行 | CP2 | MCP 调用、代码实现 |
| 验证 | CP3 | 测试、修复 |
| 完成 | CP4 | 代码审查、合并 |

## MCP 集成

Nuwax 使用 MCP 进行 Agent 通信。

```bash
mcp invoke agent-runtime.execute --args '{"task": "..."}'
```

## 状态更新

```bash
python3 tools/update-state.py --checkpoint CP1
```
