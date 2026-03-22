# React Best Practices Skill

> Web Tech Stack: React + TypeScript  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Component Patterns

### 1.1 函数组件优先

```tsx
// ✅ Good
function UserCard({ user }: { user: User }) {
  return <div>{user.name}</div>;
}

// ❌ Bad
class UserCard extends Component {}
```

### 1.2 Hooks 规则

```tsx
// ✅ 顶层调用
function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  return { user, setUser };
}
```

---

## 2. TypeScript 规则

### 2.1 显式类型

```tsx
// ✅ Good
interface Props {
  name: string;
  age?: number;
}

// ❌ Bad
const UserCard = (props) => <div>{props.name}</div>;
```

### 2.2 泛型约束

```tsx
// ✅ Good
function fetchData<T>(url: string): Promise<T> {
  return fetch(url).then(res => res.json());
}
```

---

## 3. 状态管理

### 3.1 Zustand (推荐)

```ts
import { create } from 'zustand';

interface Store {
  user: User | null;
  setUser: (user: User) => void;
}

export const useStore = create<Store>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));
```

### 3.2 React Query (数据获取)

```ts
const { data, isLoading } = useQuery({
  queryKey: ['user', userId],
  queryFn: () => fetchUser(userId),
});
```

---

## 4. 性能优化

| 场景 | 方案 |
|------|------|
| 组件重渲染 | React.memo |
| 状态变化 | useMemo / useCallback |
| 大列表 | 虚拟滚动 |
| API 缓存 | React Query |

---

## 5. 目录结构

```
src/
├── components/       # 组件
├── hooks/           # 自定义 Hooks
├── pages/           # 页面
├── services/        # API
├── stores/          # 状态
└── types/          # 类型定义
```
