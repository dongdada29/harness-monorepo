# Tools Layer

> Tools for harness development  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## Tools

| 工具 | 说明 |
|------|------|
| **cli** | Harness CLI 工具 |
| **benchmark** | Benchmark 评分工具 |
| **validator** | Schema 验证器 |
| **generator** | 项目生成器 |

---

## CLI

```bash
harness init              # 初始化
harness status           # 查看状态
harness checkpoint      # 标记检查点
harness validate        # 验证 Schema
harness report          # 生成报告
```

---

## Benchmark

```bash
benchmark.py --project ./    # 评分
benchmark.py --compare a b   # 对比两次
```

---

## Validator

```bash
validate.py state.json       # 验证状态
validate.py schema         # 验证 Schema
```
