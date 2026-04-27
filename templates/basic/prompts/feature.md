# Feature Development — Basic Prompt

> 基础功能开发流程

---

## Step 1: Read State

```bash
cat harness/feedback/state/state.json
```

## Step 2: Plan

理解任务，列出：
- 要改的文件
- 要加的逻辑
- 依赖项

## Step 3: Implement

按顺序：
1. 接口/类型定义
2. 核心逻辑
3. 测试

## Step 4: Verify

```bash
# Run gates
npm run lint && npx tsc --noEmit && npm test
```

## Step 5: Done

```
harness state done
```