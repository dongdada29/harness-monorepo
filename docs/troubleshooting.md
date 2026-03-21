# 故障排查指南

> harness-monorepo 常见问题解决方案

---

## 目录

- [安装问题](#安装问题)
- [配置问题](#配置问题)
- [工作流问题](#工作流问题)
- [门禁问题](#门禁问题)
- [状态问题](#状态问题)

---

## 安装问题

### Q: setup.sh 报错 "packages 目录不存在"

**原因**: 不在 harness-monorepo 根目录下运行

**解决**:
```bash
cd harness-monorepo
./setup.sh nuwax /path/to/project
```

---

### Q: setup.sh 报错 "rsync 未安装"

**原因**: 系统缺少 rsync

**解决**:
```bash
# macOS
brew install rsync

# Linux
sudo apt-get install rsync  # Debian/Ubuntu
sudo yum install rsync      # CentOS/RHEL
```

---

### Q: setup.sh 安装后找不到 CLAUDE.md

**原因**: 目标目录路径错误

**解决**:
```bash
# 检查当前目录
pwd

# 使用绝对路径
./setup.sh generic /absolute/path/to/project

# 或相对路径
./setup.sh generic ./my-project
```

---

## 配置问题

### Q: Agent 不读取 CLAUDE.md

**原因**: Agent 配置文件优先级问题

**解决**:
```bash
# Claude Code
# CLAUDE.md 应在项目根目录

# Cursor
# .cursorrules 应在项目根目录

# Codex/OpenCode
# AGENTS.md 应在项目根目录

# 检查文件位置
ls -la CLAUDE.md .cursorrules AGENTS.md
```

---

### Q: 约束不生效

**原因**: 约束文件路径错误

**解决**:
```bash
# 检查约束文件
ls -la harness/base/constraints.md
ls -la harness/projects/*/constraints.md

# 确保文件不为空
cat harness/base/constraints.md
```

---

## 工作流问题

### Q: /start 命令不工作

**原因**: 命令未注册或 Agent 不支持

**解决**:
```bash
# 检查 state.json
cat harness/feedback/state/state.json

# 手动更新状态
./scripts/update-state.sh start "任务描述"

# 查看状态
./scripts/update-state.sh show
```

---

### Q: 任务状态不更新

**原因**: 缺少状态更新脚本或权限

**解决**:
```bash
# 检查脚本
ls -la scripts/update-state.sh

# 添加执行权限
chmod +x scripts/update-state.sh

# 手动更新
./scripts/update-state.sh start "新任务"
```

---

## 门禁问题

### Q: Gate 1 (Lint) 失败

**原因**: 代码不符合 lint 规则

**解决**:
```bash
# 查看详细错误
npm run lint

# 自动修复
npm run lint -- --fix

# 检查 eslint 配置
cat .eslintrc.js
```

---

### Q: Gate 2 (Typecheck) 失败

**原因**: TypeScript 类型错误

**解决**:
```bash
# 查看详细错误
npm run typecheck

# 检查 tsconfig.json
cat tsconfig.json

# 常见问题：
# - 缺少类型定义
# - 类型不匹配
# - any 类型
```

---

### Q: Gate 3 (Test) 失败

**原因**: 测试未通过

**解决**:
```bash
# 查看详细错误
npm test

# 运行单个测试文件
npm test -- path/to/test.ts

# 更新快照
npm test -- -u
```

---

### Q: Gate 4 (Build) 失败

**原因**: 构建失败

**解决**:
```bash
# 查看详细错误
npm run build

# 清理缓存
rm -rf node_modules/.vite
rm -rf dist

# 重新安装依赖
rm -rf node_modules
npm install
```

---

## 状态问题

### Q: state.json 损坏

**原因**: 手动编辑错误或并发写入

**解决**:
```bash
# 验证 JSON 格式
jq . harness/feedback/state/state.json

# 重置状态
./scripts/update-state.sh reset

# 或手动修复
vim harness/feedback/state/state.json
```

---

### Q: 最近变更丢失

**原因**: recentChanges 数组溢出（只保留 10 条）

**解决**:
```bash
# 查看当前变更
jq '.recentChanges' harness/feedback/state/state.json

# 备份 state.json
cp harness/feedback/state/state.json{,.backup}

# 手动编辑保留更多
vim harness/feedback/state/state.json
```

---

### Q: 检查点状态不正确

**原因**: 跳过步骤或手动修改错误

**解决**:
```bash
# 查看当前状态
./scripts/update-state.sh show

# 手动更新检查点
./scripts/update-state.sh checkpoint CP1 completed
./scripts/update-state.sh checkpoint CP2 in_progress

# 重置所有检查点
./scripts/update-state.sh reset
```

---

## 通用问题

### Q: 找不到 harness 命令

**原因**: PATH 未设置

**解决**:
```bash
# 添加到 PATH
export PATH="$PWD/scripts:$PATH"

# 或使用相对路径
./scripts/update-state.sh show
```

---

### Q: 权限错误

**原因**: 脚本没有执行权限

**解决**:
```bash
# 添加执行权限
chmod +x scripts/*.sh
chmod +x setup.sh

# 或一次性添加所有
find . -name "*.sh" -exec chmod +x {} \;
```

---

### Q: 依赖版本冲突

**原因**: package.json 版本不兼容

**解决**:
```bash
# 检查依赖版本
npm list

# 更新依赖
npm update

# 或重新安装
rm -rf node_modules package-lock.json
npm install
```

---

## 调试技巧

### 1. 启用详细日志

```bash
# setup.sh
bash -x ./setup.sh nuwax /path/to/project

# 脚本
bash -x ./scripts/update-state.sh show
```

### 2. 检查环境

```bash
# Node 版本
node --version  # 需要 >= 16

# npm 版本
npm --version

# jq 版本（状态脚本需要）
jq --version
```

### 3. 清理并重试

```bash
# 删除 harness 配置
rm -rf harness CLAUDE.md .cursorrules AGENTS.md

# 重新安装
./setup.sh nuwax /path/to/project
```

---

## 获取帮助

如果以上方法都无法解决：

1. **查看日志**: 检查 `harness/logs/` 目录
2. **查看文档**: `README.md`, `QUICKSTART.md`
3. **提交 Issue**: https://github.com/dongdada29/harness-monorepo/issues
4. **社区支持**: 在 GitHub Discussions 提问

---

## 报告 Bug

提交 Bug 时请包含：

```markdown
**环境**:
- OS: [e.g. macOS 14.0]
- Node: [e.g. 18.17.0]
- npm: [e.g. 9.6.7]
- harness-monorepo version: [e.g. 1.0.0]

**复现步骤**:
1. ...
2. ...
3. ...

**期望结果**:
...

**实际结果**:
...

**日志**:
```
[粘贴日志]
```
```

---

*最后更新: 2026-03-22*
