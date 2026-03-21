#!/bin/bash
# evaluator.sh - Simple shell-based evaluator (no Python required)

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT=${1:-.}

echo "==================================="
echo "Harness Evaluator (Shell)"
echo "==================================="
echo "Project: $PROJECT"
echo ""

# Check state.json
STATE_FILE="$PROJECT/harness/feedback/state/state.json"
if [ -f "$STATE_FILE" ]; then
    echo "--- State Metrics ---"
    
    TASKS_COMPLETED=$(grep -o '"tasksCompleted":[0-9]*' "$STATE_FILE" 2>/dev/null | cut -d: -f2 || echo "0")
    TASKS_BLOCKED=$(grep -o '"tasksBlocked":[0-9]*' "$STATE_FILE" 2>/dev/null | cut -d: -f2 || echo "0")
    
    echo "Tasks Completed: $TASKS_COMPLETED"
    echo "Tasks Blocked: $TASKS_BLOCKED"
    
    TOTAL=$((TASKS_COMPLETED + TASKS_BLOCKED))
    if [ "$TOTAL" -gt 0 ]; then
        COMPLETE_RATE=$((TASKS_COMPLETED * 100 / TOTAL))
        BLOCK_RATE=$((TASKS_BLOCKED * 100 / TOTAL))
        echo "Completion Rate: ${COMPLETE_RATE}%"
        echo "Block Rate: ${BLOCK_RATE}%"
    fi
else
    echo "Warning: state.json not found"
fi

echo ""

# Check code quality
echo "--- Code Quality ---"
CONSOLE_LOGS=$(grep -r "console\.log" "$PROJECT/src" --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l | tr -d ' ')
DEBUGGERS=$(grep -r "debugger" "$PROJECT/src" --include="*.ts" --include="*.tsx" 2>/dev/null | wc -l | tr -d ' ')
UNMARKED_TODOS=$(grep -r "TODO" "$PROJECT/src" --include="*.ts" --include="*.tsx" 2>/dev/null | grep -v "#" | wc -l | tr -d ' ')

echo "console.log count: $CONSOLE_LOGS"
echo "debugger count: $DEBUGGERS"
echo "unmarked TODO count: $UNMARKED_TODOS"

echo ""

# Recommendations
echo "--- Recommendations ---"
if [ "$CONSOLE_LOGS" -gt 0 ]; then
    echo "1. Clean up $CONSOLE_LOGS console.log statements"
fi
if [ "$DEBUGGERS" -gt 0 ]; then
    echo "2. Remove $DEBUGGERS debugger statements"
fi
if [ "$UNMARKED_TODOS" -gt 0 ]; then
    echo "3. Tag $UNMARKED_TODOS TODOs with issue references"
fi
if [ ! -f "$STATE_FILE" ]; then
    echo "4. Initialize harness: cp -r harness/feedback/state/state.json"
fi
if [ "$BLOCK_RATE" -gt 10 ]; then
    echo "5. Block rate is high (${BLOCK_RATE}%)"
fi

echo ""
echo "==================================="
