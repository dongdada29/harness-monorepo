# CP4 自愈循环 (Self-Healing Loop)

> **版本**: 1.0.0  
> **日期**: 2026-04-30  
> **目标**: Gate 失败后自动尝试修复并重新验证，直到通过或达到最大重试次数

---

## 1. 背景问题

当前 `verify` 命令的行为：
```
Gate 失败 → 输出错误 → 退出
```

问题：
- Agent 需要手动重新运行 verify
- 没有记录修复尝试历史
- 无法区分"一直失败"和"需要多次尝试"

---

## 2. 自愈循环定义

### 2.1 流程

```
CP3 Verify
    │
    ├── Gates 全部通过 ──→ CP4 完成 ✅
    │
    └── Gates 失败 ──→ CP4 自愈循环 🔄
                            │
                            ├─→ 分析失败原因
                            ├─→ 尝试修复 (healing attempt)
                            ├─→ 重新验证
                            │
                            ├─→ 通过 ──→ CP4 完成 ✅
                            │
                            └─→ 失败 ──→ max attempts?
                                      ├── 未达上限 ──→ 继续尝试 🔄
                                      └── 达到上限 ──→ 退出，请求人工介入 ❌
```

### 2.2 核心概念

| 概念 | 说明 |
|------|------|
| **healing attempt** | 一次修复尝试（不限一次修复，可能多个文件的改动） |
| **healing cycle** | 一次 attempt + 一次 re-verify |
| **max healing cycles** | 最大自愈循环次数，默认 3 |
| **healing budget** | 每次 attempt 的最大时间（防止无限修复） |

---

## 3. State Schema 更新

### 3.1 新增字段

```json
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "healing": {
    "enabled": true,
    "maxAttempts": 3,
    "currentAttempt": 0,
    "lastAttempt": null,
    "lastError": null,
    "retryHistory": [
      {
        "attempt": 1,
        "timestamp": "2026-04-30T14:00:00Z",
        "failedGates": ["lint"],
        "errorSummary": "unused variable 'x' in foo.ts",
        "filesTouched": ["src/foo.ts"],
        "status": "passed"  // or "failed"
      }
    ],
    "autoHeal": true
  }
}
```

### 3.2 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `enabled` | boolean | 是否启用自愈 |
| `maxAttempts` | number | 最大尝试次数 |
| `currentAttempt` | number | 当前尝试次数 |
| `lastAttempt` | ISO timestamp | 上次尝试时间 |
| `lastError` | string | 上次失败的原因摘要 |
| `retryHistory` | array | 所有尝试的历史 |
| `autoHeal` | boolean | 是否自动进入下次循环 |

---

## 4. 触发条件

### 4.1 自动触发

当以下条件全部满足时，自动进入自愈循环：

```
CP3 verify 失败 AND
  healing.enabled === true AND
  currentAttempt < maxAttempts AND
  autonomy.level >= 3
```

### 4.2 手动触发

```bash
harness heal           # 进入自愈循环
harness heal --dry-run # 只分析，不修复
harness heal --force   # 强制进入（无视 maxAttempts）
```

---

## 5. 自愈策略

### 5.1 错误分类与响应

| 错误类型 | 策略 |
|----------|------|
| **lint error** | 分析错误，定位文件，修复后重新 lint |
| **typecheck error** | 分析类型错误，修复类型定义，重新 tsc |
| **test failed** | 分析测试失败原因，修复代码或测试，重新跑 |
| **build failed** | 分析构建错误，修复依赖或配置，重新构建 |
| **runtime error** | 分析错误栈，定位问题，修复后重新运行 |

### 5.2 修复优先级

```
1. 最小改动原则：只改必要的文件
2. 单文件优先：问题能在一个文件内解决，不动多个文件
3. 测试优先：如果是测试本身的问题，优先修测试
4. 配置次之：最后才动配置文件
```

### 5.3 不自愈的情况

```
✗ 网络请求失败
✗ 权限问题
✗ 外部依赖不可用
✗ 涉及 API 破坏性变更
✗ 超过 maxAttempts
```

---

## 6. 实施

### 6.1 文件变更

| 文件 | 变更 |
|------|------|
| `core/harness/feedback/healing-loop.md` | 本文档 |
| `packages/agent-harness/index.js` | 新增 `heal` 命令和自愈逻辑 |
| `packages/cli/bin/harness.js` | 新增 `heal` CLI 命令 |
| `core/harness/feedback/state/state.json` | 更新 schema（见 3.1） |

### 6.2 CLI 命令

```bash
harness heal              # 启动自愈循环
harness heal --dry-run    # 分析失败原因，不修复
harness heal --force      # 强制重试（无视上限）
harness heal --max <n>    # 设置最大尝试次数
```

### 6.3 退出码

| 退出码 | 含义 |
|--------|------|
| 0 | 自愈成功，所有 gates 通过 |
| 1 | 自愈失败（达到最大次数） |
| 2 | 自愈被禁用 |
| 3 | 无失败需要自愈 |

---

## 7. 与其他模块的关系

```
healing-loop.md
    │
    ├─→ autonomy.md (L3+ 才能自愈)
    │
    ├─→ memory-retrieval.md (查历史修复经验)
    │
    └─→ logging.md (记录修复日志)
```

---

## 8. 变更记录

| 日期 | 版本 | 变更 |
|------|------|------|
| 2026-04-30 | 1.0.0 | 初始版本 |
