#!/bin/bash
# Harness 验证脚本 - 验证方案有效性

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

pass() { echo -e "${GREEN}✓ $1${NC}"; ((TESTS_PASSED++)); }
fail() { echo -e "${RED}✗ $1${NC}"; ((TESTS_FAILED++)); }
info() { echo -e "${BLUE}ℹ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }

TESTS_PASSED=0
TESTS_FAILED=0

# 验证子包完整性
validate_package() {
    local pkg=$1
    local pkg_dir="$PROJECT_ROOT/packages/$pkg"
    
    echo ""
    echo "========================================"
    echo "  验证: $pkg"
    echo "========================================"
    
    # 检查必需文件
    local required_files=("CLAUDE.md" "AGENTS.md" ".cursorrules" "README.md" "CONTRIBUTING.md")
    for file in "${required_files[@]}"; do
        if [ -f "$pkg_dir/$file" ]; then
            pass "$file 存在"
        else
            fail "$file 缺失"
        fi
    done
    
    # 检查文档完整性
    if [ -f "$pkg_dir/CLAUDE.md" ]; then
        if grep -q "工作流" "$pkg_dir/CLAUDE.md" && grep -q "质量门禁" "$pkg_dir/CLAUDE.md"; then
            pass "CLAUDE.md 包含核心概念"
        else
            fail "CLAUDE.md 缺少核心概念"
        fi
    fi
    
    # 检查约束文件
    if [ -d "$pkg_dir/harness" ]; then
        if [ -f "$pkg_dir/harness/base/constraints.md" ]; then
            pass "约束文件存在"
        else
            fail "约束文件缺失"
        fi
    fi
    
    # 运行 benchmark
    if [ -f "$PROJECT_ROOT/tools/eval-cli/benchmark.py" ]; then
        info "运行 benchmark..."
        cd "$pkg_dir"
        python3 "$PROJECT_ROOT/tools/eval-cli/benchmark.py" --project . --output json > /tmp/benchmark_$pkg.json 2>&1
        if [ $? -eq 0 ]; then
            pass "Benchmark 通过"
            
            # 提取分数
            local score=$(jq -r '.overall // 0' /tmp/benchmark_$pkg.json 2>/dev/null || echo "0")
            info "Benchmark 分数: $score"
        else
            fail "Benchmark 失败"
        fi
    fi
}

# 验证示例项目
validate_examples() {
    echo ""
    echo "========================================"
    echo "  验证: 示例项目"
    echo "========================================"
    
    local example_dir="$PROJECT_ROOT/examples/todo-app"
    
    if [ -d "$example_dir" ]; then
        pass "示例项目存在"
        
        # 检查核心文件
        local core_files=("src/App.tsx" "src/hooks/useTodos.ts" "tests/useTodos.test.ts" "package.json")
        for file in "${core_files[@]}"; do
            if [ -f "$example_dir/$file" ]; then
                pass "示例文件存在: $file"
            else
                fail "示例文件缺失: $file"
            fi
        done
        
        # 检查工作流文档
        if [ -f "$example_dir/README.md" ]; then
            if grep -q "CP1" "$example_dir/README.md" && grep -q "CP5" "$example_dir/README.md"; then
                pass "示例文档包含完整工作流"
            else
                fail "示例文档缺少工作流说明"
            fi
        fi
    else
        fail "示例项目不存在"
    fi
}

# 验证工具链
validate_tools() {
    echo ""
    echo "========================================"
    echo "  验证: 工具链"
    echo "========================================"
    
    # 检查脚本
    local scripts=("setup.sh" "scripts/check.sh" "scripts/cleanup.sh" "scripts/list.sh")
    for script in "${scripts[@]}"; do
        if [ -f "$PROJECT_ROOT/$script" ]; then
            if [ -x "$PROJECT_ROOT/$script" ]; then
                pass "$script 可执行"
            else
                fail "$script 不可执行"
            fi
        else
            fail "$script 不存在"
        fi
    done
    
    # 检查 Python 工具
    if [ -f "$PROJECT_ROOT/tools/eval-cli/benchmark.py" ]; then
        pass "benchmark.py 存在"
        
        # 验证 Python 语法
        if python3 -m py_compile "$PROJECT_ROOT/tools/eval-cli/benchmark.py" 2>/dev/null; then
            pass "benchmark.py 语法正确"
        else
            fail "benchmark.py 语法错误"
        fi
    else
        fail "benchmark.py 不存在"
    fi
}

# 验证文档完整性
validate_docs() {
    echo ""
    echo "========================================"
    echo "  验证: 文档完整性"
    echo "========================================"
    
    local docs=("README.md" "QUICKSTART.md" "docs/troubleshooting.md" "README_CN.md")
    for doc in "${docs[@]}"; do
        if [ -f "$PROJECT_ROOT/$doc" ]; then
            pass "$doc 存在"
            
            # 检查文档长度
            local lines=$(wc -l < "$PROJECT_ROOT/$doc")
            if [ "$lines" -gt 50 ]; then
                pass "$doc 内容充实 ($lines 行)"
            else
                warn "$doc 内容较少 ($lines 行)"
            fi
        else
            fail "$doc 不存在"
        fi
    done
}

# 运行综合 benchmark
run_comprehensive_benchmark() {
    echo ""
    echo "========================================"
    echo "  综合评估"
    echo "========================================"
    
    cd "$PROJECT_ROOT"
    
    # 运行整体 benchmark
    if [ -f "tools/eval-cli/benchmark.py" ]; then
        info "运行综合 benchmark..."
        python3 tools/eval-cli/benchmark.py --project . --output json > /tmp/overall_benchmark.json 2>&1
        
        if [ $? -eq 0 ]; then
            pass "综合 benchmark 通过"
            
            # 提取并显示分数
            local overall=$(jq -r '.overall // 0' /tmp/overall_benchmark.json 2>/dev/null || echo "0")
            local efficiency=$(jq -r '.efficiency // {}' /tmp/overall_benchmark.json 2>/dev/null)
            local quality=$(jq -r '.quality // {}' /tmp/overall_benchmark.json 2>/dev/null)
            local behavior=$(jq -r '.behavior // {}' /tmp/overall_benchmark.json 2>/dev/null)
            local autonomy=$(jq -r '.autonomy // {}' /tmp/overall_benchmark.json 2>/dev/null)
            
            echo ""
            echo "Benchmark 结果:"
            echo "  Overall: $overall"
            echo "  Efficiency: $(echo $efficiency | jq -r 'to_entries | map("\(.key): \(.value)") | join(", ")')"
            echo "  Quality: $(echo $quality | jq -r 'to_entries | map("\(.key): \(.value)") | join(", ")')"
            echo "  Behavior: $(echo $behavior | jq -r 'to_entries | map("\(.key): \(.value)") | join(", ")')"
            echo "  Autonomy: $(echo $autonomy | jq -r 'to_entries | map("\(.key): \(.value)") | join(", ")')"
        else
            fail "综合 benchmark 失败"
        fi
    fi
}

# 生成报告
generate_report() {
    echo ""
    echo "========================================"
    echo "  验证报告"
    echo "========================================"
    echo ""
    echo -e "  ${GREEN}通过: $TESTS_PASSED${NC}"
    echo -e "  ${RED}失败: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        echo -e "${GREEN}✓ 所有验证通过！方案有效！${NC}"
        echo ""
        echo "质量评级:"
        local pass_rate=$((TESTS_PASSED * 100 / (TESTS_PASSED + TESTS_FAILED)))
        if [ $pass_rate -ge 95 ]; then
            echo "  S+ (World Class)"
        elif [ $pass_rate -ge 90 ]; then
            echo "  S (Excellent)"
        elif [ $pass_rate -ge 85 ]; then
            echo "  A+ (Outstanding)"
        elif [ $pass_rate -ge 80 ]; then
            echo "  A (Very Good)"
        elif [ $pass_rate -ge 75 ]; then
            echo "  B+ (Good)"
        elif [ $pass_rate -ge 70 ]; then
            echo "  B (Satisfactory)"
        else
            echo "  C (Marginal)"
        fi
        exit 0
    else
        echo -e "${RED}✗ 部分验证失败，请检查${NC}"
        exit 1
    fi
}

# 主函数
main() {
    echo "========================================"
    echo "  Harness 方案有效性验证"
    echo "========================================"
    echo ""
    
    # 验证各个子包
    validate_package "agent-harness"
    validate_package "nuwax-harness"
    validate_package "electron-harness"
    validate_package "generic-harness"
    
    # 验证示例
    validate_examples
    
    # 验证工具链
    validate_tools
    
    # 验证文档
    validate_docs
    
    # 运行综合 benchmark
    run_comprehensive_benchmark
    
    # 生成报告
    generate_report
}

main "$@"
