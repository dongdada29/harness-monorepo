# CLAUDE.md - Nuwax Agent OS 开发规范

> 本文件在项目根目录，Claude Code 启动时**自动加载**

---

## 项目概述

**Nuwax Agent OS** - 通用智能体操作系统

### 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | React 18 + UmiJS Max |
| UI 组件 | Ant Design (优先 ProComponents) |
| 图形引擎 | AntV X6 |
| 状态管理 | Zustand / UmiJS model |
| 样式 | CSS Modules / Less |
| 包管理 | pnpm |
| 类型 | TypeScript |

### 目录结构

```
src/
├── components/      # 通用组件
├── pages/          # 页面
├── models/         # UmiJS model (全局状态)
├── hooks/          # 自定义 Hooks
├── services/       # API 请求封装
├── utils/          # 工具函数
├── constants/      # 常量
├── contexts/       # React Context
├── layouts/        # 布局组件
├── locales/        # 国际化
├── routes/         # 路由配置
├── plugins/        # UmiJS 插件
├── types/          # 类型定义
└── wrrappers/      # 封装组件
```

---

## 立即行动

```
1. 读取 harness/feedback/state/state.json
2. 读取 harness/input/constraints.md
3. 确认当前任务
```

---

## 开发约束

### 绝对禁止

- ❌ 不读 state.json 就开始
- ❌ 不确认范围就实现
- ❌ 跳过 /verify
- ❌ 一次改超过 5 个文件
- ❌ 不更新 state 就结束
- ❌ 遇到阻塞不汇报
- ❌ 直接在组件内写请求（必须放 services/）
- ❌ 组件内直接写 console.log
- ❌ 不用 useMemo/useCallback 优化

### 必须执行

- ✅ 使用 Ant Design ProComponents
- ✅ 复杂组件用 AntV X6
- ✅ 所有请求封装到 services/
- ✅ 组件有详细注释
- ✅ Props/State 有类型注解

---

## 五阶段工作流

```
CP1 → CP2 → CP3 → CP4 → CP5
任务确认 → 规划分解 → 执行实现 → 质量门禁 → 审查完成
```

---

## 核心命令

| 命令 | 作用 |
|------|------|
| `/state` | 显示状态 |
| `/start <任务>` | 开始任务 |
| `/verify` | 运行门禁 |
| `/test` | 运行测试 |
| `/review <文件>` | 代码审查 |
| `/done` | 完成任务 |
| `/blocked <原因>` | 报告阻塞 |
| `/metrics` | 显示指标 |
| `/history` | 查看历史 |

---

## 质量门禁

```
Gate 1: npm run lint     → 0 errors
Gate 2: npm run typecheck → 0 errors
Gate 3: npm test          → all pass
Gate 4: npm run build     → 0 errors
```

---

## 相关文档

- `harness/input/projects/nuwax.md` - Nuwax 项目规范
- `docs/architecture.md` - 架构设计
- `docs/components.md` - 组件规范
- `prompts/tasks/` - 任务模板
