#!/bin/bash
#
# Harness Unit Tests
# 测试各个核心组件的功能
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 测试计数器
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# 测试函数
test_case() {
    local name="$1"
    local result="$2"
    
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if [ "$result" = "0" ]; then
        echo -e "  ${GREEN}✓${NC} $name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "  ${RED}✗${NC} $name"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

echo "========================================"
echo "  Harness 单元测试"
echo "========================================"
echo ""

# ============================================
# 1. 项目结构测试
# ============================================
echo "【1/6】项目结构测试..."

# 测试根目录文件
test_case "README.md 存在" $([ -f "$ROOT_DIR/README.md" ]; echo $?)
test_case "QUICKSTART.md 存在" $([ -f "$ROOT_DIR/QUICKSTART.md" ]; echo $?)
test_case "setup.sh 存在" $([ -f "$ROOT_DIR/setup.sh" ]; echo $?)
test_case "package.json 存在" $([ -f "$ROOT_DIR/package.json" ]; echo $?)

# 测试 packages 目录
test_case "packages/agent-harness 存在" $([ -d "$ROOT_DIR/packages/agent-harness" ]; echo $?)
test_case "packages/nuwax-harness 存在" $([ -d "$ROOT_DIR/packages/nuwax-harness" ]; echo $?)
test_case "packages/electron-harness 存在" $([ -d "$ROOT_DIR/packages/electron-harness" ]; echo $?)

# 测试 docs 目录
test_case "docs 目录存在" $([ -d "$ROOT_DIR/docs" ]; echo $?)
test_case "docs/BENCHMARK_METRICS.md 存在" $([ -f "$ROOT_DIR/docs/BENCHMARK_METRICS.md" ]; echo $?)
test_case "docs/VALIDATION.md 存在" $([ -f "$ROOT_DIR/docs/VALIDATION.md" ]; echo $?)

echo ""

# ============================================
# 2. Harness 结构测试
# ============================================
echo "【2/6】Harness 结构测试..."

HARNESS_DIR="$ROOT_DIR/packages/agent-harness/harness"

# 测试 harness 目录结构
test_case "harness/base 存在" $([ -d "$HARNESS_DIR/base" ]; echo $?)
test_case "harness/feedback 存在" $([ -d "$HARNESS_DIR/feedback" ]; echo $?)
test_case "harness/prompts 存在" $([ -d "$HARNESS_DIR/prompts" ]; echo $?)

# 测试核心文件
test_case "CLAUDE.md 存在" $([ -f "$ROOT_DIR/packages/agent-harness/CLAUDE.md" ]; echo $?)
test_case "constraints.md 存在" $([ -f "$HARNESS_DIR/base/constraints.md" ]; echo $?)
test_case "state.json 存在" $([ -f "$HARNESS_DIR/feedback/state/state.json" ]; echo $?)

echo ""

# ============================================
# 3. JSON 格式测试
# ============================================
echo "【3/6】JSON 格式测试..."

# 测试 package.json 格式
python3 -c "import json; json.load(open('$ROOT_DIR/package.json'))" 2>/dev/null
test_case "package.json 格式正确" $?

# 测试 state.json 格式
for pkg in agent-harness nuwax-harness; do
    STATE_FILE="$ROOT_DIR/packages/$pkg/harness/feedback/state/state.json"
    if [ -f "$STATE_FILE" ]; then
        python3 -c "import json; json.load(open('$STATE_FILE'))" 2>/dev/null
        test_case "$pkg/state.json 格式正确" $?
    fi
done

# 测试示例项目的 state.json
EXAMPLE_STATE="$ROOT_DIR/examples/todo-app/harness/feedback/state/state.json"
if [ -f "$EXAMPLE_STATE" ]; then
    python3 -c "import json; json.load(open('$EXAMPLE_STATE'))" 2>/dev/null
    test_case "examples/todo-app/state.json 格式正确" $?
fi

echo ""

# ============================================
# 4. 脚本可执行性测试
# ============================================
echo "【4/6】脚本可执行性测试..."

# 测试脚本是否有执行权限
for script in setup.sh scripts/quick-validate.sh packages/agent-harness/tests/validate-harness.sh; do
    if [ -f "$ROOT_DIR/$script" ]; then
        test_case "$script 可执行" $([ -x "$ROOT_DIR/$script" ]; echo $?)
    fi
done

echo ""

# ============================================
# 5. Setup 脚本测试
# ============================================
echo "【5/6】Setup 脚本测试..."

# 创建临时目录
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# 测试 setup.sh 语法
bash -n "$ROOT_DIR/setup.sh" 2>/dev/null
test_case "setup.sh 语法正确" $?

# 测试 setup.sh 帮助信息
"$ROOT_DIR/setup.sh" --help >/dev/null 2>&1
test_case "setup.sh --help 可用" $?

echo ""

# ============================================
# 6. Benchmark 工具测试
# ============================================
echo "【6/6】Benchmark 工具测试..."

BENCHMARK="$ROOT_DIR/tools/eval-cli/benchmark.py"

if [ -f "$BENCHMARK" ]; then
    # 测试 Python 语法
    python3 -m py_compile "$BENCHMARK" 2>/dev/null
    test_case "benchmark.py 语法正确" $?
    
    # 测试帮助信息
    python3 "$BENCHMARK" --help >/dev/null 2>&1
    test_case "benchmark.py --help 可用" $?
else
    test_case "benchmark.py 存在" 1
fi

# 测试 evaluator.py
EVALUATOR="$ROOT_DIR/tools/eval-cli/evaluator.py"
if [ -f "$EVALUATOR" ]; then
    python3 -m py_compile "$EVALUATOR" 2>/dev/null
    test_case "evaluator.py 语法正确" $?
fi

echo ""

# ============================================
# 测试总结
# ============================================
echo "========================================"
echo "  测试总结"
echo "========================================"
echo ""
echo -e "  总计: $TESTS_RUN 个测试"
echo -e "  ${GREEN}通过: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
    echo -e "  ${RED}失败: $TESTS_FAILED${NC}"
fi
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}✗ 有测试失败${NC}"
    exit 1
fi
