# Generic Harness Constraints

> Platform: Generic  
> Version: 1.0.0  
> 更新: 2026-03-25

---

## 1. Overview

通用项目 Harness 模板，适用于任何 Node.js/TypeScript 项目。

---

## 2. Commands

### Auto-Approve
```bash
npm run dev              # 开发模式
npm run build            # 构建
npm run typecheck        # 类型检查
```

### Need Confirm
```bash
npm add <pkg>          # 添加包
git commit -m <msg>     # 提交
```

### Blocked
```bash
npm install -g           # 全局安装
```

---

## 3. Gates

```
npm run lint → npm run typecheck → npm test → npm run build
```

| Gate | Command | Threshold |
|------|---------|-----------|
| Lint | `npm run lint` | 0 errors |
| Typecheck | `npm run typecheck` | 0 errors |
| Test | `npm test` | 0 failures |
| Build | `npm run build` | success |

---

## 4. Testing

| 类型 | 工具 |
|------|------|
| 单元测试 | Jest / Vitest |
| 覆盖率目标 | 80%+ |

---

## 5. Skills

| Skill | 说明 |
|-------|------|
| `generic-workflow` | 通用工作流 |
