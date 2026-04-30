# Feature — Task Spec

> Basic 模板任务定义

---

## 任务类型

**Feature** — 新功能开发

---

## 触发条件

```
harness state start <功能描述>
```

---

## 执行流程

### CP0 — Init
- [ ] 理解功能需求
- [ ] 确认涉及文件数（≤5 个）
- [ ] 判断复杂度（Low = 1-2文件，直接执行）

### CP1 — Plan
- [ ] 列出要改的文件
- [ ] 确认接口/类型
- [ ] 确认不包含的范围

### CP2 — Exec
- [ ] 按顺序实现
  1. 类型/接口定义
  2. 核心逻辑
  3. 测试
- [ ] 每步 `harness verify`

### CP3 — Verify
- [ ] `harness verify` 全部通过
- [ ] 无 console.log / debugger
- [ ] Benchmark 自评

### CP4 — Complete
- [ ] `harness state done`
- [ ] 写入 taskHistory

---

## 验收标准

- 代码可运行
- 测试通过
- lint / typecheck 通过
- 无硬编码敏感信息
