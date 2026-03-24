# Generic Harness Skill

> Package: generic-harness  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

通用项目 Harness 模板，适用于任何 Node.js/TypeScript 项目。

---

## 2. 支持的 Agent

- Claude Code
- Cursor
- Codex
- OpenCode
- Copilot

---

## 3. 工作流

```
CP0 → CP1 → CP2 → CP3 → CP4
初始化 → 规划 → 执行 → 验证 → 完成
```

---

## 4. 命令配置

编辑 `harness/base/constraints.md` 自定义命令。

---

## 5. 约束规则

| 类型 | 规则 |
|------|------|
| Auto-Approve | dev, build, test |
| Need-Confirm | add, delete, commit |
| Blocked | 全局安装 |

---

## 6. 模板变量

```json
{
  "{{project_name}}": "项目名称",
  "{{language}}": "语言",
  "{{framework}}": "框架"
}
```
