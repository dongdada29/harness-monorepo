#!/bin/bash
# 测试 setup.sh 脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓ $1${NC}"; }
fail() { echo -e "${RED}✗ $1${NC}"; }
info() { echo -e "${YELLOW}ℹ $1${NC}"; }

# 测试计数器
TESTS_PASSED=0
TESTS_FAILED=0

# 测试 setup.sh --help
test_help() {
    info "Testing: setup.sh --help"
    
    cd "$PROJECT_ROOT"
    if ./setup.sh --help | grep -q "Usage:"; then
        pass "setup.sh --help works"
        ((TESTS_PASSED++))
    else
        fail "setup.sh --help failed"
        ((TESTS_FAILED++))
    fi
}

# 测试 setup.sh 无效参数
test_invalid_param() {
    info "Testing: setup.sh with invalid param"
    
    cd "$PROJECT_ROOT"
    if ./setup.sh invalid_param 2>&1 | grep -q "未知项目类型"; then
        pass "setup.sh rejects invalid param"
        ((TESTS_PASSED++))
    else
        fail "setup.sh should reject invalid param"
        ((TESTS_FAILED++))
    fi
}

# 测试目录结构
test_directory_structure() {
    info "Testing: directory structure"
    
    cd "$PROJECT_ROOT"
    
    if [ -d "packages" ]; then
        pass "packages/ directory exists"
        ((TESTS_PASSED++))
    else
        fail "packages/ directory missing"
        ((TESTS_FAILED++))
    fi
    
    if [ -d "scripts" ]; then
        pass "scripts/ directory exists"
        ((TESTS_PASSED++))
    else
        fail "scripts/ directory missing"
        ((TESTS_FAILED++))
    fi
    
    if [ -f "setup.sh" ]; then
        pass "setup.sh exists"
        ((TESTS_PASSED++))
    else
        fail "setup.sh missing"
        ((TESTS_FAILED++))
    fi
}

# 测试 packages 完整性
test_packages() {
    info "Testing: packages integrity"
    
    cd "$PROJECT_ROOT/packages"
    
    local packages=("agent-harness" "nuwax-harness" "generic-harness")
    
    for pkg in "${packages[@]}"; do
        if [ -d "$pkg" ]; then
            if [ -f "$pkg/CLAUDE.md" ] && [ -f "$pkg/AGENTS.md" ]; then
                pass "Package $pkg is complete"
                ((TESTS_PASSED++))
            else
                fail "Package $pkg missing config files"
                ((TESTS_FAILED++))
            fi
        else
            fail "Package $pkg missing"
            ((TESTS_FAILED++))
        fi
    done
}

# 测试脚本可执行性
test_scripts_executable() {
    info "Testing: scripts are executable"
    
    cd "$PROJECT_ROOT/scripts"
    
    for script in *.sh; do
        if [ -x "$script" ]; then
            pass "$script is executable"
            ((TESTS_PASSED++))
        else
            fail "$script is not executable"
            ((TESTS_FAILED++))
        fi
    done
}

# 测试 setup.sh 集成（使用临时目录）
test_setup_integration() {
    info "Testing: setup.sh integration"
    
    local TEMP_DIR=$(mktemp -d)
    cd "$PROJECT_ROOT"
    
    # 测试 generic 类型
    if ./setup.sh generic "$TEMP_DIR/test-generic" > /dev/null 2>&1; then
        if [ -f "$TEMP_DIR/test-generic/CLAUDE.md" ]; then
            pass "setup.sh generic works"
            ((TESTS_PASSED++))
        else
            fail "setup.sh generic did not create CLAUDE.md"
            ((TESTS_FAILED++))
        fi
    else
        fail "setup.sh generic failed"
        ((TESTS_FAILED++))
    fi
    
    # 清理
    rm -rf "$TEMP_DIR"
}

# 运行所有测试
main() {
    echo "======================================"
    echo "  Harness Monorepo Test Suite"
    echo "======================================"
    echo ""
    
    test_help
    test_invalid_param
    test_directory_structure
    test_packages
    test_scripts_executable
    test_setup_integration
    
    echo ""
    echo "======================================"
    echo "  Test Results"
    echo "======================================"
    echo -e "  ${GREEN}Passed: $TESTS_PASSED${NC}"
    echo -e "  ${RED}Failed: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}All tests passed! ✓${NC}"
        exit 0
    else
        echo -e "${RED}Some tests failed! ✗${NC}"
        exit 1
    fi
}

main "$@"
