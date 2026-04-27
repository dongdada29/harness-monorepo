# Feature Development Workflow
> CP0 → CP1 → CP2 → CP3 → CP4 全流程指令

---

## Step 0: Read Harness State

```bash
cat harness/feedback/state/state.json
```

读取当前 checkpoint 状态和 autonomy level，确认任务范围。

---

## Step 1: CP0 — Init (Initialize)

**目标**: 解析任务、拆解目标、判断复杂度

### 1.1 解析任务
- 读需求文档 / issue 描述
- 提取功能点，列出 TODO
- 识别依赖（外部 API、库、其他模块）

### 1.2 复杂度判断
| 复杂度 | 标准 | Agent 行为 |
|--------|------|-----------|
| Low | 改1-2个文件，<50行 | Agent 直接执行 |
| Medium | 涉及多文件，需要设计 | Agent 规划后执行 |
| High | 跨模块，影响核心逻辑 | 人类确认后再执行 |

### 1.3 写 CP0 记录
```bash
# 更新 state.json — CP0
harness state cp CP0 completed
```

### 1.4 人类确认（仅 High 复杂度）
```
## CP0 报告

**功能**: [描述]
**复杂度**: [Low/Medium/High]
**涉及文件**: [列表]
**依赖**: [列表]

等待确认后继续...
```

---

## Step 2: CP1 — Plan (任务规划)

**目标**: 制定实现计划，确定范围和顺序

### 2.1 读约束
```bash
cat harness/base/constraints.md
cat harness/overlay/constraints.md 2>/dev/null || true
```

### 2.2 制定计划
按以下顺序规划：

1. **接口设计**（如有 API 变更）
   - 明确输入/输出
   - 列出需要新增或修改的接口

2. **数据层变更**（如有）
   - Schema 变更
   - 数据迁移

3. **业务逻辑实现**
   - 按模块拆分
   - 每个模块 < 100 行核心逻辑

4. **测试计划**
   - 单元测试覆盖
   - 集成测试场景

### 2.3 写计划到 state.json
```bash
harness state cp CP1 completed
```

### 2.4 范围确认
```
## CP1 计划

**实现顺序**:
1. [步骤1]
2. [步骤2]
3. [步骤3]

**验收标准**:
- [标准1，可测试]
- [标准2，可测试]

**不包括**:
- [排除项]

等待确认后继续...
```

---

## Step 3: CP2 — Execute (实现)

**目标**: 按计划实现，遵守约束，小步验证

### 3.1 约束检查清单（每次修改前）
- [ ] 符合 `constraints.md` 规则
- [ ] 不含 `console.log` / `debugger`
- [ ] 不含硬编码值（配置要外置）
- [ ] 不直接删除文件（用 `trash` 或备份）
- [ ] 网络请求需要明确用途

### 3.2 小步提交规则
每完成一个小功能点，commit 一次：

```bash
git add .
git commit -m "feat: [功能] [简短描述]

- [改动点A]
- [改动点B]"
```

### 3.3 增量验证
每完成一个子模块，立即验证：

```bash
# Lint
shellcheck scripts/*.sh
npm run lint 2>/dev/null || true

# Type check
npm run typecheck 2>/dev/null || true

# Test
npm run test 2>/dev/null || true
```

### 3.4 遇到阻塞
```bash
harness state blocked "[原因描述]"
harness state done  # 不可行时标记任务结束
```

### 3.5 完成标记
```bash
harness state cp CP2 completed
```

---

## Step 4: CP3 — Verify (验证)

**目标**: 全部质量门禁通过

### 4.1 运行 Verify 脚本
```bash
cd "$(git rev-parse --show-toplevel)"
bash packages/agent-harness/scripts/verify.sh
```

### 4.2 逐项门禁检查

| Gate | 检查项 | 通过标准 |
|------|--------|---------|
| lint | shellcheck / eslint | 0 errors |
| typecheck | tsc --noEmit | 0 errors |
| test | npm test | 全部通过 |
| build | npm run build | 0 errors |

### 4.3 代码质量检查
```bash
# 无 console.log
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" || true

# 无 debugger
grep -rn "debugger" src/ --include="*.ts" --include="*.tsx" || true

# 无敏感信息
grep -rn "password\|secret\|api_key\|token" src/ --include="*.ts" --include="*.tsx" || true
```

### 4.4 Benchmark 自评
```bash
python3 tools/benchmark/runner.py --project . --output text
```

### 4.5 门禁通过后
```bash
harness state gate verify passed
harness state cp CP3 completed
```

---

## Step 5: CP4 — Complete (完成)

### 5.1 更新 State
```bash
harness state done
harness state cp CP4 completed
```

### 5.2 输出报告

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
- Grade: [S/A/B/C...]

### Autonomy
- Level: [Lx]
- 人工介入: [是/否]

### 下一步
- [可选：后续改进建议]
```

### 5.3 打开 PR（如果适用）
```bash
harness open-pr -l [level]
# 或手动:
./scripts/open-pr.sh -l [level]
```

---

## 完整命令速查

```bash
# 状态管理
harness state cp CP0 completed   # 标记 CP0 完成
harness state cp CP1 completed   # 标记 CP1 完成
harness state cp CP2 completed   # 标记 CP2 完成
harness state cp CP3 completed   # 标记 CP3 完成
harness state cp CP4 completed   # 标记 CP4 完成
harness state done               # 标记任务完成
harness state blocked "[原因]"   # 标记阻塞

# 门禁
harness state gate lint passed
harness state gate typecheck passed
harness state gate test passed
harness state gate build passed
harness state gate verify passed

# PR
harness open-pr -l 4             # L4: 开 PR，人工 merge
harness open-pr -l 5             # L5: 开 PR，CI 后自动 merge
```
