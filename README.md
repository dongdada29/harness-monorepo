# Agent Harness Monorepo

> 所有 AI 编码 Agent 的工程化工作流统一管理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/dongdada29/harness-monorepo)](https://github.com/dongdada29/harness-monorepo/stargazers)
[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)]()

---

## 🎯 是什么

Harness 是 AI Coding Agent 的**工程化框架**，提供：
- 标准化工作流 (CP0→CP1→CP2→CP3→CP4)
- 量化评分体系 (Benchmark)
- 质量门禁 (Gates)
- CLI 工具链 (init/state/verify/benchmark/clean/doctor)

---

## 📦 Packages

| Package | 说明 | Agent |
|---------|------|-------|
| **agent-harness** | 通用版 | Claude Code / Cursor / Codex / OpenCode |
| **nuwax-harness** | Nuwax Agent OS 专用 | Nuwax |
| **electron-harness** | Electron + Ant Design | 通用 |
| **generic-harness** | 通用项目模板 | 通用 |
| **@harnesskit/cli** | CLI 工具 | 全平台 |

---

## 🏗️ 结构

```
harness-monorepo/
├── packages/          # Harness 包 (@harnesskit/cli, nuwax-harness, etc)
├── core/             # CP 工作流、Schema
├── tools/            # benchmark runner
├── templates/        # basic / advanced 模板
│   ├── basic/        # 轻量约束，适合简单项目
│   └── advanced/     # 完整流程，适合复杂项目
├── docs/             # 架构、指标、集成文档
└── tests/            # 单元测试 (30 tests)
```

---

## 🚀 快速开始

```bash
# 1. Clone
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo

# 2. 初始化项目
node packages/cli/bin/harness.js init generic /path/to/project --template basic

# 3. 开始任务
cd /path/to/project
harness state start <任务描述>

# 4. 查看状态
harness state show
harness doctor  # 检查环境
```

---

## 🔧 CLI 命令

```
harness init [type] [dir] --template basic|advanced   初始化
harness state show|start|done|blocked|stats|export  状态管理
harness verify [dir]                              运行 Gate
harness test [dir]                               运行测试
harness benchmark [dir]                          运行评分
harness clean [dir]                               重置 CP0
harness doctor                                    检查环境
```

---

## 📊 Benchmark 评分

| 等级 | 分数 | 说明 |
|------|------|------|
| S+ | ≥95 | 卓越 |
| S | ≥90 | 优秀 |
| A+ | ≥85 | 很好 |
| A | ≥80 | 良好 |
| B | ≥70 | 合格 |
| C | ≥60 | 一般 |
| D | ≥50 | 较差 |
| F | <50 | 不合格 |

---

## 📖 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](./QUICKSTART.md) | 5 分钟快速开始 |
| [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) | 架构设计 |
| [docs/BENCHMARK_METRICS.md](./docs/BENCHMARK_METRICS.md) | 指标详解 |
| [docs/AGENT_INTEGRATION.md](./docs/AGENT_INTEGRATION.md) | Agent 集成 |
| [docs/VALIDATION.md](./docs/VALIDATION.md) | 验证指南 |
| [docs/FAQ.md](./docs/FAQ.md) | 常见问题 |

---

## 🌐 相关项目

- [harness-monorepo](https://github.com/dongdada29/harness-monorepo)
- [agent-harness](https://github.com/dongdada29/agent-harness)
- [nuwax-harness](https://github.com/dongdada29/nuwax-harness)

---

## 许可证

MIT License
