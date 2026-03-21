# 架构约束规则

## 分层架构

```
Types → Config → Repo → Service → UI
```

## 依赖规则

1. **单向依赖**：只能依赖下一层，不能反向
2. **同层可互相引用**
3. **禁止跨层依赖**

## 验证命令

```bash
# 检查架构违规
npm run lint
```

## Lint 规则

在 `eslint.config.js` 中添加自定义规则：

```javascript
// 禁止跨层依赖
// types/ → config/ → repo/ → service/ → ui/
```

## 违规示例

```typescript
// ❌ 错误：UI 层直接依赖 Types
import type { HelloMessage } from '../types/hello';

// ✅ 正确：通过 Service 层获取
import { helloService } from '../services/hello';
```

## 测试覆盖率要求

- 新功能必须有对应测试
- 覆盖率 > 80% 才能合并
