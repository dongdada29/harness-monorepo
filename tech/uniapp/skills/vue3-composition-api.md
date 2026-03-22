# Vue 3 Composition API Skill

> Tech Stack: Vue 3 + Composition API  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Setup

```vue
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
</script>
```

---

## 2. 响应式

| API | 说明 |
|-----|------|
| `ref()` | 基本类型响应式 |
| `reactive()` | 对象响应式 |
| `computed()` | 计算属性 |
| `watch()` | 监听 |

```ts
const count = ref(0);
const doubled = computed(() => count.value * 2);
```

---

## 3. Hooks

```ts
// useUser.ts
export function useUser() {
  const user = ref<User | null>(null);
  
  async function fetchUser(id: number) {
    user.value = await api.getUser(id);
  }
  
  return { user, fetchUser };
}
```

---

## 4. Pinia Store

```ts
// stores/user.ts
export const useUserStore = defineStore('user', {
  state: () => ({ user: null }),
  actions: {
    async fetchUser(id: number) {
      this.user = await api.getUser(id);
    },
  },
});
```

---

## 5. 生命周期

| Hook | 说明 |
|------|------|
| `onMounted` | 挂载后 |
| `onUnmounted` | 卸载后 |
| `onUpdated` | 更新后 |
