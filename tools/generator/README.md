# Generator Tool

> Harness 项目生成器  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 概述

快速生成 Harness 项目结构。

---

## 2. 使用方法

```bash
# 生成通用 Harness
python3 tools/generator/generate.py --template basic --output ./my-harness

# 生成 Electron Harness
python3 tools/generator/generate.py --template electron --output ./electron-app

# 生成带 MCP 的 Harness
python3 tools/generator/generate.py --template nuwax --output ./nuwax-app --with-mcp
```

---

## 3. 模板

| 模板 | 说明 |
|------|------|
| `basic` | 基础 Harness |
| `advanced` | 完整工作流 |
| `electron` | Electron 专用 |
| `nuwax` | Nuwax 专用 |
| `generic` | 通用模板 |

---

## 4. 生成结构

```
my-harness/
├── harness/
│   ├── base/
│   │   ├── constraints.md
│   │   └── state.json
│   ├── feedback/
│   │   └── state/
│   │       └── state.json
│   └── projects/
│       └── default/
│           └── project.md
├── skills/
│   └── README.md
└── README.md
```

---

## 5. 自定义

编辑生成后的 `harness/base/constraints.md` 自定义约束。

---

## 6. 验证

生成后验证：

```bash
python3 tools/validator/validate.py --all ./my-harness
```
