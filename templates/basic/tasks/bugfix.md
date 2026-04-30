# Bug Fix — Task Spec

> Basic 模板任务定义

---

## 任务类型

**Bugfix** — Bug 修复

---

## 触发条件

```
harness state start <bug描述>
```

---

## 执行流程

### CP0 — Init
- [ ] 理解预期行为 vs 实际行为
- [ ] 确认复现步骤
- [ ] 确认涉及文件

### CP1 — Plan
- [ ] 定位问题根源
- [ ] 制定修复方案
- [ ] 确认最小改动原则

### CP2 — Exec
- [ ] 修复问题
- [ ] 保持改动最小化
- [ ] 添加 regression 测试

### CP3 — Verify
- [ ] `harness verify` 全部通过
- [ ] 复现步骤验证通过
- [ ] Benchmark 自评

### CP4 — Complete
- [ ] `harness state done`
- [ ] 写入 taskHistory

---

## 约束

- 只改必要的文件
- 不引入新功能
- 不做代码风格大面积修改
- 修复后立即验证
