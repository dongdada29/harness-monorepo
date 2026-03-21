#!/bin/bash
# list.sh - 列出所有 Harness 配置

echo "==================================="
echo "Harness Monorepo - Available Packages"
echo "==================================="
echo ""

for pkg in packages/*; do
    if [ -d "$pkg" ]; then
        name=$(basename "$pkg")
        echo "📦 $name"
        echo "   ---"
        
        # Count files
        md_count=$(find "$pkg" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        sh_count=$(find "$pkg" -name "*.sh" 2>/dev/null | wc -l | tr -d ' ')
        
        echo "   📄 $md_count .md files"
        echo "   🔧 $sh_count .sh files"
        
        # Show key files
        if [ -f "$pkg/README.md" ]; then
            echo "   ✅ README.md"
        fi
        if [ -f "$pkg/CLAUDE.md" ]; then
            echo "   🤖 CLAUDE.md (Claude Code)"
        fi
        if [ -f "$pkg/.cursorrules" ]; then
            echo "   🎯 .cursorrules (Cursor)"
        fi
        if [ -f "$pkg/AGENTS.md" ]; then
            echo "   📋 AGENTS.md (Codex/OpenCode)"
        fi
        
        echo ""
    fi
done

echo "==================================="
echo "Usage:"
echo "  ./setup.sh <package> <target-dir>"
echo ""
echo "Example:"
echo "  ./setup.sh nuwax-harness /path/to/project"
echo "==================================="
