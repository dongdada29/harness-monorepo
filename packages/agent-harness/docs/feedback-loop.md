# 反馈回路实践

> 版本: 2.0.0 — 集成 CP4 自愈循环

---

## 核心概念

反馈回路 = Agent 看到自己的输出结果 + 调整行为

Harness 通过三层反馈实现：

| 层次 | 反馈源 | 响应 |
|------|--------|------|
| **Gate 反馈** | lint / typecheck / test / build | 失败 → 修复 → 重验证 |
| **Memory 反馈** | taskHistory / healing.retryHistory | 查历史相似任务，复用修复方案 |
| **Autonomy 反馈** | L1-L9 等级 | 决定何时需要人工介入 |

---

## 反馈时机

### CP0 INIT — Memory 检索（必须）

```
任务开始
  └─→ 查询 state.json
        ├─ taskHistory         → 最近相似任务的解决方案
        └─ healing.retryHistory → 历史修复经验
```

### CP3 VERIFY 失败 → CP4 自愈循环

```
Gate 失败
  │
  ├─ 查 healing.retryHistory（同类错误以前怎么修的）
  │
  ├─ 修复失败的 gate
  │
  ├─ harness heal   # 重新跑验证
  │
  └─ 通过 → 继续
      失败 → 最多重试 3 次
```

### CP2 EXEC 阻塞

```
阻塞 30 分钟
  │
  ├─ 查 healing.retryHistory
  └─ 查同类错误的修复记录
      │
      └─ 有 → 复用方案
          无 → 升级到 L3 人工介入
```

---

## 会话流程

```
1. harness state start <任务>   # CP0 INIT：检索相似历史
2. CP1 → CP2 → CP3
3. Gate 失败？
   │
   ├─ 否 → 完成
   └─ 是 → CP4 自愈循环
              │
              ├─ 修复 → harness heal
              ├─ 通过 → 完成
              └─ 失败 → 重试（最多3次）
4. harness state done             # 写入 taskHistory
```

---

## Memory 反馈数据流

```
Agent 执行任务
    │
    ├─ 成功 → harness done → taskHistory 追加记录
    │
    └─ 失败（heal 成功）→ retryHistory 追加 [status: passed]
    └─ 失败（heal 失败）→ retryHistory 追加 [status: failed]
```

下次任务开始时，CP0 会自动检索这些历史。

---

## 验证练习

```bash
# 1. 查看当前状态
harness state show

# 2. 开始任务
harness state start "添加用户头像上传"

# 3. CP0 自动检索相似历史
#    查看有哪些可以复用的经验

# 4. 执行中遇到 Gate 失败
harness verify
#  ❌ Gate lint failed

# 5. 进入自愈循环
harness heal
#  → 修复 → 重验证 → 通过或继续修复

# 6. 完成任务
harness state done
#  → taskHistory 追加记录
```
