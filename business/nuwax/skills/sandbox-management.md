# Nuwax Sandbox Management Skill

> Business: Nuwax 沙箱管理  
> 版本: 1.0.0  
> 更新: 2026-03-25

---

## 1. 沙箱架构

```
┌─────────────────────────────────┐
│         Agent Runtime           │
├─────────────────────────────────┤
│    Sandbox Manager             │
├──────────┬──────────────────────┤
│ Workspace│   Permission Manager │
├──────────┴──────────────────────┤
│        Audit Logger            │
└─────────────────────────────────┘
```

---

## 2. 创建沙箱

```ts
const sandbox = await sandboxManager.create({
  type: 'docker',
  workspace: '/tmp/nuwax-agent',
  memory: '2g',
  cpu: 2,
});
```

---

## 3. 权限级别

| 级别 | 说明 | 权限 |
|------|------|------|
| `read` | 只读 | 读取文件、API |
| `write` | 写入 | 创建、修改文件 |
| `execute` | 执行 | 运行命令 |
| `admin` | 完全 | 所有操作 |

---

## 4. 命令白名单

```json
{
  "allowedCommands": [
    "pnpm dev",
    "pnpm build",
    "pnpm typecheck",
    "git status",
    "npm test"
  ]
}
```

---

## 5. 审计日志

```ts
audit.log({
  action: 'file:write',
  path: '/tmp/test.txt',
  timestamp: Date.now(),
  allowed: true,
});
```

---

## 6. 状态更新

```ts
await state.update({
  sandbox: {
    active: true,
    workspace: '/tmp/nuwax-agent',
    permissions: ['read', 'execute'],
  },
});
```
