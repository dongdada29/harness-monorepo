# Agent Harness Monorepo

> 所有 AI 编码 Agent 的工程化工作流统一管理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub stars](https://img.shields.io/github/stars/dongdada29/harness-monorepo)](https://github.com/dongdada29/harness-monorepo/stargazers)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()

---

## 🎯 是什么

Harness 是 AI Coding Agent 的**工程化框架**，提供：
- 标准化工作流 (CP0→CP1→CP2→CP3→CP4)
- 量化评分体系 (Benchmark)
- 质量门禁 (Gates)

---

## 📦 Packages

| Package | 说明 | Agent |
|---------|------|-------|
| **agent-harness** | 通用版 | Claude Code / Cursor / Codex / OpenCode |
| **nuwax-harness** | Nuwax Agent OS 专用 | Nuwax |
| **electron-harness** | Electron + Ant Design | 通用 |
| **generic-harness** | 通用项目模板 | 通用 |

---

## 🏗️ 结构

```
harness-monorepo/
├── core/              # CP 工作流、Schema、Benchmark
├── business/           # 业务层 (nuwax, agent-desktop)
├── tech/             # 技术层 (web, electron, rust, cli, uniapp)
├── tools/            # 工具 (benchmark, validator, cli)
├── templates/         # 模板 (basic, advanced)
├── packages/         # Harness 包
├── docs/            # 文档
└── tests/           # 测试
```

---

## 🚀 快速开始

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
./setup.sh nuwax /path/to/project
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

## 🔧 Tools

| 工具 | 说明 |
|------|------|
| `tools/eval-cli/` | 完整评估系统 |
| `tools/harness-cli/` | CLI 工具 |
| `tools/benchmark/` | 评分工具 |
| `tools/validator/` | Schema 验证 |

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
