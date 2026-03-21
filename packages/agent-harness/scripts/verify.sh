#!/bin/bash
# verify.sh - Quality Gate Verification
# Usage: ./scripts/verify.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "🔍 Running Quality Gates"
echo "======================================"
echo ""

FAILED=0

# Gate 1: Lint
echo "Gate 1: Lint"
echo "   └─ npm run lint"
if npm run lint > /tmp/lint.log 2>&1; then
    echo -e "   └─ ${GREEN}✅ Passed${NC}"
else
    echo -e "   └─ ${RED}❌ Failed${NC}"
    cat /tmp/lint.log
    FAILED=1
fi
echo ""

# Gate 2: Typecheck
echo "Gate 2: Typecheck"
echo "   └─ npx tsc --noEmit"
if npx tsc --noEmit > /tmp/tsc.log 2>&1; then
    echo -e "   └─ ${GREEN}✅ Passed${NC}"
else
    echo -e "   └─ ${RED}❌ Failed${NC}"
    cat /tmp/tsc.log
    FAILED=1
fi
echo ""

# Gate 3: Test
echo "Gate 3: Test"
echo "   └─ npm test"
if npm test > /tmp/test.log 2>&1; then
    echo -e "   └─ ${GREEN}✅ Passed${NC}"
else
    echo -e "   └─ ${RED}❌ Failed${NC}"
    cat /tmp/test.log
    FAILED=1
fi
echo ""

# Gate 4: Build
echo "Gate 4: Build"
echo "   └─ npm run build"
if npm run build > /tmp/build.log 2>&1; then
    echo -e "   └─ ${GREEN}✅ Passed${NC}"
else
    echo -e "   └─ ${RED}❌ Failed${NC}"
    cat /tmp/build.log
    FAILED=1
fi
echo ""

echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All gates passed!${NC}"
else
    echo -e "${RED}❌ Some gates failed.${NC}"
fi
echo "======================================"

exit $FAILED
