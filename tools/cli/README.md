# Tools CLI

> Harness 命令行工具  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

Tools 层提供 CLI 工具集，用于管理 Harness 项目。

---

## 2. 工具列表

| 工具 | 说明 |
|------|------|
| `benchmark/` | 效果评分 |
| `validator/` | Schema 验证 |
| `generator/` | 项目生成 |
| `eval-cli/` | 评估系统 |
| `harness-cli/` | CLI 工具 |

---

## 3. 安装

```bash
# 添加到 PATH
export PATH=$PATH:~/harness-monorepo/tools/cli

# 或使用完整路径
~/harness-monorepo/tools/cli/harness.sh
```

---

## 4. 常用命令

```bash
# 初始化
python3 tools/harness-cli/harness.py init

# 检查状态
python3 tools/harness-cli/harness.py status

# 创建检查点
python3 tools/harness-cli/harness.py checkpoint

# 验证
python3 tools/harness-cli/harness.py validate
```

---

## 5. 快捷脚本

| 脚本 | 说明 |
|------|------|
| `harness.sh` | 主 CLI |
| `check.sh` | 快速检查 |
| `validate.sh` | 验证 |
