# Quick Start - 5 分钟上手 Harness

> AI Coding Agent 工程化框架  
> 版本: 2.1.0  
> 更新: 2026-04-27

---

## 1. 什么是 Harness

Harness 是 AI Coding Agent 的**工程化框架**，提供：
- 标准化工作流 (CP0→CP1→CP2→CP3→CP4)
- 量化评分体系 (Benchmark)
- 质量门禁 (Gates)
- 状态管理 + CLI 工具

---

## 2. 安装

```bash
git clone https://github.com/dongdada29/harness-monorepo.git
cd harness-monorepo
npm install  # 已安装可跳过
```

---

## 3. 为项目启用 Harness

```bash
# 方式 1: 使用 setup 脚本
./setup.sh nuwax /path/to/project

# 方式 2: 使用 CLI 初始化（推荐）
node packages/cli/bin/harness.js init generic /path/to/project --template basic
# 或 --template advanced（完整工作流）
```

---

## 4. CLI 命令

| 命令 | 说明 |
|------|------|
| `harness init [type] [dir] --template basic\|advanced` | 初始化 |
| `harness state show` | 查看当前状态 |
| `harness state start <task>` | 开始任务 |
| `harness state done` | 标记完成 |
| `harness state stats` | 查看 metrics |
| `harness state export` | 导出 state.json |
| `harness verify` | 运行质量门禁 |
| `harness test` | 运行测试 |
| `harness clean` | 重置到 CP0 |
| `harness doctor` | 检查环境 |
| `harness benchmark` | 运行评分 |

---

## 5. 工作流程

```
1. harness state start <任务描述>
2. CP0 → CP1 → CP2 → CP3 → CP4
3. 每个阶段通过 Gate
4. harness state done
```

### Gate 门禁（自动验证）

| Gate | 检查 |
|------|------|
| lint | ESLint 通过 |
| typecheck | TypeScript 无错误 |
| test | 单元测试通过 |
| build | 构建成功 |

---

## 6. Benchmark 评分

```bash
# 基本评分
python3 tools/benchmark/runner.py --project .

# 对比历史
python3 tools/benchmark/runner.py --project . --output markdown

# 评分等级
# S+ ≥95 | S ≥90 | A+ ≥85 | A ≥80 | B ≥70 | C ≥60 | D ≥50 | F <50
```

---

## 7. CI 集成

```yaml
# .github/workflows/ci.yml
- name: Run harness tests
  run: node packages/cli/bin/harness.js test
```

---

## 8. 下一步

- 阅读 [README.md](./README.md) 了解整体架构
- 查看 [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md) 深入设计
- 参考 [docs/USAGE_EXAMPLES.md](./docs/USAGE_EXAMPLES.md) 实战案例
- 跑 `harness doctor` 检查环境

---

## 9. 常见问题

**Q: 支持哪些 Agent？**
A: Claude Code, Cursor, Codex, OpenCode, Copilot

**Q: 需要安装依赖吗？**
A: Node.js >= 18 即可，其他按需安装

**Q: 如何自定义约束？**
A: 编辑 `harness/base/constraints.md`