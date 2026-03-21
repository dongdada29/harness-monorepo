# Base Constraints - 通用约束

> 适用于所有 Agent 和所有项目

---

## 绝对禁止

- ❌ 不读 `state.json` 就开始写代码
- ❌ 不确认任务范围就自行实现
- ❌ 跳过 `/verify` 直接说"完成"
- ❌ 一次改超过 5 个文件
- ❌ 不更新 `state.json` 就结束 session
- ❌ 遇到阻塞不汇报继续硬做
- ❌ 删除文件（除非人类明确授权）
- ❌ 提交包含 `console.log`、`debugger`、调试代码
- ❌ 提交包含敏感信息（API keys、passwords）
- ❌ commit message 写 "WIP"、"fixed stuff"

---

## 必须执行

### Session 开始
```bash
1. 读取 harness/feedback/state/state.json
2. 读取 harness/base/constraints.md
3. 读取项目约束（harness/projects/{类型}/constraints.md）
```

### 任务开始
```bash
1. /start <任务描述>
2. 确认任务范围
3. 获得人类确认
```

### 执行中
```bash
1. 每步运行 /verify
2. 遇到阻塞立即 /blocked
3. 保持 state.json 更新
```

### 任务结束
```bash
1. /verify 全部通过
2. /review 自审
3. 人类 approve
4. /done
5. 更新 state.json
```

---

## 质量门禁

### TypeScript/React
```bash
Gate 1: npm run lint       → eslint
Gate 2: npm run typecheck → tsc --noEmit
Gate 3: npm test           → vitest/jest
Gate 4: npm run build    → vite build
```

### Python
```bash
Gate 1: ruff check .   → 0 errors
Gate 2: mypy .         → 0 errors
Gate 3: pytest         → all pass
Gate 4: python -m py_compile
```

### Go
```bash
Gate 1: golangci-lint run → 0 errors
Gate 2: go vet ./...     → 0 errors
Gate 3: go test ./...    → all pass
Gate 4: go build ./...   → 0 errors
```

### Rust
```bash
Gate 1: cargo clippy   → 0 warnings
Gate 2: cargo check     → 0 errors
Gate 3: cargo test     → all pass
Gate 4: cargo build   → 0 errors
```

---

## 代码规范

| 规则 | 限制 |
|------|------|
| 函数长度 | < 50 行 |
| 文件长度 | < 300 行 |
| 圈复杂度 | < 10 |

---

## 违规处理

```
检测到违规 → 立即停止 → 修复 → 继续
```

多次违规 → 重读本文件
