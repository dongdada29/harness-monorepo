# Agent Harness Monorepo

> 所有 AI 编码 Agent 的工程化工作流统一管理

---

## 快速开始

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
./setup.sh nuwax /path/to/project
```

---

## Packages

| Package | 说明 |
|---------|------|
| **agent-harness** | 通用版（Claude Code / Cursor / Codex / OpenCode） |
| **nuwax-harness** | Nuwax Agent OS 专用 |
| **electron-harness** | Electron + Ant Design 专用 |
| **generic-harness** | 通用项目模板 |

---

## Scripts

| 脚本 | 说明 |
|------|------|
| `setup.sh` | 一键安装 |
| `scripts/check.sh` | 配置检查 |
| `scripts/cleanup.sh` | 技术债务扫描 |
| `scripts/eval.sh` | 效果评估 |
| `scripts/init.sh` | 初始化 |
| `scripts/list.sh` | 列出 Package |

---

## Tools

| 工具 | 说明 |
|------|------|
| `tools/eval-cli/` | 完整评估系统（Python/Shell） |

---

## 工作流

```
CP1 → CP2 → CP3 → CP4 → CP5
任务确认 → 规划分解 → 执行实现 → 质量门禁 → 审查完成
```

---

## 质量门禁

```
Gate 1: npm run lint       → 0 errors
Gate 2: npm run typecheck → 0 errors
Gate 3: npm test           → all pass
Gate 4: npm run build     → 0 errors
```

---

## 约束规则

### 禁止
- ❌ 不读 state 就开始
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 遇到阻塞不汇报

### 必须
- ✅ 开始前读 state
- ✅ 用 /start 开始
- ✅ 每步 /verify

---

## 文档

| 文档 | 说明 |
|------|------|
| [QUICKSTART.md](./QUICKSTART.md) | 5 分钟快速开始 |
| [docs/USAGE_EXAMPLES.md](./docs/USAGE_EXAMPLES.md) | 使用案例集 |
| [docs/AGENT_INTEGRATION.md](./docs/AGENT_INTEGRATION.md) | Agent 集成指南 |
| [docs/BENCHMARK_METRICS.md](./docs/BENCHMARK_METRICS.md) | Benchmark 指标详解 |
| [docs/VALIDATION.md](./docs/VALIDATION.md) | 验证指南 |
| [docs/FAQ.md](./docs/FAQ.md) | 常见问题 |
| [docs/troubleshooting.md](./docs/troubleshooting.md) | 故障排查 |

---

## npm scripts

```bash
npm run setup          # 安装 harness
npm run test           # 单元测试 (28 个测试)
npm run test:quick     # 快速验证 (5 分钟)
npm run validate       # 快速验证
npm run ci             # CI 完整流程
```

---

## GitHub

https://github.com/dongdada29/harness-monorepo

## 相关项目

- [harness-monorepo](https://github.com/dongdada29/harness-monorepo)
- [agent-harness](https://github.com/dongdada29/agent-harness)
- [nuwax-harness](https://github.com/dongdada29/nuwax-harness)
