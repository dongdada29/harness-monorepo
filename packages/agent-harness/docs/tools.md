# 工具配置

## Claude Code 可用工具

| 工具 | 用途 | 权限 |
|------|------|------|
| Read | 读取文件 | ✅ 始终允许 |
| Write | 写入文件 | ✅ 始终允许 |
| Edit | 编辑文件 | ✅ 始终允许 |
| Glob | 查找文件 | ✅ 始终允许 |
| Grep | 搜索内容 | ✅ 始终允许 |
| Bash | 执行命令 | ⚠️ 需要确认 |

## Bash 命令白名单

```bash
# 允许的命令
npm install
npm run dev
npm run build
npm test
npm run lint
git add .
git commit
git push
```

## 禁止的命令

```bash
# 禁止
rm -rf node_modules
rm -rf .git
curl/wget (网络访问)
npm publish
```

## MCP 服务

暂不需要外部 MCP 服务。

## 环境变量

项目所需环境变量：
- `NODE_ENV`: development | production
- `PORT`: 开发服务器端口 (默认 3000)
