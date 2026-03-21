#!/bin/bash
# init.sh - 在项目目录初始化 Harness

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }

# Banner
cat << 'EOF'
   _    _                     _____ _    _ _               
  | |  | |                   / ____| |  | | |              
  | |  | |___  ___ _ __ ___ | |  __| |  | | |              
  | |  | / __|/ _ \ '__/ _ \| | |_ | |  | | |              
  | |__| \__ \  __/ | | (_) | |__| | |__| |_|              
   \____/|___/\___|_|  \___/ \_____|\____/(_)              
                                                            
  Agent Harness Setup - One command to rule them all
EOF

# Check args
if [ $# -eq 0 ]; then
    echo ""
    echo "Usage: $0 <project-type> [target-dir]"
    echo ""
    echo "Project Types:"
    echo "  nuwax       - Nuwax Agent OS 项目"
    echo "  electron    - Electron + Ant Design 项目"
    echo "  generic     - 通用项目"
    echo ""
    echo "Example:"
    echo "  $0 nuwax ."
    exit 1
fi

TYPE=$1
TARGET=${2:-.}

# Find monorepo root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONOREPO="$(dirname "$SCRIPT_DIR")"

info "Project type: $TYPE"
info "Target directory: $TARGET"

# Create target dir
mkdir -p "$TARGET"

# Copy based on type
case $TYPE in
    nuwax)
        info "Setting up Nuwax Harness..."
        cp -r "$MONOREPO/packages/agent-harness/harness/" "$TARGET/"
        cp -r "$MONOREPO/packages/nuwax-harness/harness/"* "$TARGET/harness/" 2>/dev/null || true
        cp "$MONOREPO/packages/nuwax-harness/CLAUDE.md" "$TARGET/" 2>/dev/null || true
        cp "$MONOREPO/packages/nuwax-harness/.cursorrules" "$TARGET/" 2>/dev/null || true
        ;;
    electron)
        info "Setting up Electron Harness..."
        cp -r "$MONOREPO/packages/agent-harness/harness/" "$TARGET/"
        cp -r "$MONOREPO/packages/electron-harness/harness/"* "$TARGET/harness/" 2>/dev/null || true
        cp "$MONOREPO/packages/electron-harness/CLAUDE.md" "$TARGET/" 2>/dev/null || true
        cp "$MONOREPO/packages/electron-harness/.cursorrules" "$TARGET/" 2>/dev/null || true
        ;;
    generic)
        info "Setting up Generic Harness..."
        cp -r "$MONOREPO/packages/agent-harness/harness/" "$TARGET/"
        cp -r "$MONOREPO/packages/generic-harness/harness/"* "$TARGET/harness/" 2>/dev/null || true
        cp "$MONOREPO/packages/generic-harness/CLAUDE.md" "$TARGET/" 2>/dev/null || true
        cp "$MONOREPO/packages/generic-harness/.cursorrules" "$TARGET/" 2>/dev/null || true
        ;;
    *)
        echo "Unknown type: $TYPE"
        exit 1
        ;;
esac

# Initialize state.json
mkdir -p "$TARGET/harness/feedback/state"
cat > "$TARGET/harness/feedback/state/state.json" << EOF
{
  "project": "",
  "version": "1.0.0",
  "type": "$TYPE",
  "lastUpdated": "$(date +%Y-%m-%d)",
  "currentTask": null,
  "taskStatus": "idle",
  "stage": "none",
  "checkpoints": {
    "CP1": "pending",
    "CP2": "pending",
    "CP3": "pending",
    "CP4": "pending",
    "CP5": "pending"
  },
  "gates": {
    "lint": "pending",
    "typecheck": "pending",
    "test": "pending",
    "build": "pending"
  },
  "constraints": {
    "maxFilesPerTask": 5
  },
  "recentChanges": []
}
EOF

# Make scripts executable
chmod +x "$TARGET/harness/"*.sh 2>/dev/null || true
chmod +x "$TARGET/harness"/*/*.sh 2>/dev/null || true
chmod +x "$TARGET/scripts"/*.sh 2>/dev/null || true

success "Setup complete!"
echo ""
echo "Next steps:"
echo "  1. cd $TARGET"
echo "  2. Update harness/feedback/state/state.json with your project name"
echo "  3. claude  # or open Cursor / Codex"
echo ""
