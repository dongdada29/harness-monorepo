# Quick Start - 5 分钟上手

> Harness Monorepo 快速入门  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 什么是 Harness

Harness 是 AI Coding Agent 的**工程化框架**，提供：
- 标准化工作流 (CP0→CP1→CP2→CP3→CP4)
- 量化评分体系 (Benchmark)
- 质量门禁 (Gates)

---

## 2. 安装

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
```

---

## 3. 为项目启用 Harness

```bash
# 方式 1: 使用 setup 脚本
./setup.sh nuwax /path/to/project

# 方式 2: 复制模板
cp -r templates/basic /path/to/project/harness
```

---

## 4. 常用命令

| 命令 | 说明 |
|------|------|
| `./scripts/check.sh` | 检查配置 |
| `./scripts/eval.sh` | 评估效果 |
| `./scripts/validate.sh` | 验证 Schema |

---

## 5. 工作流程

```
1. 读取 harness/base/state.json
2. 执行任务（遵循 constraints.md）
3. 更新 checkpoint
4. 通过 Gate（lint → test → build）
5. 提交审查
```

---

## 6. Benchmark 评分

```bash
python3 tools/benchmark/benchmark.py --project .
# 输出: Score /100, Grade A-F
```

---

## 7. 下一步

- 阅读 [README.md](./README.md) 了解整体架构
- 查看 [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) 深入设计
- 参考 [docs/USAGE_EXAMPLES.md](./docs/USAGE_EXAMPLES.md) 实战案例

---

## 8. 常见问题

**Q: 需要安装依赖吗？**
A: 不需要，Harness 是纯配置文件。

**Q: 支持哪些 Agent？**
A: Claude Code, Cursor, Codex, OpenCode, Copilot。

**Q: 如何自定义？**
A: 编辑 `harness/base/constraints.md`。
