# Advanced Harness Template

> 高级模板，包含完整的工作流  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 包含内容

| 组件 | 文件 |
|-------|------|
| **Harness** | base/, projects/, feedback/ |
| **MCP Tools** | mcp/*.md |
| **Skills** | skills/*.md |
| **Tests** | tests/ |
| **Tools** | benchmark/, validator/ |

---

## 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
```

| Checkpoint | 说明 |
|-----------|------|
| CP0 | 初始化 |
| CP1 | 任务规划 |
| CP2 | 执行 |
| CP3 | 验证 |
| CP4 | 完成 |

---

## 工具

```bash
python3 tools/benchmark.py --project .
python3 tools/validate.py
python3 tools/cli/harness.py init
```

---

## 自定义

编辑：
- `harness/base/constraints.md`
- `harness/projects/*/constraints.md`
- `skills/*/README.md`
