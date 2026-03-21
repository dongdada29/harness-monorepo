# Harness 快速参考卡

> 一页纸速查手册

---

## 安装

```bash
# 克隆
git clone https://github.com/dongdada29/harness-monorepo.git

# 安装到项目
./setup.sh /path/to/project
./setup.sh --type electron /path/to/project
```

---

## 核心文件

```
项目/
├── CLAUDE.md                    # Claude Code 指令
├── .cursorrules                 # Cursor 规则
├── harness/
│   ├── base/
│   │   └── constraints.md       # 约束规则
│   └── feedback/
│       └── state/
│           └── state.json       # 任务状态
└── scripts/
    └── update-state.sh          # 状态更新
```

---

## 工作流 (CP1-CP5)

```
CP1 ──► CP2 ──► CP3 ──► CP4 ──► CP5
确认     规划     实现     验证     完成
```

---

## 4 Gates 质量门禁

| Gate | 命令 | 要求 |
|------|------|------|
| Lint | `npm run lint` | 0 errors |
| Type | `npm run typecheck` | 0 errors |
| Test | `npm test` | all pass |
| Build | `npm run build` | 0 errors |

---

## 常用命令

```bash
# 状态管理
./scripts/update-state.sh task_start "任务描述"
./scripts/update-state.sh task_complete "任务描述"
./scripts/update-state.sh task_block "阻塞原因"

# 验证
npm run test           # 单元测试 (28 个)
npm run validate       # 快速验证 (5 分钟)
npm run ci             # CI 完整流程

# Benchmark
python3 tools/eval-cli/benchmark.py --project .
python3 tools/eval-cli/benchmark.py --project . --output json
```

---

## Benchmark 评分

| 分数 | 等级 | 描述 |
|------|------|------|
| 95-100 | S+ | World Class |
| 90-94 | S | Excellent |
| 85-89 | A+ | Outstanding |
| 80-84 | A | Very Good |
| 75-79 | B+ | Good |
| 70-74 | B | Satisfactory |
| 60-69 | C | Marginal |
| <60 | D/F | 需改进 |

---

## 评分维度

| 维度 | 权重 | 指标 |
|------|------|------|
| **Efficiency** | 40% | 完成率、Gate 通过率、吞吐量 |
| **Quality** | 30% | 无 console.log、测试通过 |
| **Behavior** | 15% | 状态更新、变更追踪 |
| **Autonomy** | 15% | 自主完成、自我修正 |

---

## 约束速查

### ❌ 禁止

```
不读 state 就开始
跳过 /verify
一次改 > 5 个文件
遇到阻塞不汇报
console.log / debugger
直接 push to main
```

### ✅ 必须

```
开始前读 state
用 /start 开始
每步 /verify
阻塞时及时汇报
写测试
代码审查
```

---

## Agent 支持

| Agent | 配置文件 | 状态 |
|-------|----------|------|
| Claude Code | CLAUDE.md | ✅ |
| Cursor | .cursorrules | ✅ |
| Codex | CODEX.md | ✅ |
| OpenCode | OPENCODE.md | 🔄 |

---

## 故障排查

```bash
# state.json 损坏
curl -fsSL https://.../state.json > harness/feedback/state/state.json

# 脚本权限
chmod +x scripts/*.sh

# Python 报错
pip install -r tools/eval-cli/requirements.txt
```

---

## 文档链接

- [使用案例](./USAGE_EXAMPLES.md)
- [Agent 集成](./AGENT_INTEGRATION.md)
- [Benchmark 指标](./BENCHMARK_METRICS.md)
- [验证指南](./VALIDATION.md)
- [FAQ](./FAQ.md)
- [故障排查](./troubleshooting.md)

---

## GitHub

https://github.com/dongdada29/harness-monorepo

---

*快速参考卡 v1.2.0 | 2026-03-22*
