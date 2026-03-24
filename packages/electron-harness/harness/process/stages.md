# Process Stages

> Platform: Electron  
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
| 执行 | CP2 | 代码实现、功能开发 |
| 验证 | CP3 | 测试、修复、Bugfix |
| 完成 | CP4 | 代码审查、合并 |

## 状态更新

每个阶段完成后更新 state.json：

```bash
python3 tools/update-state.py --checkpoint CP1
```
