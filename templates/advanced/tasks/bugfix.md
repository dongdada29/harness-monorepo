# Bug Fix — Task Spec

> Advanced 模板任务定义（支持复杂度评估 + CP4 自愈）

---

## 任务类型

**Bugfix** — Bug 修复

---

## 触发条件

```
harness state start <bug描述>
```

---

## 复杂度评估

| 等级 | 标准 | Agent 行为 |
|------|------|-----------|
| **Low** | 单文件，根因明确 | Agent 直接修复，无需确认 |
| **Medium** | 多文件，根因需调查 | Agent 调查后规划，再执行 |
| **High** | 跨模块，可能影响核心功能 | 人类确认后再修复 |

---

## 执行流程

### CP0 — Init
- [ ] 理解预期行为 vs 实际行为
- [ ] 收集信息：错误日志、复现步骤、调用链路
- [ ] 确认涉及文件
- [ ] 评估复杂度

**CP0 报告**:
```
## CP0 报告

**Bug**: [描述]
**复现步骤**: [步骤]
**预期行为**: [描述]
**实际行为**: [描述]
**复杂度**: [Low/Medium/High]
**涉及文件**: [列表]
```

### CP1 — Plan
- [ ] 读 `harness/constraints.md`
- [ ] 制定调查计划（定位根因）
- [ ] 制定修复方案（最小改动原则）

**调查手段**:
```bash
# 日志追踪
grep -rn "ERROR_KEYWORD" src/ --include="*.ts"
git log --oneline -10

# 运行时调试
npm run dev  # 启动开发服务器
# ... 复现步骤

# 单元测试
npm test -- --testPathPattern="模块名"
```

**CP1 计划**:
```
## CP1 计划

**根因**: [描述]
**修复方案**: [描述]
**改动文件**: [列表]
**回归测试**: [计划]
```

### CP2 — Exec
- [ ] 修复根因
- [ ] 保持改动最小化（不引入新功能、不做大面积风格修改）
- [ ] 添加 regression 测试防止再次发生
- [ ] 立即运行 `harness verify`

**约束**:
- 只改必要的文件
- 不在修复时重构无关代码
- 不引入新的 lint warning

### CP3 — Verify
- [ ] `harness verify` 全部 Gate 通过
- [ ] 用复现步骤验证修复有效
- [ ] 回归测试通过
- [ ] Benchmark 自评

### CP4 — Review + Heal
- [ ] 自审代码（逻辑、边界、错误处理）
- [ ] Gate 失败？进入 CP4 自愈循环：
  1. `harness heal --dry-run` — 查看历史同类修复经验
  2. 修复 → `harness heal` — 重验证
  3. 通过 → 继续；失败 → 最多重试 3 次

---

## 约束

- 只改必要的文件
- 不引入新功能
- 不做代码风格大面积修改
- 修复后立即验证
- 写入 `taskHistory` 时标注"根因"和"修复方案"供下次参考

---

## 输出报告

CP4 完成后输出：
```
## ✅ Bug 修复报告

**Bug**: [描述]
**分支**: [branch-name]
**根因**: [描述]
**复杂度**: [Low/Medium/High]
**修复耗时**: [X小时]

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

### 回归测试
- [ ] [测试场景1] — 通过
- [ ] [测试场景2] — 通过
```

---

## 命令速查

```bash
harness state start <bug>         # 开始任务（CP0 检索相似bug修复历史）
harness verify                     # 运行全部 Gate
harness heal [--dry-run]           # CP4 自愈循环
harness heal on|off|status         # 管理自愈功能
harness state done                 # 完成任务，写入 taskHistory
harness state blocked <原因>       # 报告阻塞
```
