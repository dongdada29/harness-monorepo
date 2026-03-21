#!/bin/bash
# cleanup.sh - 技术债务扫描和清理

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASS=0
WARN=0
FAIL=0

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((PASS++)); }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; ((WARN++)); }
fail() { echo -e "${RED}[FAIL]${NC} $1"; ((FAIL++)); }

echo "==================================="
echo "Harness Tech Debt Scanner"
echo "==================================="
echo ""

# Check for console.log / debugger
echo "--- 检查调试代码 ---"
if grep -r "console\.log" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null | grep -v node_modules | grep -v ".git"; then
    warn "发现 console.log，请清理"
else
    pass "无 console.log"
fi

if grep -r "debugger" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null | grep -v node_modules | grep -v ".git"; then
    warn "发现 debugger，请移除"
else
    pass "无 debugger"
fi

# Check for TODO without issue reference
echo ""
echo "--- 检查 TODO ---"
if grep -r "TODO" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" . 2>/dev/null | grep -v "#" | grep -v node_modules | grep -v ".git" | head -5; then
    warn "发现未标记 issue 的 TODO"
else
    pass "TODO 都有 issue 标记"
fi

# Check for long functions (> 50 lines)
echo ""
echo "--- 检查函数长度 ---"
log "扫描中..."
LONG_FUNC=$(find . -name "*.ts" -o -name "*.tsx" | xargs wc -l 2>/dev/null | grep -v node_modules | grep -v ".git" | awk '$1 > 200 {print $2": "$1" lines"}' | head -5)
if [ -n "$LONG_FUNC" ]; then
    warn "发现 >200 行的文件："
    echo "$LONG_FUNC" | while read line; do
        echo "  $line"
    done
else
    pass "无超长文件"
fi

# Check for duplicate code (simple heuristic)
echo ""
echo "--- 检查重复代码 ---"
log "扫描中..."

# Check state.json is up to date
echo ""
echo "--- 检查 state.json ---"
if [ -f "harness/feedback/state/state.json" ]; then
    LAST_UPDATE=$(grep lastUpdated harness/feedback/state/state.json | cut -d'"' -f4)
    TODAY=$(date +%Y-%m-%d)
    if [ "$LAST_UPDATE" == "$TODAY" ]; then
        pass "state.json 今天已更新"
    else
        warn "state.json 需要更新 (上次: $LAST_UPDATE)"
    fi
else
    warn "state.json 不存在"
fi

# Summary
echo ""
echo "==================================="
echo "扫描完成"
echo -e "通过: ${GREEN}$PASS${NC}"
echo -e "警告: ${YELLOW}$WARN${NC}"
echo -e "失败: ${RED}$FAIL${NC}"
echo "==================================="

if [ $WARN -gt 0 ]; then
    echo ""
    echo "建议："
    echo "  1. 清理 console.log / debugger"
    echo "  2. 为 TODO 添加 issue 标记"
    echo "  3. 拆分长文件"
    echo "  4. 更新 state.json"
fi
