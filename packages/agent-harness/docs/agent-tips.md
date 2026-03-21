# Agent Tips & Tricks

> 各 Agent 的使用技巧和最佳实践

---

## Claude Code

### 上下文管理

#### /compact - 上下文压缩
当上下文快满时使用：
```
/compact
```
会压缩历史消息，保留关键上下文。

**建议时机：**
- 上下文使用 > 70%
- 完成一个阶段性任务后
- session 变慢时

#### 权限模式
```bash
# 跳过权限确认（自动化场景）
claude --dangerously-skip-permissions

# 权限模式提示
claude --dangerously-enable-permanent-root
```

### 工具使用

#### 高效文件操作
```bash
# 批量读取
Read: [file1.ts, file2.ts, file3.ts]

# 使用 Glob 找文件
glob "**/*.test.ts"

# 使用 Grep 搜索
grep "function_name" --include="*.ts"
```

#### Bash 命令
```bash
# 后台运行
command &

# 长时间任务用 yield
command  # 会阻塞，等结果

# 用 ; 分隔多命令
cd src && npm test && npm run build
```

### Session 管理

```bash
# 新 session
claude

# 查看 session 列表
claude sessions list

# 恢复 session
claude --resume <session-id>
```

---

## Cursor

### Tab 补全技巧

#### 接受/拒绝补全
- **Tab** - 接受补全
- **Esc** - 拒绝补全
- **Cmd →** - 接受单词
- **Cmd ←** - 接受行

#### 理解补全
```
灰色文字 = 建议补全
蓝色下划线 = 较确定的补全
```

### Composer (Cmd+I)

#### 多文件编辑
1. Cmd+I 打开 Composer
2. 输入需求描述
3. 选择多个文件同时编辑
4. Apply 一次性修改

#### 例子
```
帮我把这 5 个文件的 import 语句统一改成绝对路径
```

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| Cmd+K | 编辑当前文件 |
| Cmd+I | 打开 Composer |
| Cmd+L | 打开 Chat |
| Cmd+/ | 注释代码 |
| Cmd+Shift+L | 格式化代码 |

---

## Codex

### 自动模式
Codex 默认在自动模式运行，会自动执行命令。

### 手动模式
```bash
# 切换到手动模式
/manual

# 然后用 approve/deny 确认每个命令
```

### 常用命令
```
/verbose - 显示详细输出
/clear - 清空对话
/extend <file> - 扩展文件
/test - 运行测试
```

---

## OpenCode

### 配置
```bash
# 使用 Claude 模型
opencode --model claude

# 使用 GPT 模型
opencode --model gpt-4

# 指定项目目录
opencode /path/to/project
```

### 交互模式
```
输入命令后：
- y = 确认执行
- n = 拒绝
- a = 全部确认
- q = 退出
```

---

## 通用技巧

### 1. 任务分解

不要一次性给太多任务：
```
❌ 帮我重构整个项目
✅ 帮我重构 src/auth/ 模块
```

### 2. 上下文注入

提供相关文件路径让 Agent 读取：
```
看一下 src/auth/login.ts，然后帮我加个注册功能
```

### 3. 约束表达

用明确的约束：
```
❌ 代码要写得好
✅ 函数不超过 50 行，用 useMemo 优化
```

### 4. 反馈循环

给 Agent 反馈：
```
✅ 对，继续
❌ 不对，应该用 X 方法
```

### 5. 状态追踪

让 Agent 每次用 /state：
```
每次任务开始前先 /state
```

---

## 调试技巧

### 1. 让 Agent 解释
```
解释一下这段代码为什么这么写
```

### 2. 让 Agent 写测试
```
给这个函数写 3 个边界条件的测试用例
```

### 3. 让 Agent 审查
```
review 这几个文件，找潜在 bug
```

### 4. 让 Agent 优化
```
这个函数太慢了，优化一下
```

---

## 常见问题

### Agent 跑偏了
```
/state  # 查看当前状态
/stop   # 停止当前任务
/start <新任务>  # 重新开始
```

### Agent 说不理解
提供更多上下文：
- 相关文件路径
- 期望的行为
- 限制条件

### 结果不符合预期
1. 明确指出哪里不对
2. 解释为什么不对
3. 给出正确的方向

---

## 最佳实践

### 1. 项目初始化
```bash
# 1. 克隆项目
git clone <repo>

# 2. 安装 harness
./setup.sh nuwax .

# 3. 启动 Agent
claude

# 4. 确认状态
/state
```

### 2. 任务执行
```
1. /start <任务描述>
2. 确认范围
3. 小步验证 (/verify)
4. /done
```

### 3. 遇到问题
```
1. /blocked <原因>
2. 等待指示
3. 继续执行
```
