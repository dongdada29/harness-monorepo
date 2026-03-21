# 常见问题 (FAQ)

---

## 安装相关

### Q: setup.sh 支持哪些项目类型？

**A:** 支持 3 种类型：
- `generic` - 通用项目 (默认)
- `nuwax` - Nuwax Agent 项目
- `electron` - Electron 桌面应用

```bash
./setup.sh --type electron
```

### Q: 可以在没有网络的环境安装吗？

**A:** 可以，下载后离线使用：

```bash
# 下载到本地
git clone https://github.com/dongdada29/harness-monorepo.git

# 复制到项目
cp -r harness-monorepo/packages/agent-harness ~/projects/my-project/
```

### Q: 安装后需要配置什么？

**A:** 主要配置项：
1. 编辑 `CLAUDE.md` - 添加项目信息
2. 编辑 `harness/base/constraints.md` - 添加约束
3. 运行 `./scripts/update-state.sh init` - 初始化状态

---

## 使用相关

### Q: 如何更新任务状态？

**A:** 使用 update-state.sh 脚本：

```bash
# 开始任务
./scripts/update-state.sh task_start "实现用户登录"

# 完成任务
./scripts/update-state.sh task_complete "实现用户登录"

# 阻塞任务
./scripts/update-state.sh task_block "等待 API 文档"
```

### Q: 如何运行 benchmark？

**A:** 使用 Python 脚本：

```bash
# 基础运行
python3 tools/eval-cli/benchmark.py --project .

# JSON 输出
python3 tools/eval-cli/benchmark.py --project . --output json

# Markdown 输出
python3 tools/eval-cli/benchmark.py --project . --output markdown
```

### Q: Benchmark 评分低怎么办？

**A:** 常见原因和解决方案：

| 问题 | 解决方案 |
|------|----------|
| 任务完成率低 | 更新 state.json，记录完成的任务 |
| Gate 通过率低 | 修复 lint/typecheck/test/build 错误 |
| 违规项多 | 删除 console.log、debugger 等 |
| 效率低 | 减少阻塞，提高吞吐量 |

### Q: 如何自定义约束？

**A:** 编辑 `harness/base/constraints.md`：

```markdown
## 必须遵守

### 编码规范
- [ ] 使用 TypeScript strict mode
- [ ] 函数必须有 JSDoc 注释
- [ ] 测试覆盖率 > 80%

### 禁止事项
- [ ] 禁止使用 any 类型
- [ ] 禁止 console.log
- [ ] 禁止 debugger
```

---

## Agent 相关

### Q: Claude Code 不读取 CLAUDE.md 怎么办？

**A:** 检查以下几点：

1. **文件位置** - 必须在项目根目录
2. **文件格式** - 确保是有效的 Markdown
3. **编码格式** - 使用 UTF-8 编码

```bash
# 验证文件
file CLAUDE.md
# 应该显示: UTF-8 Unicode text
```

### Q: 如何在 Cursor 中使用？

**A:** Cursor 使用 `.cursorrules` 文件：

```bash
# setup.sh 自动生成
./setup.sh

# 或手动创建
cat > .cursorrules << 'EOF'
遵循 CLAUDE.md 中的规则
使用 TypeScript
写测试
EOF

# 打开 Cursor
cursor .
```

### Q: 可以同时用多个 Agent 吗？

**A:** 可以！使用不同的配置文件：

```
项目/
├── CLAUDE.md        # Claude Code 配置
├── .cursorrules     # Cursor 配置
├── CODEX.md         # Codex 配置
└── harness/         # 共享的约束和状态
```

每个 Agent 可以有不同角色：
- Claude Code: 架构设计
- Cursor: 代码实现
- Codex: 测试编写

---

## CI/CD 相关

### Q: 如何在 CI 中使用？

**A:** 使用 npm scripts：

```yaml
# GitHub Actions
- name: Run Harness
  run: |
    npm run validate      # 快速验证
    npm run test:unit     # 单元测试
    npm run ci           # 完整 CI 流程
```

### Q: CI 中 benchmark 失败怎么办？

**A:** 使用 `continue-on-error`：

```yaml
- name: Run Benchmark
  continue-on-error: true
  run: npm run test:benchmark
```

### Q: 如何设置质量门禁？

**A:** 在 CI 中添加条件：

```yaml
- name: Quality Gate
  run: |
    SCORE=$(python3 tools/eval-cli/benchmark.py --project . --output json | jq '.overall')
    if [ $(echo "$SCORE < 80" | bc) -eq 1 ]; then
      echo "Quality gate failed: $SCORE < 80"
      exit 1
    fi
```

---

## 故障排查

### Q: state.json 损坏怎么办？

**A:** 重新生成：

```bash
# 备份旧文件
cp harness/feedback/state/state.json state.json.bak

# 下载模板
curl -fsSL https://raw.githubusercontent.com/dongdada29/harness-monorepo/main/packages/agent-harness/harness/feedback/state/state.json > harness/feedback/state/state.json

# 编辑项目信息
vim harness/feedback/state/state.json
```

### Q: 脚本没有执行权限？

**A:** 添加权限：

```bash
chmod +x setup.sh
chmod +x scripts/*.sh
chmod +x packages/*/tests/*.sh
```

### Q: Python 脚本报错？

**A:** 检查 Python 版本和依赖：

```bash
# 检查 Python 版本 (需要 3.8+)
python3 --version

# 安装依赖
pip install -r tools/eval-cli/requirements.txt

# 检查语法
python3 -m py_compile tools/eval-cli/benchmark.py
```

---

## 性能相关

### Q: Benchmark 运行太慢？

**A:** 使用性能优化模块：

```python
from benchmark_perf import BenchmarkCache, ParallelMetrics

# 使用缓存
cache = BenchmarkCache()

# 并行处理
counts = ParallelMetrics.count_files(path, ["*.ts", "*.js"])
```

### Q: 如何提高评分？

**A:** 关注高权重指标：

| 维度 | 权重 | 重点 |
|------|------|------|
| Efficiency | 40% | 任务完成率、Gate 通过率 |
| Quality | 30% | 无 console.log、测试通过 |
| Behavior | 15% | 状态更新、变更追踪 |
| Autonomy | 15% | 自主完成、自我修正 |

---

## 其他

### Q: 如何贡献代码？

**A:** 参见 [CONTRIBUTING.md](../CONTRIBUTING.md)

### Q: 有问题去哪里问？

**A:** 
- GitHub Issues: https://github.com/dongdada29/harness-monorepo/issues
- 文档: `docs/` 目录
- 故障排查: [troubleshooting.md](./troubleshooting.md)

### Q: 如何获取更新？

**A:** 

```bash
# 拉取最新代码
git pull origin main

# 或重新安装
curl -fsSL https://raw.githubusercontent.com/dongdada29/harness-monorepo/main/setup.sh | bash
```

---

*Last updated: 2026-03-22*
