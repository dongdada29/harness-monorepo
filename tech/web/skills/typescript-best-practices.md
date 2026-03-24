# TypeScript Best Practices Skill

> Tech Stack: TypeScript  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 类型定义

### 接口 vs 类型别名

```ts
// 接口 - 推荐用于对象
interface User {
  id: number;
  name: string;
}

// 类型别名 - 用于联合类型
type Status = 'active' | 'inactive' | 'pending';
```

---

## 2. 泛型

```ts
// 泛型函数
function identity<T>(arg: T): T {
  return arg;
}

// 泛型约束
function getProperty<T, K extends keyof T>(obj: T, key: K) {
  return obj[key];
}
```

---

## 3. 实用类型

| 类型 | 说明 |
|------|------|
| `Partial<T>` | 所有属性可选 |
| `Required<T>` | 所有属性必需 |
| `Pick<T, K>` | 选取部分属性 |
| `Omit<T, K>` | 排除部分属性 |
| `Record<K, V>` | 键值对对象 |

---

## 4. 错误处理

```ts
// Result 类型
type Result<T, E = Error> = 
  | { ok: true; value: T }
  | { ok: false; error: E };

function safeParse(json: string): Result<unknown> {
  try {
    return { ok: true, value: JSON.parse(json) };
  } catch (e) {
    return { ok: false, error: e as Error };
  }
}
```

---

## 5. 模块

```ts
// 导出
export interface User { ... }
export type Status = 'active' | 'inactive';

// 导入
import { User, Status } from './types';
import type { User } from './types';
```

---

## 6. 配置

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "exactOptionalPropertyTypes": true
  }
}
```
