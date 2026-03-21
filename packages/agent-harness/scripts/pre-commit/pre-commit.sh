#!/bin/bash
# pre-commit hook
# 放置在 .git/hooks/pre-commit 或通过 husky 配置

set -e

echo "🔍 Running pre-commit quality checks..."

# 1. Lint
echo "📝 Linting..."
npm run lint || {
    echo "❌ Lint failed. Fix errors before committing."
    exit 1
}

# 2. Typecheck
echo "📦 Type checking..."
npx tsc --noEmit || {
    echo "❌ Typecheck failed. Fix errors before committing."
    exit 1
}

# 3. Tests
echo "🧪 Running tests..."
npm test || {
    echo "❌ Tests failed. Fix errors before committing."
    exit 1
}

echo "✅ All pre-commit checks passed!"
