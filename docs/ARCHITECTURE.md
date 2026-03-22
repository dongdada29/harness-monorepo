# Harness Monorepo 架构设计文档

> **版本**: 2.0.0  
> **更新**: 2026-03-23  
> **状态**: 设计完成

---

## 1. 设计目标

### 1.1 核心问题

当前 harness 分散在多个项目中：
- nuwaclaw (Electron 客户端)
- agent-desktop (Tauri 桌面)
- 各种内部项目

### 1.2 解决目标

```
统一 + 可复用 + 可扩展
         ↓
    业务 × 技术栈 矩阵
         ↓
    Core + Business + Tech
```

---

## 2. 设计原则

### 2.1 分层架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Core (通用层)                          │
│  - CP 工作流定义                                        │
│  - State Schema                                        │
│  - Benchmark 框架                                      │
│  - 通用约束                                            │
└───────────────────────────────────────────────────────┬─┘
                                                        │
┌───────────────────────────────────────────────────────▼─┐
│                   Business (业务层)                      │
│  - nuwax 业务                                         │
│  - agent-desktop 业务                                   │
│  - 其他业务...                                         │
└───────────────────────────────────────────────────────┬─┘
                                                        │
┌───────────────────────────────────────────────────────▼─┐
│                   Tech Stack (技术栈层)                  │
│  - web-harness (UmiJS + React + AntD)                  │
│  - electron-harness (Electron)                         │
│  - cli-harness (Node.js)                              │
│  - rust-harness (Rust + Tauri)                        │
│  - uniapp-harness (UniApp + Vue)                      │
└───────────────────────────────────────────────────────┬─┘
                                                        │
┌───────────────────────────────────────────────────────▼─┐
│                    Tools (工具层)                        │
│  - Benchmark CLI                                       │
│  - State Validator                                    │
│  - MCP Tools                                         │
│  - Skills                                           │
│  - Testing Templates                                 │
└───────────────────────────────────────────────────────┘
```

### 2.2 依赖关系

```
Core ← Business ← Tech
         ↓
       Tools
```

**规则：**
- Core 是底层，不能依赖其他层
- Business 依赖 Core
- Tech 依赖 Core + Business
- Tools 依赖所有层

---

## 3. 目录结构

### 3.1 完整结构

```
harness-monorepo/
│
├── core/                          # 核心层（与业务无关）
│   ├── harness/                   # CP 工作流定义
│   │   ├── base/                # 基础配置
│   │   │   ├── constraints.md
│   │   │   ├── state.schema.json
│   │   │   └── checkpoints.md
│   │   ├── templates/           # 任务模板
│   │   │   ├── feature.md
│   │   │   ├── bugfix.md
│   │   │   └── refactor.md
│   │   └── prompts/           # Agent 提示词
│   │       ├── task-start.md
│   │       └── task-complete.md
│   │
│   ├── benchmark/               # 评分框架
│   │   ├── runner.py
│   │   ├── scorer.py
│   │   └── reporters/
│   │
│   ├── constraints/             # 通用约束
│   │   ├── security.md
│   │   ├── code-style.md
│   │   └── git-workflow.md
│   │
│   └── schema/                  # JSON Schema
│       ├── state.v1.schema.json
│       ├── checkpoint.v1.schema.json
│       └── metrics.v1.schema.json
│
├── business/                      # 业务层
│   ├── nuwax/                  # 业务 A
│   │   ├── harness/           # 业务特定 harness
│   │   ├── skills/            # 业务特定 skills
│   │   ├── mcp/              # 业务 MCP 工具
│   │   └── tests/            # 业务测试方案
│   │
│   ├── agent-desktop/          # 业务 B
│   │   ├── harness/
│   │   ├── skills/
│   │   ├── mcp/
│   │   └── tests/
│   │
│   └── _template/              # 业务模板（新建业务用）
│       ├── harness/
│       ├── skills/
│       ├── mcp/
│       └── tests/
│
├── tech/                         # 技术栈层
│   ├── web/                     # UmiJS + React + AntD
│   │   ├── harness/           # Web 特定配置
│   │   ├── skills/            # Web Skills
│   │   │   ├── react.md
│   │   │   ├── umi.md
│   │   │   └── antd.md
│   │   ├── mcp/              # Web MCP 工具
│   │   │   ├── file-system.md
│   │   │   └── git.md
│   │   └── tests/            # Web 测试方案
│   │       ├── jest.md
│   │       └── playwright.md
│   │
│   ├── electron/                # Electron
│   │   ├── harness/
│   │   ├── skills/
│   │   ├── mcp/
│   │   └── tests/
│   │
│   ├── cli/                     # Node.js CLI
│   │   ├── harness/
│   │   ├── skills/
│   │   ├── mcp/
│   │   └── tests/
│   │
│   ├── rust/                    # Rust + Tauri
│   │   ├── harness/
│   │   ├── skills/
│   │   ├── mcp/
│   │   └── tests/
│   │
│   └── uniapp/                  # UniApp + Vue
│       ├── harness/
│       ├── skills/
│       ├── mcp/
│       └── tests/
│
├── tools/                         # 工具层
│   ├── cli/                     # Harness CLI
│   │   ├── init/               # 初始化
│   │   ├── status/            # 状态查看
│   │   ├── checkpoint/        # 检查点管理
│   │   └── validate/          # 验证工具
│   │
│   ├── benchmark/              # Benchmark 工具
│   │   ├── runner.py
│   │   ├── compare.py
│   │   └── report.py
│   │
│   ├── validator/              # Schema 验证器
│   │   ├── state-validator.py
│   │   └── checkpoint-validator.py
│   │
│   └── generator/              # 项目生成器
│       └── new-business.sh
│
├── templates/                     # 可复用模板
│   ├── basic-harness/
│   ├── advanced-harness/
│   └── enterprise-harness/
│
└── docs/                         # 文档
    ├── architecture.md
    ├── quickstart.md
    └── best-practices.md
```

---

## 4. 业务 × 技术栈 矩阵

### 4.1 矩阵定义

| 业务 ↓ / 技术 → | Web | Electron | CLI | Rust | UniApp |
|---------------|------|----------|------|------|---------|
| **nuwax**     | ✅  | ✅       | ✅  | ✅  | ✅     |
| **agent-desktop** | ✅ | ✅     | ✅  | ✅  | -      |
| **template** | ✅  | ✅       | ✅  | ✅  | ✅     |

### 4.2 继承关系

```
nuwax-electron-harness = nuwax-business + electron-tech + core
```

**继承链：**
```
core → nuwax-business → electron-tech → nuwax-electron-harness
```

---

## 5. MCP Tools 设计

### 5.1 分类

| 类型 | 说明 | 示例 |
|------|------|------|
| **通用** | 所有技术栈通用 | `git`, `file-read`, `file-write` |
| **技术栈特定** | 某类技术栈通用 | `npm-install` (Node), `cargo-build` (Rust) |
| **业务特定** | 某业务专用 | `nuwax-api-call` (nuwax) |

### 5.2 MCP Tools 结构

```
mcp/
├── universal/              # 通用工具
│   ├── git.md
│   ├── file-system.md
│   └── terminal.md
│
├── web/                   # Web 工具
│   ├── npm.md
│   ├── pnpm.md
│   └── jest.md
│
├── electron/              # Electron 工具
│   ├── electron-build.md
│   └── electron-test.md
│
├── rust/                 # Rust 工具
│   ├── cargo.md
│   └── rust-analyzer.md
│
└── nuwax/               # nuwax 业务工具
    ├── api-call.md
    └── auth.md
```

---

## 6. Skills 设计

### 6.1 分类

| 类型 | 说明 |
|------|------|
| **通用 Skills** | 所有项目通用 |
| **技术 Skills** | 按技术栈 |
| **业务 Skills** | 按业务 |

### 6.2 Skills 结构

```
skills/
├── universal/               # 通用
│   ├── code-review.md
│   ├── refactor.md
│   └── testing.md
│
├── web/                   # Web Skills
│   ├── react-best-practices.md
│   ├── antd-usage.md
│   └── umijs-patterns.md
│
├── electron/              # Electron Skills
│   ├── ipc-patterns.md
│   └── main-process.md
│
├── rust/                  # Rust Skills
│   ├── rust-best-practices.md
│   └── tokio-async.md
│
└── nuwax/                # nuwax 业务 Skills
    ├── agent-workflow.md
    └── mcp-integration.md
```

---

## 7. 测试方案

### 7.1 测试分类

| 类型 | 说明 |
|------|------|
| **单元测试** | 函数/组件测试 |
| **集成测试** | 模块间协作 |
| **E2E 测试** | 端到端流程 |
| **性能测试** | Benchmark |

### 7.2 测试结构

```
tests/
├── unit/                 # 单元测试模板
│   ├── jest.config.js
│   ├── vitest.config.ts
│   └── templates/
│
├── integration/           # 集成测试
│   └── templates/
│
├── e2e/                  # E2E 测试
│   ├── playwright/
│   └── cypress/
│
└── performance/          # 性能测试
    └── lighthouse/
```

---

## 8. 使用示例

### 8.1 创建新业务

```bash
# 使用模板创建
harness-monorepo/tools/generator/new-business.sh mybusiness
```

### 8.2 组合继承

```bash
# 创建 nuwax + Electron 项目
harness init --business nuwax --tech electron

# 生成的结构
nuwax-electron/
├── harness/               # 继承 core + nuwax-business + electron-tech
├── skills/
├── mcp/
└── tests/
```

### 8.3 自定义扩展

```bash
# 在已有基础上添加业务特定配置
harness extend --business nuwax --skill api-integration
```

---

## 9. 迁移计划

### 9.1 当前状态

```
harness-monorepo/
├── generic-harness/      # 通用（混乱）
├── electron-harness/     # Electron（部分）
├── nuwax-harness/       # nuwax（部分）
└── agent-harness/       # Agent（部分）
```

### 9.2 目标状态

```
harness-monorepo/
├── core/                 # 重构
├── business/            # 新结构
│   └── nuwax/
├── tech/                # 新结构
│   ├── web/
│   ├── electron/
│   └── rust/
└── tools/
```

### 9.3 迁移步骤

1. **Phase 1**: 创建 core 层
2. **Phase 2**: 迁移 nuwax 业务
3. **Phase 3**: 迁移 tech 层
4. **Phase 4**: 清理旧结构

---

## 10. 参考

- [Monorepo Tools](https://turborepo.com)
- [Nx](https://nx.dev)
- [Lerna](https://lerna.js.org)
- [Harness Engineering - Anthropic](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)

---

## 11. 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-03-23 | 2.0.0 | 按业务×技术栈矩阵重构 |
| 2026-03-22 | 1.0.0 | 初始版本 |
