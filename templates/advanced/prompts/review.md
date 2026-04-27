# Code Review Workflow
> Agent 自审 → 人类审查 → 合并

---

## 触发时机

- CP3 完成后，PR 打开前
- 人类要求 review 时
- 每次 push 后自动触发（CI）

---

## Step 1: Agent 自审

### 1.1 自审清单

**功能正确性**
- [ ] 代码实现了需求功能
- [ ] 边界条件全部处理
- [ ] 错误处理完善（有 try-catch / fallback）
- [ ] 空值 / 零值场景处理

**代码质量**
- [ ] 无重复代码（DRY 原则）
- [ ] 函数 < 60 行
- [ ] 变量命名清晰（不用 x, temp, data）
- [ ] 无硬编码值（配置外置）
- [ ] 无魔法数字（用常量替代）

**测试覆盖**
- [ ] 有对应单元测试
- [ ] 边界条件有测试
- [ ] 错误场景有测试
- [ ] 测试可读可维护

**安全**
- [ ] 无敏感信息硬编码（password / secret / token）
- [ ] 无 SQL / 命令注入风险
- [ ] 用户输入有校验

**提交规范**
- [ ] 无 `console.log` / `debugger`
- [ ] commit message 清晰（feat/fix/style/test）
- [ ] 无不必要的文件（临时文件、注释代码）

### 1.2 运行自检
```bash
# 代码质量扫描
grep -rn "console.log" src/ --include="*.ts" --include="*.tsx" || echo "clean"
grep -rn "debugger" src/ --include="*.ts" --include="*.tsx" || echo "clean"
grep -rn "password\|secret\|api_key\|token" src/ --include="*.ts" --include="*.tsx" || echo "clean"

# 复杂度检查（可选）
tokei src/ 2>/dev/null || true

# 变更统计
git diff --stat HEAD
```

### 1.3 输出自审报告
```
## 自审报告

### ✅ 通过
- [检查项A]
- [检查项B]

### ⚠️ 需要关注
- [建议项A — 说明]

### 🔴 阻塞问题
- [问题A — 必须修复才能合并]
```

---

## Step 2: 人类审查

### 2.1 审查关注点（人类）

**架构层面**
- 改动是否符合项目架构？
- 是否有更好的设计方案？

**业务层面**
- 是否符合业务需求？
- 边界场景是否考虑？

**长期维护**
- 代码是否易于理解和修改？
- 是否有技术债？

### 2.2 问题严重程度

| 等级 | 标记 | 说明 | 处理 |
|------|------|------|------|
| 阻塞 | 🔴 | 必须修，否则不能合并 | 立即修 |
| 应该修 | 🟡 | 强烈建议修 | 尽快修 |
| 可以修 | 🟢 | 建议修 | 下个迭代 |

---

## Step 3: 合并

### 3.1 Autonomy Level 决定行为

| Level | 行为 |
|-------|------|
| L1-L3 | Agent 自审 → 人类 merge |
| L4 | Agent 开 PR → 人类 merge |
| L5+ | Agent 开 PR → CI 通过后自动 merge |

### 3.2 合并条件
```
✅ 自审通过
✅ lint: 0 errors
✅ test: 全部通过
✅ build: 成功
✅ 人类 approve（L1-L4）
✅ CI 全部通过
```

### 3.3 合并命令（人类）
```bash
# 手动 merge
gh pr merge #PR_NUMBER --squash --delete-branch

# 或通过 GitHub UI
```

---

## 快速参考

```bash
# 自审
harness state gate verify passed   # 运行 verify.sh

# 看 diff
git diff main..HEAD

# 看提交历史
git log main..HEAD --oneline

# 搜索问题代码
grep -rn "console.log\|debugger" src/ --include="*.ts"

# 运行 benchmark
python3 tools/benchmark/runner.py --project . --output text
```
