#!/bin/bash
# check.sh - 检查 Harness 配置是否完整

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASS=0
FAIL=0

check() {
    local file=$1
    local name=$2
    
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $name"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $name (missing: $file)"
        ((FAIL++))
    fi
}

check_dir() {
    local dir=$1
    local name=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} $name"
        ((PASS++))
    else
        echo -e "${RED}✗${NC} $name (missing: $dir)"
        ((FAIL++))
    fi
}

echo "==================================="
echo "Harness Configuration Check"
echo "==================================="
echo ""

PROJECT_ROOT=${1:-.}

cd "$PROJECT_ROOT"

echo "--- Root Files ---"
check "CLAUDE.md" "CLAUDE.md"
check ".cursorrules" ".cursorrules"
check "AGENTS.md" "AGENTS.md"
check "harness/feedback/state/state.json" "state.json"
echo ""

echo "--- Harness Structure ---"
check_dir "harness/base" "harness/base"
check_dir "harness/input" "harness/input"
check_dir "harness/feedback" "harness/feedback"
echo ""

echo "--- Base Constraints ---"
check "harness/base/constraints.md" "base/constraints.md"
check_dir "harness/base/tasks" "base/tasks"
check "harness/base/tasks/feature.md" "feature template"
check "harness/base/tasks/bugfix.md" "bugfix template"
echo ""

echo "--- Scripts ---"
check "scripts/verify.sh" "verify.sh"
check "scripts/state.sh" "state.sh"
if [ -f "scripts/verify.sh" ]; then
    if [ -x "scripts/verify.sh" ]; then
        echo -e "${GREEN}✓${NC} verify.sh is executable"
    else
        echo -e "${YELLOW}!${NC} verify.sh not executable (run: chmod +x scripts/*.sh)"
    fi
fi
echo ""

echo "==================================="
echo "Result: $PASS passed, $FAIL failed"
echo "==================================="

if [ $FAIL -gt 0 ]; then
    exit 1
fi
