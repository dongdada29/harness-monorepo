# Feature — Task Spec

> Advanced 模板任务定义（支持复杂度评估）

---

## 任务类型

**Feature** — 新功能开发

---

## 触发条件

```
harness state start <功能描述>
```

---

## 复杂度评估

| 等级 | 标准 | Agent 行为 |
|------|------|-----------|
| **Low** | 改 1-2 个文件，<50 行 | Agent 直接执行，无需确认 |
| **Medium** | 多文件，需设计 | Agent 规划后执行 |
| **High** | 跨模块，影响核心 | 人类确认后再执行 |

---

## 执行流程

### CP0 — Init
- [ ] 解析功能需求，提取功能点
- [ ] 识别依赖（外部 API、库、其他模块）
- [ ] 评估复杂度
- [ ] Low → 直接执行；Medium/High → 等待确认

**CP0 报告**（CP0 完成后输出）:
```
## CP0 报告

**功能**: [描述]
**复杂度**: [Low/Medium/High]
**涉及文件**: [列表]
**依赖**: [列表]

等待确认后继续...
```

### CP1 — Plan
- [ ] 读 `harness/constraints.md`
- [ ] 接口设计（如有 API 变更）
- [ ] 制定实现顺序
- [ ] 列出验收标准

**CP1 计划**（CP1 完成后输出）:
```
## CP1 计划

**实现顺序**:
1. [步骤1]
2. [步骤2]

**验收标准**:
- [可测试的标准1]
- [可测试的标准2]

**不包括**:
- [排除项]
```

### CP2 — Exec
- [ ] 约束检查清单
  - [ ] 符合 `constraints.md` 规则
  - [ ] 无 `console.log` / `debugger`
  - [ ] 无硬编码值
  - [ ] 网络请求有明确用途
- [ ] 按 CP1 计划顺序实现
- [ ] 每完成一个子模块立即验证

**小步提交规则**: 每完成一个功能点 commit 一次，commit message 格式：
```
feat: [功能名] [简短描述]

- [改动点A]
- [改动点B]
```

### CP3 — Verify
- [ ] `harness verify` 全部 Gate 通过
- [ ] 逐项质量检查：
  - [ ] 无 `console.log` / `debugger`
  - [ ] 无敏感信息（password、secret、api_key）
  - [ ] 注释无调试遗留
- [ ] Benchmark 自评

**Gate 检查表**:

| Gate | 命令 | 通过标准 |
|------|------|---------|
| lint | `npm run lint` | 0 errors |
| typecheck | `npm run typecheck` | 0 errors |
| test | `npm test` | 全部通过 |
| build | `npm run build` | 0 errors |

### CP4 — Review + Heal
- [ ] 自审代码（逻辑、边界、错误处理）
- [ ] Gate 失败？进入 CP4 自愈循环：
  1. `harness heal --dry-run` — 查看修复方案
  2. 修复 → `harness heal` — 重验证
  3. 通过 → 继续；失败 → 最多重试 3 次

---

## 验收标准

- 所有 Gate 通过
- Benchmark 自评完成
- 代码符合约束
- 准备好合并

---

## 输出报告

CP4 完成后输出：
```
## ✅ 功能完成报告

**功能**: [名称]
**分支**: [branch-name]
**复杂度**: [Low/Medium/High]
**耗时**: [X小时 / Y步]

### 变更文件
- [file1] — [改动描述]
- [file2] — [改动描述]

### 门禁结果
| Gate | Result |
|------|--------|
| lint | ✅ |
| typecheck | ✅ |
| test | ✅ |
| build | ✅ |

### Benchmark
- Score: [X/100]
- Grade: [S/A/B/C]
```

---

## 命令速查

```bash
harness state start <功能>     # 开始任务（CP0 检索历史）
harness verify                  # 运行全部 Gate
harness heal [--dry-run]        # CP4 自愈循环
harness heal on|off|status      # 管理自愈功能
harness state done              # 完成任务，写入 taskHistory
harness state blocked <原因>    # 报告阻塞
```
