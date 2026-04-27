# Bug Fix — Basic Prompt

> 基础 Bug 修复流程

---

## Step 1: Read State

```bash
cat harness/feedback/state/state.json
```

## Step 2: Investigate

收集信息：
- 错误日志
- 复现步骤
- 预期 vs 实际行为

## Step 3: Locate

```bash
grep -rn "ERROR_KEYWORD" src/ --include="*.ts"
git log --oneline -5
```

## Step 4: Fix

定位后修改，保持改动最小化。

## Step 5: Verify

```bash
npm run lint && npm test
```

## Step 6: Done

```
harness state done
```