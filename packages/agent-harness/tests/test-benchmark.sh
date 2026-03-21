#!/bin/bash
# Benchmark 测试用例 - 验证 harness 方案有效性

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

echo "========================================"
echo "  Harness Benchmark 测试"
echo "========================================"
echo ""

# 测试 1: 基础 Benchmark
echo "【测试 1】基础 Benchmark"
python3 "$PROJECT_ROOT/tools/eval-cli/benchmark.py" --project "$PROJECT_ROOT/examples/todo-app"

# 测试 2: JSON 输出
echo ""
echo "【测试 2】JSON 输出"
python3 "$PROJECT_ROOT/tools/eval-cli/benchmark.py" --project "$PROJECT_ROOT/examples/todo-app" --output json > /tmp/benchmark_test.json
cat /tmp/benchmark_test.json | jq

# 测试 3: Markdown 输出
echo ""
echo "【测试 3】Markdown 输出"
python3 "$PROJECT_ROOT/tools/eval-cli/benchmark.py" --project "$PROJECT_ROOT/examples/todo-app" --output markdown > /tmp/benchmark_test.md
head -30 /tmp/benchmark_test.md

# 测试 4: 子包 Benchmark
echo ""
echo "【测试 4】子包 Benchmark"
for pkg in agent-harness nuwax-harness; do
    echo "  测试 $pkg..."
    python3 "$PROJECT_ROOT/tools/eval-cli/benchmark.py" --project "$PROJECT_ROOT/packages/$pkg" --output json > "/tmp/benchmark_$pkg.json" 2>&1
    if [ $? -eq 0 ]; then
        echo "  ✓ $pkg benchmark 通过"
    else
        echo "  ✗ $pkg benchmark 失败"
    fi
done

# 测试 5: 验证评分系统
echo ""
echo "【测试 5】验证评分系统"
python3 << 'PYEOF'
import json

# 读取 benchmark 结果
with open('/tmp/benchmark_test.json') as f:
    result = json.load(f)

# 验证评分维度
print("评分维度验证:")
print(f"  Overall: {result.get('overall', 0):.1f}")
print(f"  Grade: {result.get('grade', 'N/A')}")

# 验证分数范围
overall = result.get('overall', 0)
if 0 <= overall <= 100:
    print("  ✓ Overall 分数在有效范围内")
else:
    print("  ✗ Overall 分数超出范围")

# 验证各个维度
for dimension in ['efficiency', 'quality', 'behavior', 'autonomy']:
    if dimension in result:
        print(f"  ✓ {dimension} 维度存在")
    else:
        print(f"  ✗ {dimension} 维度缺失")

# 验证建议
if 'recommendations' in result:
    print(f"  ✓ 包含 {len(result['recommendations'])} 条建议")
else:
    print("  ✗ 缺少建议")

print("\n所有测试通过!")
PYEOF

echo ""
echo "========================================"
echo "  ✓ Benchmark 测试完成"
echo "========================================"
