#!/bin/bash
# 状态更新脚本 - 更新 harness/feedback/state/state.json

set -e

STATE_FILE="harness/feedback/state/state.json"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 使用帮助
usage() {
    cat << EOF
Usage: $0 <command> [args]

Commands:
  start <task>       - 开始任务
  done               - 完成任务
  blocked <reason>   - 报告阻塞
  verify             - 运行验证
  gate <name> <status> - 更新门禁状态
  checkpoint <cp> <status> - 更新检查点状态
  show               - 显示当前状态
  reset              - 重置状态

Examples:
  $0 start "实现登录功能"
  $0 done
  $0 blocked "缺少 API 文档"
  $0 gate lint passed
  $0 checkpoint CP1 completed
  $0 show
  $0 reset
EOF
}

# 检查 state.json 是否存在
check_state() {
    if [ ! -f "$STATE_FILE" ]; then
        error "state.json not found: $STATE_FILE"
        info "Run: ./setup.sh <type> to initialize"
        exit 1
    fi
}

# 开始任务
cmd_start() {
    local task="$1"
    
    if [ -z "$task" ]; then
        error "Task description required"
        usage
        exit 1
    fi
    
    check_state
    
    # 更新状态
    tmp=$(mktemp)
    jq ".currentTask = \"$task\" | .taskStatus = \"in_progress\" | .stage = \"CP1\" | .lastUpdated = \"$(date +%Y-%m-%d)\"" "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    
    # 添加变更记录
    add_change "started" "$task"
    
    success "Task started: $task"
    show_status
}

# 完成任务
cmd_done() {
    check_state
    
    # 获取当前任务
    local task=$(jq -r '.currentTask' "$STATE_FILE")
    
    if [ "$task" == "null" ] || [ -z "$task" ]; then
        error "No task in progress"
        exit 1
    fi
    
    # 更新状态
    tmp=$(mktemp)
    jq ".taskStatus = \"completed\" | .lastUpdated = \"$(date +%Y-%m-%d)\" | .checkpoints.CP5 = \"completed\"" "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    
    # 添加变更记录
    add_change "completed" "$task"
    
    success "Task completed: $task"
    show_status
}

# 报告阻塞
cmd_blocked() {
    local reason="$1"
    
    if [ -z "$reason" ]; then
        error "Reason required"
        usage
        exit 1
    fi
    
    check_state
    
    # 更新状态
    tmp=$(mktemp)
    jq ".taskStatus = \"blocked\" | .lastUpdated = \"$(date +%Y-%m-%d)\"" "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    
    # 添加变更记录
    add_change "blocked" "$reason"
    
    warn "Task blocked: $reason"
    show_status
}

# 运行验证
cmd_verify() {
    check_state
    
    info "Running quality gates..."
    
    local all_passed=true
    
    # Gate 1: Lint
    if npm run lint > /dev/null 2>&1; then
        cmd_gate lint passed
        success "✓ Gate 1: Lint passed"
    else
        cmd_gate lint failed
        error "✗ Gate 1: Lint failed"
        all_passed=false
    fi
    
    # Gate 2: Typecheck
    if npm run typecheck > /dev/null 2>&1; then
        cmd_gate typecheck passed
        success "✓ Gate 2: Typecheck passed"
    else
        cmd_gate typecheck failed
        error "✗ Gate 2: Typecheck failed"
        all_passed=false
    fi
    
    # Gate 3: Test
    if npm test > /dev/null 2>&1; then
        cmd_gate test passed
        success "✓ Gate 3: Test passed"
    else
        cmd_gate test failed
        error "✗ Gate 3: Test failed"
        all_passed=false
    fi
    
    # Gate 4: Build
    if npm run build > /dev/null 2>&1; then
        cmd_gate build passed
        success "✓ Gate 4: Build passed"
    else
        cmd_gate build failed
        error "✗ Gate 4: Build failed"
        all_passed=false
    fi
    
    echo ""
    
    if [ "$all_passed" = true ]; then
        success "All gates passed! ✓"
        return 0
    else
        error "Some gates failed! ✗"
        return 1
    fi
}

# 更新门禁状态
cmd_gate() {
    local gate="$1"
    local status="$2"
    
    if [ -z "$gate" ] || [ -z "$status" ]; then
        error "Gate name and status required"
        usage
        exit 1
    fi
    
    check_state
    
    # 验证 gate 名称
    if ! echo "lint typecheck test build" | grep -qw "$gate"; then
        error "Invalid gate: $gate"
        exit 1
    fi
    
    # 验证状态
    if ! echo "pending passed failed" | grep -qw "$status"; then
        error "Invalid status: $status"
        exit 1
    fi
    
    # 更新状态
    tmp=$(mktemp)
    jq ".gates.$gate = \"$status\" | .lastUpdated = \"$(date +%Y-%m-%d)\"" "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    
    success "Gate $gate: $status"
}

# 更新检查点状态
cmd_checkpoint() {
    local cp="$1"
    local status="$2"
    
    if [ -z "$cp" ] || [ -z "$status" ]; then
        error "Checkpoint name and status required"
        usage
        exit 1
    fi
    
    check_state
    
    # 验证 checkpoint 名称
    if ! echo "CP1 CP2 CP3 CP4 CP5" | grep -qw "$cp"; then
        error "Invalid checkpoint: $cp"
        exit 1
    fi
    
    # 验证状态
    if ! echo "pending in_progress completed" | grep -qw "$status"; then
        error "Invalid status: $status"
        exit 1
    fi
    
    # 更新状态
    tmp=$(mktemp)
    jq ".checkpoints.$cp = \"$status\" | .stage = \"$cp\" | .lastUpdated = \"$(date +%Y-%m-%d)\"" "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
    
    success "Checkpoint $cp: $status"
}

# 显示状态
show_status() {
    check_state
    
    echo ""
    echo "======================================"
    echo "  Harness State"
    echo "======================================"
    echo ""
    
    # 基本信息
    local project=$(jq -r '.project' "$STATE_FILE")
    local task=$(jq -r '.currentTask' "$STATE_FILE")
    local status=$(jq -r '.taskStatus' "$STATE_FILE")
    local stage=$(jq -r '.stage' "$STATE_FILE")
    
    echo "Project: ${project:-unknown}"
    echo "Task: ${task:-none}"
    echo "Status: $status"
    echo "Stage: $stage"
    echo ""
    
    # 检查点
    echo "Checkpoints:"
    jq -r '.checkpoints | to_entries[] | "  \(.key): \(.value)"' "$STATE_FILE"
    echo ""
    
    # 门禁
    echo "Quality Gates:"
    jq -r '.gates | to_entries[] | "  \(.key): \(.value)"' "$STATE_FILE"
    echo ""
    
    # 最近变更
    echo "Recent Changes:"
    jq -r '.recentChanges[-3:][] | "  [\(.timestamp)] \(.type): \(.description)"' "$STATE_FILE" 2>/dev/null || echo "  none"
    echo ""
}

# 重置状态
cmd_reset() {
    check_state
    
    warn "This will reset all state to initial values"
    read -p "Are you sure? (y/N): " confirm
    
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        # 重置状态
        tmp=$(mktemp)
        jq ".currentTask = null | .taskStatus = \"idle\" | .stage = \"none\" | .checkpoints = {CP1: \"pending\", CP2: \"pending\", CP3: \"pending\", CP4: \"pending\", CP5: \"pending\"} | .gates = {lint: \"pending\", typecheck: \"pending\", test: \"pending\", build: \"pending\"} | .lastUpdated = \"$(date +%Y-%m-%d)\" | .recentChanges = []" "$STATE_FILE" > "$tmp"
        mv "$tmp" "$STATE_FILE"
        
        success "State reset"
    else
        info "Cancelled"
    fi
}

# 添加变更记录
add_change() {
    local type="$1"
    local description="$2"
    
    check_state
    
    # 添加新变更到开头（最新的在前）
    tmp=$(mktemp)
    jq ".recentChanges = [{timestamp: \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\", type: \"$type\", description: \"$description\"}] + .recentChanges | .recentChanges = .recentChanges[0:10]" "$STATE_FILE" > "$tmp"
    mv "$tmp" "$STATE_FILE"
}

# 主函数
main() {
    if [ $# -eq 0 ]; then
        usage
        exit 0
    fi
    
    local command="$1"
    shift
    
    case "$command" in
        start)
            cmd_start "$@"
            ;;
        done)
            cmd_done
            ;;
        blocked)
            cmd_blocked "$@"
            ;;
        verify)
            cmd_verify
            ;;
        gate)
            cmd_gate "$@"
            ;;
        checkpoint)
            cmd_checkpoint "$@"
            ;;
        show)
            show_status
            ;;
        reset)
            cmd_reset
            ;;
        -h|--help)
            usage
            ;;
        *)
            error "Unknown command: $command"
            usage
            exit 1
            ;;
    esac
}

main "$@"
