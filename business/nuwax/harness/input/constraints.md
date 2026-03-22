# Nuwax 项目约束规则

## 绝对禁止

- ❌ 不读 state.json 就开始
- ❌ 不确认任务范围就实现
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 不更新 state 就结束
- ❌ 遇到阻塞不汇报
- ❌ 直接在组件内写请求（必须放 services/）
- ❌ 组件内直接写 console.log
- ❌ 不用 useMemo/useCallback 优化
- ❌ 提交包含敏感信息

## 必须执行

### 代码规范
- ✅ 使用 Ant Design ProComponents
- ✅ 复杂交互用 AntV X6
- ✅ 所有 API 请求封装到 services/
- ✅ 组件有详细注释
- ✅ Props/State 有类型注解
- ✅ 使用 useMemo/useCallback 优化性能

### 文件规范
- ✅ 组件放 components/
- ✅ 页面放 pages/
- ✅ API 封装放 services/
- ✅ 全局状态用 models/
- ✅ 工具函数放 utils/

### 质量规范
- ✅ /verify 全部通过
- ✅ ESLint 0 errors
- ✅ TypeScript 0 errors
- ✅ 测试通过

---

## UmiJS 特定约束

### 路由规范
- 使用 UmiJS 约定式路由
- 页面组件放在 pages/ 目录
- 路由懒加载

### 插件规范
- 使用 UmiJS 插件体系
- 插件放 plugins/ 目录

---

## UI 组件规范

### Ant Design
- 优先使用 ProComponents
- 表格用 ProTable
- 表单用 ProForm
- 弹窗用 ProModal

### AntV X6
- 图形组件封装
- 自适应容器大小
- 节点/边定义清晰

---

## 违规处理

```
检测到违规 → 停止 → 修复 → 继续
```

多次违规 → 重读本文件
