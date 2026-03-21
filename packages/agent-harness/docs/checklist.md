# 开发检查清单

## 开始新任务

- [ ] `/start <任务名>` 开始任务
- [ ] 确认任务范围
- [ ] 确认没有超过 5 个文件

## 实现阶段

- [ ] 按约束实现
- [ ] 遵守架构分层
- [ ] 小步验证

## 验证阶段

- [ ] `/verify` 全部通过
- [ ] lint: 0 errors
- [ ] typecheck: 0 errors
- [ ] test: all passed
- [ ] build: passed

## 代码审查

- [ ] `/review <文件>` 完成自审
- [ ] 无严重问题
- [ ] 人类 approve（如果需要）

## 完成阶段

- [ ] `/done` 完成任务
- [ ] state.json 已更新
- [ ] history 已记录
- [ ] commit message 清晰

## 提交规范

- [ ] commit message 格式正确
- [ ] 无 console.log
- [ ] 无敏感信息
- [ ] 无调试代码
- [ ] 覆盖率 >= 80%

---

## 常见错误

### ❌ 不应该做的

1. 不读 state.json 就开始
2. 跳过 /verify
3. 一次改太多文件
4. 不更新 state 就结束
5. 遇到阻塞不汇报

### ✅ 正确做法

1. 先 `/state` 了解情况
2. 每步 `/verify`
3. 分多次改动
4. 完成后 `/done`
5. 阻塞用 `/blocked`
