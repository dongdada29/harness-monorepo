# Quality Gates - 质量门禁

> 强制执行的验证检查，未通过不能算任务完成

---

## 门禁列表

### Gate 1: Lint Gate
```bash
npm run lint
```
- 必须：0 errors
- 警告可忽略（但建议修复）

### Gate 2: Type Check Gate
```bash
npx tsc --noEmit
```
- 必须：0 errors

### Gate 3: Unit Test Gate
```bash
npm test
```
- 必须：all tests passed
- 覆盖率 >= 80%

### Gate 4: Build Gate
```bash
npm run build
```
- 必须：0 errors

---

## 执行顺序

```
Gate 1 (Lint) → Gate 2 (Type) → Gate 3 (Test) → Gate 4 (Build)
```

任何 Gate 失败都停止，直到修复。

---

## 门禁豁免

**原则上不允许豁免。**

特殊情况需要人类授权，并记录在 commit message：
```
WARN: Gate bypass - [原因]
```

---

## 门禁脚本

使用 `scripts/verify.sh` 自动执行所有门禁：
```bash
./scripts/verify.sh
```
