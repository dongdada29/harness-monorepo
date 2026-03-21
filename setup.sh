#!/bin/bash
# Harness Setup - 一键安装脚本
# Usage: ./setup.sh <project-type> [target-dir]
# Example: ./setup.sh nuwax
#         ./setup.sh electron /path/to/project

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Colors for echo
info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
banner() {
echo -e "${BLUE}"
cat << 'EOF'
   _    _                     _____ _    _ _               
  | |  | |                   / ____| |  | | |              
  | |  | |___  ___ _ __ ___ | |  __| |  | | |              
  | |  | / __|/ _ \ '__/ _ \| | |_ | |  | | |              
  | |__| \__ \  __/ | | (_) | |__| | |__| |_|              
   \____/|___/\___|_|  \___/ \_____|\____/(_)              
                                                          
  Agent Harness Setup - One command to rule them all
EOF
echo -e "${NC}"
}

# Usage
usage() {
    echo "Usage: $0 <project-type> [target-dir]"
    echo ""
    echo "Project Types:"
    echo "  nuwax     - Nuwax Agent OS 项目"
    echo "  electron  - Electron + Ant Design 项目"
    echo "  generic   - 通用项目"
    echo "  all       - 安装所有项目配置"
    echo ""
    echo "Examples:"
    echo "  $0 nuwax /path/to/nuwax-project"
    echo "  $0 electron ."
    echo "  $0 all"
    echo ""
    echo "Agent Configs:"
    echo "  Claude Code: CLAUDE.md"
    echo "  Cursor:      .cursorrules"
    echo "  Codex:      AGENTS.md"
}

# Check prerequisites
check_prereq() {
    info "检查前置条件..."
    
    if [ ! -d "packages" ]; then
        error "请在 harness-monorepo 目录下运行"
        exit 1
    fi
    
    if ! command -v rsync &> /dev/null; then
        error "需要 rsync，请先安装: brew install rsync"
        exit 1
    fi
    
    success "前置检查通过"
}

# Copy agent config
copy_agent_config() {
    local target=$1
    local package=$2
    
    info "复制 Agent 配置文件..."
    
    # Claude Code
    if [ -f "packages/$package/CLAUDE.md" ]; then
        cp packages/$package/CLAUDE.md "$target/CLAUDE.md"
        success "已安装: CLAUDE.md (Claude Code)"
    fi
    
    # Cursor
    if [ -f "packages/$package/.cursorrules" ]; then
        cp packages/$package/.cursorrules "$target/.cursorrules"
        success "已安装: .cursorrules (Cursor)"
    fi
    
    # Codex / OpenCode
    if [ -f "packages/$package/AGENTS.md" ]; then
        cp packages/$package/AGENTS.md "$target/AGENTS.md"
        success "已安装: AGENTS.md (Codex/OpenCode)"
    fi
}

# Copy project harness
copy_harness() {
    local type=$1
    local target=$2
    
    info "复制 Harness 配置..."
    
    case $type in
        nuwax)
            if [ -d "packages/agent-harness" ]; then
                rsync -av --exclude='.git' packages/agent-harness/harness/ "$target/harness/"
                success "已安装: agent-harness (通用配置)"
            fi
            if [ -d "packages/nuwax-harness" ]; then
                rsync -av --exclude='.git' packages/nuwax-harness/ "$target/"
                success "已安装: nuwax-harness (Nuwax 专用)"
            fi
            ;;
        electron)
            if [ -d "packages/agent-harness" ]; then
                rsync -av --exclude='.git' packages/agent-harness/harness/ "$target/harness/"
                success "已安装: agent-harness (通用配置)"
            fi
            if [ -d "packages/electron-harness" ]; then
                rsync -av --exclude='.git' packages/electron-harness/ "$target/"
                success "已安装: electron-harness (Electron 专用)"
            fi
            ;;
        generic)
            if [ -d "packages/agent-harness" ]; then
                rsync -av --exclude='.git' packages/agent-harness/harness/ "$target/harness/"
                success "已安装: agent-harness (通用配置)"
            fi
            if [ -d "packages/generic-harness" ]; then
                rsync -av --exclude='.git' packages/generic-harness/ "$target/"
                success "已安装: generic-harness (通用模板)"
            fi
            ;;
    esac
}

# Setup state.json
setup_state() {
    local target=$1
    local type=$2
    
    info "初始化状态文件..."
    
    mkdir -p "$target/harness/feedback/state"
    
    cat > "$target/harness/feedback/state/state.json" << EOF
{
  "project": "",
  "version": "1.0.0",
  "type": "$type",
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
    
    success "已初始化: state.json"
}

# Make scripts executable
setup_scripts() {
    local target=$1
    
    if [ -d "$target/scripts" ]; then
        chmod +x "$target/scripts"/*.sh 2>/dev/null || true
        chmod +x "$target/scripts"/*/*.sh 2>/dev/null || true
        success "已设置: 脚本执行权限"
    fi
}

# Print next steps
next_steps() {
    local type=$1
    
    echo ""
    echo -e "${GREEN}======================================${NC}"
    success "安装完成！"
    echo -e "${GREEN}======================================${NC}"
    echo ""
    echo "下一步："
    echo "  1. 进入你的项目目录"
    echo "  2. 启动 Claude Code: claude"
    echo "     或 Cursor / Codex"
    echo "  3. 使用 /start <任务> 开始工作"
    echo ""
    echo "可用命令："
    echo "  /state   - 查看状态"
    echo "  /start   - 开始任务"
    echo "  /verify  - 运行验证"
    echo "  /done    - 完成任务"
    echo "  /blocked - 报告阻塞"
    echo ""
}

# Main
main() {
    banner
    
    if [ $# -eq 0 ] || [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
        usage
        exit 0
    fi
    
    check_prereq
    
    local type=$1
    local target=${2:-.}
    
    # Validate type
    case $type in
        nuwax|electron|generic|all) ;;
        *)
            error "未知项目类型: $type"
            usage
            exit 1
            ;;
    esac
    
    info "开始安装: ${type}"
    info "目标目录: ${target}"
    echo ""
    
    if [ "$type" == "all" ]; then
        warn "all 模式会为每种项目类型创建子目录"
        exit 1
    fi
    
    # Create target dir if not exists
    mkdir -p "$target"
    
    # Install
    copy_agent_config "$target" "agent-harness"
    copy_harness "$type" "$target"
    setup_state "$target" "$type"
    setup_scripts "$target"
    
    next_steps "$type"
}

main "$@"
