# Basic Harness Template

> 最基础的 Harness 模板  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 快速开始

```bash
# 1. 复制模板
cp -r templates/basic myproject

# 2. 自定义
cd myproject
# 编辑 harness/base/constraints.md

# 3. 初始化
python3 tools/cli/harness.py init
```

---

## 包含内容

| 文件 | 说明 |
|------|------|
| `harness/base/constraints.md` | 基础约束 |
| `harness/base/state.json` | 状态模板 |
| `harness/feedback/state/state.json` | 反馈状态 |
| `tools/benchmark.py` | 评分工具 |
| `tools/validate.py` | 验证工具 |

---

## 自定义

### 1. 修改约束

编辑 `harness/base/constraints.md`

### 2. 配置检查点

编辑 `harness/base/state.json`

### 3. 启动开发

```bash
python3 tools/benchmark.py --project .
```

---

## 依赖

- Python 3.8+
- Git
