# Advanced Template — Constraints

> 高级模板约束，适合复杂项目

---

## 绝对禁止

- ❌ 不读 `state.json` 就开始
- ❌ 不确认任务范围就实现
- ❌ 跳过 `/verify`
- ❌ 一次改超过 3 个文件
- ❌ 不更新 `state.json` 就结束
- ❌ 遇到阻塞不汇报
- ❌ 删除文件（除非明确授权）
- ❌ 提交 `console.log`、`debugger`、调试代码
- ❌ 提交敏感信息（API keys、passwords）
- ❌ 绕过 code review

---

## 必须执行

### Session 开始
```
1. 读 harness/feedback/state/state.json
2. 读 harness/base/constraints.md
3. 读 harness/overlay/constraints.md (如存在)
```

### 任务开始
```
1. harness state start <task>
2. 确认范围
3. 获得确认（Medium/High 复杂度）
```

### 执行中
```
1. 每步 /verify
2. 遇到阻塞 harness state blocked <reason>
3. 保持 state 更新
```

### 任务结束
```
1. /verify 通过
2. /review 自审
3. 人类 approve
4. harness state done
```

---

## 代码规范

| 规则 | 限制 |
|------|------|
| 函数长度 | < 50 行 |
| 文件长度 | < 300 行 |
| 圈复杂度 | < 10 |
| 测试覆盖率 | > 70% |

---

## Gates

Gate 1: npm run lint → ESLint 通过
Gate 2: npx tsc --noEmit → TypeScript 无错误
Gate 3: npm test → 测试通过
Gate 4: npm run build → 构建通过
Gate 5: git diff --stat → 无意外文件变更