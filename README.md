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

## GitHub

https://github.com/dongdada29/harness-monorepo

## 相关项目

- [harness-monorepo](https://github.com/dongdada29/harness-monorepo)
- [agent-harness](https://github.com/dongdada29/agent-harness)
- [nuwax-harness](https://github.com/dongdada29/nuwax-harness)
