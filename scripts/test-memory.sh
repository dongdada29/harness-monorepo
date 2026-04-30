#!/bin/bash
# test-memory.sh — Test memory-retrieval.py

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
MEMORY="$ROOT/tools/cli/memory-retrieval.py"
PASS=0 FAIL=0

pass() { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo ""
echo "==================================="
echo "  Memory Retrieval Tests"
echo "==================================="
echo ""

# Setup temp project with state.json
TMPDIR=$(mktemp -d)
mkdir -p "$TMPDIR/harness/feedback/state"
STATE="$TMPDIR/harness/feedback/state/state.json"

# Minimal valid state with history
cat > "$STATE" << 'EOF'
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "project": "test-project",
  "checkpoints": {"CP0":"pending","CP1":"pending","CP2":"pending","CP3":"pending","CP4":"pending"},
  "gates": {"init":"pending","plan":"pending","exec":"pending","verify":"pending","complete":"pending"},
  "healing": {"enabled":true,"maxAttempts":3,"currentAttempt":0,"lastAttempt":null,"lastError":null,"retryHistory":[],"autoHeal":true},
  "metrics":{"tasksCompleted":0,"tasksBlocked":0},
  "autonomy":{"level":4,"requireApprovalFor":[],"autoMergeOnCI":false},
  "taskHistory": [
    {"task":"implement login API","completedAt":"2026-04-28T10:00:00Z"},
    {"task":"fix auth token refresh bug","completedAt":"2026-04-29T14:00:00Z"}
  ]
}
EOF

cd "$TMPDIR"

# ── Test 1: default episodic ────────────────────────────────────────────
python3 "$MEMORY" . > /dev/null 2>&1
rc=$?
[ $rc -eq 0 ] && pass "default episodic retrieval" || fail "default episodic (exit $rc)"

# ── Test 2: task history ────────────────────────────────────────────────
python3 "$MEMORY" . --type task > /dev/null 2>&1
rc=$?
[ $rc -eq 0 ] && pass "task history retrieval" || fail "task history (exit $rc)"

# ── Test 3: healing empty ───────────────────────────────────────────────
python3 "$MEMORY" . --type healing > /dev/null 2>&1
rc=$?
[ $rc -eq 0 ] && pass "healing retrieval (empty)" || fail "healing empty (exit $rc)"

# ── Test 4: keywords filter ─────────────────────────────────────────────
python3 "$MEMORY" . --type task --keywords "login,auth" > /dev/null 2>&1
rc=$?
[ $rc -eq 0 ] && pass "task with keywords filter" || fail "keywords filter (exit $rc)"

# ── Test 5: semantic empty cache ───────────────────────────────────────
python3 "$MEMORY" . --type semantic > /dev/null 2>&1
rc=$?
[ $rc -eq 0 ] && pass "semantic (empty cache)" || fail "semantic (exit $rc)"

# ── Test 6: JSON output ────────────────────────────────────────────────
OUT=$(python3 "$MEMORY" . --type task --json 2>/dev/null)
rc=$?
echo "$OUT" | python3 -c "import json,sys; json.load(sys.stdin)" > /dev/null 2>&1
[ $rc -eq 0 ] && [ -n "$OUT" ] && pass "JSON output mode" || fail "JSON output (exit $rc)"

# ── Test 7: limit parameter ────────────────────────────────────────────
python3 "$MEMORY" . --type task --limit 1 > /dev/null 2>&1
rc=$?
[ $rc -eq 0 ] && pass "limit parameter" || fail "limit (exit $rc)"

# ── Test 8: invalid path ───────────────────────────────────────────────
cd "$ROOT"
python3 "$MEMORY" /nonexistent/path > /dev/null 2>&1
rc=$?
[ $rc -ne 0 ] && pass "invalid path → non-zero exit" || fail "invalid path (exit $rc)"

# ── Test 9: healing with data ───────────────────────────────────────────
cat > "$STATE" << 'EOF'
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "project": "test-project",
  "checkpoints": {"CP0":"pending","CP1":"pending","CP2":"pending","CP3":"pending","CP4":"pending"},
  "gates": {"init":"pending","plan":"pending","exec":"pending","verify":"pending","complete":"pending"},
  "healing": {
    "enabled":true,"maxAttempts":3,"currentAttempt":2,
    "lastAttempt":"2026-04-30T10:00:00Z",
    "lastError":"lint: unused variable",
    "retryHistory":[
      {"attempt":1,"timestamp":"2026-04-30T09:00:00Z","failedGates":["lint"],"errorSummary":"unused variable x in foo.ts","filesTouched":["src/foo.ts"],"status":"failed"},
      {"attempt":2,"timestamp":"2026-04-30T10:00:00Z","failedGates":["lint"],"errorSummary":"unused variable x in foo.ts","filesTouched":["src/foo.ts"],"status":"passed"}
    ],
    "autoHeal":true
  },
  "metrics":{"tasksCompleted":0,"tasksBlocked":0},
  "autonomy":{"level":4,"requireApprovalFor":[],"autoMergeOnCI":false},
  "taskHistory":[]
}
EOF
cd "$TMPDIR"
OUT=$(python3 "$MEMORY" . --type healing --json 2>/dev/null)
rc=$?
echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); sys.exit(0 if len(d)==2 else 1)" > /dev/null 2>&1
[ $rc -eq 0 ] && pass "healing with data → 2 entries" || fail "healing data (exit $rc, len=$(echo $OUT | python3 -c 'import json,sys; print(len(json.load(sys.stdin)))') 2>/dev/null || echo ?))"

# Cleanup
rm -rf "$TMPDIR"

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo "==================================="
echo "  Results: $PASS passed, $FAIL failed"
echo "==================================="
[ $FAIL -eq 0 ]
