# 架构设计

## 分层架构

```
Types → Config → Repo → Service → UI
```

## 每一层职责

### Types (types/)
- 数据模型定义
- 接口类型
- 常量枚举

### Config (config/)
- 环境配置
- 默认值
- 验证规则

### Repo (repo/)
- 数据访问层
- 外部 API 封装
- 缓存逻辑

### Service (services/)
- 业务逻辑
- 数据转换
- 工作流编排

### UI (ui/)
- React 组件
- 页面路由
- 用户交互

## 依赖规则

- 同层可互相引用
- 只能向上层依赖（UI → Service → Repo...）
- 禁止反向依赖
- 跨层依赖通过接口抽象

## 验证

运行 `npm run lint` 检查架构违规
