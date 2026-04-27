# Bug Fix Workflow
> CP0 → CP1 → CP2 → CP3 → CP4 全流程指令

---

## Step 0: Read Harness State

```bash
cat harness/feedback/state/state.json
```

---

## Step 1: CP0 — Init (收集信息)

**目标**: 确认 bug 信息，评估严重程度

### 1.1 收集信息
```
**Bug 描述**:
- 错误信息: [粘贴错误日志]
- 复现步骤: [第1步...第N步]
- 预期行为: [应该发生什么]
- 实际行为: [实际发生了什么]
```

### 1.2 严重程度判断

| 等级 | 影响 | 响应 |
|------|------|------|
| 🔴 P0 | 功能完全不可用 / 数据损坏 | 立即修复 |
| 🟠 P1 | 核心功能受影响 | 当天修复 |
| 🟡 P2 | 非核心功能 bug | 计划内修复 |
| 🟢 P3 | 体验问题 | 下个迭代 |

### 1.3 相关代码定位
```bash
# 搜错误关键字
grep -rn "ERROR_KEYWORD" src/ --include="*.ts" --include="*.tsx"

# 查最近 git 改动
git log --oneline -10 --all
git diff HEAD~3 --name-only

# 查 blame
git blame [file]
```

### 1.4 记录 CP0
```bash
harness state cp CP0 completed
```

---

## Step 2: CP1 — Root Cause Analysis (根因分析)

**目标**: 找到根本原因，不是表象

### 2.1 分析方法

**5 Why 分析法**:
```
问题: [描述]
Why 1: [原因] → Why 2: [原因] → Why 3: [原因] → Why 4: [原因] → Why 5: [根因]
```

**假设验证法**:
1. 提出假设: "可能是 X 导致的"
2. 验证: 加日志 / 断点 / 读代码
3. 排除或确认
4. 重复直到找到根因

### 2.2 输出根因报告
```
## 根因分析

**Bug**: [标题]
**严重程度**: [P0/P1/P2/P3]
**根因**: [一句话描述]

**因果链**:
1. [直接原因]
2. [中间原因]
3. [根本原因]

**受影响范围**:
- [模块A]
- [模块B]
```

### 2.3 记录 CP1
```bash
harness state cp CP1 completed
```

---

## Step 3: CP2 — Fix (修复)

**目标**: 修复根因，遵守约束

### 3.1 修复原则
- **修复根因**，不只修表象
- **最小改动**，不引入额外变更
- **测试优先**，先写测试再改代码（如果可行）

### 3.2 约束检查
- [ ] 不含 `console.log` / `debugger`
- [ ] 不引入新的 lint 错误
- [ ] 不降低现有测试覆盖率
- [ ] 修复后复现步骤验证通过

### 3.3 验证修复
```bash
# 复现 bug（修复前）
[复现命令]

# 修复后重新运行
[验证命令]

# 回归测试
npm run test 2>/dev/null || true
```

### 3.4 Commit
```bash
git add .
git commit -m "fix: [一句话描述bug和修复]

Root cause: [根本原因]
Fix: [修复方法]
Test: [验证方式]"
```

### 3.5 记录 CP2
```bash
harness state cp CP2 completed
```

---

## Step 4: CP3 — Verify (验证)

**目标**: 全部门禁通过

### 4.1 运行 Verify
```bash
bash packages/agent-harness/scripts/verify.sh
```

### 4.2 门禁清单

| Gate | 检查 |
|------|------|
| lint | 0 errors |
| typecheck | 0 errors |
| test | 全部通过 |
| build | 0 errors |

### 4.3 回归测试
确认 bug 修复不影响其他功能。

### 4.4 Benchmark 自评
```bash
python3 tools/benchmark/runner.py --project . --output text
```

### 4.5 记录 CP3
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
## 🐛 Bug 修复报告

**Bug**: [标题]
**严重程度**: [P0/P1/P2/P3]
**分支**: [branch-name]
**根因**: [一句话]
**修复方式**: [方法]

### 变更文件
- [file]:[行号] — [改动]

### 验证
- [ ] 复现步骤现在通过
- [ ] 回归测试全部通过

### 门禁
| Gate | Result |
|------|--------|
| lint | ✅ |
| test | ✅ |
| build | ✅ |

### Autonomy
- Level: [Lx]
```

### 5.3 打开 PR
```bash
harness open-pr -l 4
```
