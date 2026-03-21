#!/bin/bash
# eval.sh - 生成 Harness 效果评估报告

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "==================================="
echo "Harness 效果评估"
echo "==================================="
echo ""

# 1. 读取 state.json
if [ -f "harness/feedback/state/state.json" ]; then
    echo "--- 任务统计 ---"
    
    TOTAL=$(grep -o '"tasksCompleted":[0-9]*' harness/feedback/state/state.json | cut -d: -f2)
    BLOCKED=$(grep -o '"tasksBlocked":[0-9]*' harness/feedback/state/state.json | cut -d: -f2)
    
    echo "完成任务数: $TOTAL"
    echo "被阻塞数: $BLOCKED"
    
    if [ -n "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
        BLOCKED_RATE=$((BLOCKED * 100 / TOTAL))
        COMPLETE_RATE=$((100 - BLOCKED_RATE))
        echo "完成率: ${COMPLETE_RATE}%"
        echo "阻塞率: ${BLOCKED_RATE}%"
    fi
fi

echo ""
echo "--- Gate 统计 ---"
if grep -q '"gates"' harness/feedback/state/state.json 2>/dev/null; then
    LINT=$(grep '"lint":"[a-z]*' harness/feedback/state/state.json | grep -c "passed" 2>/dev/null || echo 0)
    TYPE=$(grep '"typecheck":"[a-z]*' harness/feedback/state/state.json | grep -c "passed" 2>/dev/null || echo 0)
    TEST=$(grep '"test":"[a-z]*' harness/feedback/state/state.json | grep -c "passed" 2>/dev/null || echo 0)
    BUILD=$(grep '"build":"[a-z]*' harness/feedback/state/state.json | grep -c "passed" 2>/dev/null || echo 0)
    
    echo "Lint: $LINT"
    echo "Typecheck: $TYPE"
    echo "Test: $TEST"
    echo "Build: $BUILD"
fi

echo ""
echo "--- 约束检查 ---"
VIOLATIONS=0

# 检查 console.log
CONSOLE_COUNT=$(grep -r "console\.log" --include="*.ts" --include="*.tsx" --include="*.js" . 2>/dev/null | grep -v node_modules | grep -v ".git" | wc -l | tr -d ' ')
echo "console.log 数量: $CONSOLE_COUNT"

# 检查 TODO
TODO_COUNT=$(grep -r "TODO" --include="*.ts" --include="*.tsx" --include="*.js" . 2>/dev/null | grep -v "#" | grep -v node_modules | grep -v ".git" | wc -l | tr -d ' ')
echo "未标记 TODO 数量: $TODO_COUNT"

echo ""
echo "==================================="
echo "建议"
echo "==================================="

if [ "$CONSOLE_COUNT" -gt 0 ]; then
    echo "1. 清理 $CONSOLE_COUNT 个 console.log"
fi

if [ "$TODO_COUNT" -gt 0 ]; then
    echo "2. 为 $TODO_COUNT 个 TODO 添加 issue 标记"
fi

if [ "$BLOCKED_RATE" -gt 10 ]; then
    echo "3. 阻塞率较高 (${BLOCKED_RATE}%)，考虑优化 Harness"
fi
