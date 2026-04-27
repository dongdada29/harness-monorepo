# Basic Template — Constraints

> 基础模板约束，适合简单项目

---

## 绝对禁止

- ❌ 不读 `state.json` 就开始
- ❌ 不确认任务范围就实现
- ❌ 跳过 `/verify`
- ❌ 一次改超过 5 个文件
- ❌ 不更新 `state.json` 就结束

---

## 必须执行

### Session 开始
```
1. 读 harness/feedback/state/state.json
2. 读 harness/base/constraints.md
```

### 任务结束
```
1. /verify 通过
2. /done
```

---

## 代码规范

| 规则 | 限制 |
|------|------|
| 函数长度 | < 60 行 |
| 文件长度 | < 400 行 |

---

## Gates

Gate 1: npm run lint → ESLint 通过
Gate 2: npx tsc --noEmit → TypeScript 无错误
Gate 3: npm test → 测试通过
Gate 4: npm run build → 构建通过