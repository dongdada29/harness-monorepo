# Agent 集成指南

本文档介绍如何将 Harness 集成到不同的 AI Agent 中。

---

## 支持的 Agent

| Agent | 状态 | 配置文件 |
|-------|------|----------|
| Claude Code | ✅ 完全支持 | CLAUDE.md |
| Cursor | ✅ 完全支持 | .cursorrules |
| Codex (OpenAI) | ✅ 完全支持 | CODEX.md |
| OpenCode | 🔄 部分支持 | OPENCODE.md |
| 其他 | ⚠️ 手动集成 | README.md |

---

## 1. Claude Code 集成

### 自动集成

```bash
# setup.sh 自动生成 CLAUDE.md
./setup.sh --type generic

# 文件结构
CLAUDE.md              # 主指令文件
harness/               # 约束和状态
```

### CLAUDE.md 结构

```markdown
# 项目规则 (AI Agent 必读)

## 项目信息
- 项目名称: xxx
- 技术栈: React, TypeScript, Node.js
- 主要框架: Next.js 14

## 工作流程
- CP1: 理解任务
- CP2: 技术方案
- CP3: 实现编码
- CP4: 测试验证
- CP5: 发布完成

## 质量门禁
- lint: 必须通过
- typecheck: 必须通过
- test: 必须通过
- build: 必须通过

## 约束
- 禁止 console.log
- 禁止 debugger
- 必须写测试
```

### 使用

```bash
# 打开项目
claude-code .

# Claude Code 自动读取 CLAUDE.md
# 遵循工作流和约束
```

---

## 2. Cursor 集成

### 自动集成

```bash
# setup.sh 生成 .cursorrules
./setup.sh --type generic

# 文件
.cursorrules            # Cursor 规则文件
```

### .cursorrules 结构

```markdown
# Cursor Project Rules

## 项目概述
- 名称: xxx
- 类型: Web Application
- 技术栈: React + TypeScript

## 编码规范
- 使用函数式组件
- 使用 TypeScript strict mode
- 使用 Tailwind CSS

## 工作流程
1. 分析需求
2. 编写代码
3. 运行测试
4. 提交代码

## 禁止事项
- 不要使用 any 类型
- 不要忽略 TypeScript 错误
- 不要跳过测试
```

### 使用

```bash
# 打开项目
cursor .

# Cursor 自动应用规则
```

---

## 3. Codex (OpenAI) 集成

### 手动集成

```bash
# 创建 CODEX.md
cat > CODEX.md << 'EOF'
# Codex Project Instructions

## 项目信息
- 名称: my-project
- 语言: TypeScript
- 框架: React

## 任务流程
1. 理解需求
2. 设计方案
3. 实现代码
4. 测试验证

## 代码规范
- 使用 ESLint
- 使用 Prettier
- 写单元测试

## 质量要求
- 无 TypeScript 错误
- 无 lint 警告
- 测试通过
EOF
```

### 使用

在 Codex 提示中引用：

```
请阅读 CODEX.md 并遵循其中的规范来实现功能。
```

---

## 4. 多 Agent 协作

### 场景：Claude Code 设计 + Cursor 实现

```bash
# 1. 设置共享 harness
./setup.sh --type generic

# 2. 为 Claude Code 创建设计文档
cat > CLAUDE.md << 'EOF'
## 角色：架构师

### 职责
- 系统设计
- 技术选型
- API 设计
- 代码审查

### 输出
- 设计文档 (docs/design/)
- API 规范
- 架构图
EOF

# 3. 为 Cursor 创建实现规则
cat > .cursorrules << 'EOF'
## 角色：实现者

### 职责
- 编写代码
- 编写测试
- 修复 bug
- 重构代码

### 输入
- 读取 docs/design/ 中的设计文档

### 输出
- src/ 中的实现代码
- tests/ 中的测试代码
EOF
```

### 协作流程

```
┌─────────────────────────────────────────────┐
│              共享 Harness                    │
│  harness/base/constraints.md                │
│  harness/feedback/state/state.json          │
└─────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌─────────────────┐   ┌─────────────────┐
│   Claude Code   │   │     Cursor      │
│   (架构师)       │   │    (实现者)      │
├─────────────────┤   ├─────────────────┤
│ CLAUDE.md       │   │ .cursorrules    │
│                 │   │                 │
│ CP1: 需求分析    │   │ CP3: 编码实现    │
│ CP2: 架构设计    │──►│ CP4: 测试验证    │
│                 │   │ CP5: 发布       │
└─────────────────┘   └─────────────────┘
```

---

## 5. CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/harness.yml
name: Harness CI

on: [push, pull_request]

jobs:
  harness:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup
        run: |
          npm install
          pip install -r tools/eval-cli/requirements.txt
      
      - name: Validate
        run: ./scripts/quick-validate.sh
      
      - name: Benchmark
        run: python3 tools/eval-cli/benchmark.py --project .
      
      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark_results.json
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - validate
  - benchmark

validate:
  stage: validate
  script:
    - ./scripts/quick-validate.sh

benchmark:
  stage: benchmark
  script:
    - pip install -r tools/eval-cli/requirements.txt
    - python3 tools/eval-cli/benchmark.py --project .
  artifacts:
    paths:
      - benchmark_results.json
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Validate') {
            steps {
                sh './scripts/quick-validate.sh'
            }
        }
        
        stage('Benchmark') {
            steps {
                sh 'pip install -r tools/eval-cli/requirements.txt'
                sh 'python3 tools/eval-cli/benchmark.py --project .'
            }
        }
    }
}
```

---

## 6. 编辑器集成

### VS Code

```json
// .vscode/settings.json
{
  "files.associations": {
    "CLAUDE.md": "markdown",
    ".cursorrules": "markdown"
  },
  
  "markdown.preview.styles": [
    "./harness/base/constraints.md"
  ]
}
```

### JetBrains IDEs

```xml
<!-- .idea/file.template.settings.xml -->
<template>
  <name>CLAUDE.md</name>
  <content>
    # 项目规则
    
    ## 项目信息
    - 名称: ${PROJECT_NAME}
    - 技术栈: 
    
    ## 工作流程
    - CP1-CP5
  </content>
</template>
```

---

## 7. 自定义 Agent 集成

### 步骤

1. **创建配置文件**

```bash
# 创建你的 Agent 配置文件
touch MY_AGENT.md
```

2. **定义规则**

```markdown
# My Agent Configuration

## 项目信息
- 从 CLAUDE.md 或 README.md 读取

## 工作流程
- 遵循 CP1-CP5

## 质量门禁
- 运行 lint/typecheck/test/build
```

3. **在 Agent 中引用**

```bash
# 在你的 Agent 提示中
请阅读 MY_AGENT.md 和 harness/base/constraints.md，遵循其中的规范。
```

---

## 最佳实践

### 1. 保持一致性

```bash
# 确保所有 Agent 使用相同的约束
CLAUDE.md ────┐
.cursorrules ─┼──► harness/base/constraints.md
CODEX.md ─────┘
```

### 2. 定期同步

```bash
# 定期更新约束
vim harness/base/constraints.md

# 所有 Agent 会自动应用新约束
```

### 3. 版本控制

```bash
# 提交所有配置文件
git add CLAUDE.md .cursorrules harness/
git commit -m "chore: update harness configuration"
```

### 4. 团队共享

```bash
# 在团队中共享配置
# 确保每个人使用相同的工作流和约束
```

---

*Last updated: 2026-03-22*
