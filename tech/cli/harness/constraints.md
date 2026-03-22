# CLI Tech Harness

> Tech Stack: Node.js + TypeScript + Commander  
> 版本: 1.0.0  
> 更新: 2026-03-23

---

## 1. Tech Stack

| 技术 | 说明 |
|------|------|
| Node.js | 运行时 |
| TypeScript | 类型系统 |
| Commander | CLI 框架 |
| Inquirer | 交互式 CLI |

---

## 2. Commands

### Auto-Approve
```bash
pnpm build         # 构建
pnpm test          # 测试
pnpm lint          # Lint
```

### Need Confirm
```bash
pnpm add <pkg>     # 添加包
pnpm link           # 链接本地包
```

### Blocked
```bash
npm install -g      # 全局安装
npm publish         # 发布
```

---

## 3. MCP Tools

| 工具 | 说明 |
|------|------|
| `cli-parse` | 解析 CLI 参数 |
| `cli-exec` | 执行命令 |
| `cli-template` | 生成模板 |

---

## 4. Gates

```
pnpm lint → pnpm typecheck → pnpm test → pnpm build
```
