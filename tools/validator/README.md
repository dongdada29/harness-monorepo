# Validator Tool

> Harness Schema 验证工具  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

验证 Harness 配置文件是否符合 Schema 规范。

---

## 2. 验证文件

| 文件 | 说明 |
|------|------|
| `constraints.md` | 约束规则 |
| `state.json` | 状态文件 |
| `state.v1.schema.json` | Schema 定义 |

---

## 3. 使用方法

```bash
# 验证所有配置
python3 tools/validator/validate.py --all ./packages/agent-harness

# 验证 state.json
python3 tools/validator/validate.py --state ./harness/feedback/state/state.json

# 验证 constraints.md
python3 tools/validator/validate.py --constraints ./harness/base/constraints.md
```

---

## 4. 验证规则

### State.json
- 必填字段存在
- 类型正确
- 枚举值有效

### Constraints.md
- 命令分类正确
- MCP Tools 格式正确
- 权限级别有效

---

## 5. 输出示例

```
========================================
      VALIDATION REPORT
========================================
Project: packages/agent-harness
----------------------------------------
constraints.md      ✅ PASSED
state.json          ✅ PASSED
schema.v1.json      ✅ PASSED
----------------------------------------
OVERALL             ✅ PASSED (3/3)
========================================
```

---

## 6. 错误处理

| 错误 | 说明 | 修复 |
|------|------|------|
| E001 | 缺少必填字段 | 添加字段 |
| E002 | 类型错误 | 检查类型 |
| E003 | 枚举值无效 | 使用有效值 |
