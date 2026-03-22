# Bug 修复模板 - Nuwax

## Bug 信息

```markdown
## Bug 标题


## Bug ID
<!-- auto-generated -->

## 严重程度
- [ ] critical (崩溃、数据丢失)
- [ ] high (功能完全不可用)
- [ ] medium (功能受损)
- [ ] low (UI 问题)
```

---

## 问题描述

```markdown
## 问题
<!-- 描述问题 -->

## 复现步骤
1. 
2. 
3. 

## 预期行为
<!-- 期望的正确行为 -->

## 实际行为
<!-- 实际的错误行为 -->

## 错误日志

**控制台：**
```
```

**网络请求：**
```
```

**堆栈信息：**
```
```
```

---

## 根因分析

```markdown
## 根因
<!-- 分析根本原因 -->

## 代码位置
- 文件：
- 函数：
- 行号：
```

---

## 修复方案

```markdown
## 修复描述


## 修改内容

```typescript
// 修改文件：src/xxx.tsx
// 修改前：
function xxx() {
  // old code
}

// 修改后：
function xxx() {
  // new code
}
```

---

## Nuwax 特定检查

```markdown
### 可能原因
- [ ] React 组件渲染问题
- [ ] UmiJS 路由问题
- [ ] Ant Design 组件问题
- [ ] API 请求问题
- [ ] 状态管理问题
- [ ] SSE 连接问题
- [ ] AntV X6 图形问题

### 相关模块
- [ ] src/pages/
- [ ] src/components/
- [ ] src/models/
- [ ] src/services/
- [ ] src/hooks/
- [ ] src/utils/sseManager.ts
```

---

## 验证

```markdown
## 复现验证
<!-- 修复后验证能复现问题 -->
- [ ] 问题不复现

## 回归测试
- [ ] 相关功能正常
- [ ] 无新的 lint 错误
- [ ] TypeScript 编译通过
- [ ] 测试通过
```

---

## 状态

```markdown
- [ ] pending
- [ ] in_progress
- [ ] verifying
- [ ] completed
```
