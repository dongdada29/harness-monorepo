#!/bin/bash
# run_eval.sh - 运行评估工具（Wrapper）

cd "$(dirname "$0")"

echo "==================================="
echo "Harness Evaluator"
echo "==================================="

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is required"
    exit 1
fi

# Run evaluator
python3 evaluator.py "$@"
