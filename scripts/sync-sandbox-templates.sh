#!/bin/bash

# Sandbox 任务定义同步脚本
# 从 NuwaClaw 提取到 harness-monorepo

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 复制 Sandbox 任务定义..."

# 创建目录（如果不存在）
mkdir -p "$MONOREPO_ROOT/core/harness/base/tasks"
mkdir -p "$MONOREPO_ROOT/core/harness/projects/darwin"
mkdir -p "$MONOREPO_ROOT/core/harness/projects/linux"
mkdir -p "$MONOREPO_ROOT/core/harness/projects/win32"
mkdir -p "$MONOREPO_ROOT/core/harness/universal"

# 复制任务文件
cp /Users/apple/workspace/nuwax-agent/crates/agent-electron-client/harness/base/tasks/sandbox-create.md \
   "$MONOREPO_ROOT/core/harness/base/tasks/"

cp /Users/apple/workspace/nuwax-agent/crates/agent-electron-client/harness/base/tasks/sandbox-execute.md \
   "$MONOREPO_ROOT/core/harness/base/tasks/"

cp /Users/apple/workspace/nuwax-agent/crates/agent-electron-client/harness/base/tasks/sandbox-cleanup.md \
   "$MONOREPO_ROOT/core/harness/base/tasks/"

# 复制平台配置
cp /Users/apple/workspace/nuwax-agent/crates/agent-electron-client/harness/projects/darwin/sandbox-config.md \
   "$MONOREPO_ROOT/core/harness/projects/darwin/" 2>/dev/null || echo "⚠️  darwin 配置不存在，跳过"

# 复制通用 API
cp /Users/apple/workspace/nuwax-agent/crates/agent-electron-client/harness/universal/sandbox-api.md \
   "$MONOREPO_ROOT/core/harness/universal/" 2>/dev/null || echo "⚠️  universal API 不存在，跳过"

echo "✅ Sandbox 模板同步完成"
echo ""
echo "已复制的文件："
echo "  - core/harness/base/tasks/sandbox-create.md"
echo "  - core/harness/base/tasks/sandbox-execute.md"
echo "  - core/harness/base/tasks/sandbox-cleanup.md"
echo "  - core/harness/projects/darwin/sandbox-config.md"
echo "  - core/harness/universal/sandbox-api.md"
