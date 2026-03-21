# 反馈回路实践

## 概念

反馈回路 = Agent 看到自己的输出结果 + 调整行为

## 实现方式

### 1. 测试反馈
```bash
npm test
```
Agent 运行测试，失败则修复

### 2. Lint 反馈
```bash
npm run lint
```
Agent 看到格式问题，自动修复

### 3. 手动反馈
人类审查 PR，提出修改意见

## 会话流程

1. **读取 progress.json** → 了解当前进度
2. **执行任务** → 写代码
3. **运行验证** → test / lint
4. **更新 progress.json** → 记录完成
5. **提交 git** → 保存状态

## 验证练习

用 Claude Code 尝试以下任务：

1. 读取 docs/progress.json
2. 添加一个新功能：计算器
3. 运行 npm test 验证
4. 更新 progress.json
