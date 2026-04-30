#!/bin/bash
# test-validator.sh — Test state-validator.py
# No set -e so we can run all tests

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VALIDATOR="$ROOT/tools/validator/state-validator.py"
PASS=0 FAIL=0

pass() { echo "  ✅ $1"; PASS=$((PASS+1)); }
fail() { echo "  ❌ $1"; FAIL=$((FAIL+1)); }

echo ""
echo "==================================="
echo "  State Validator Tests"
echo "==================================="
echo ""

# ── Test 1: valid state.json ──────────────────────────────────────────────
python3 "$VALIDATOR" "$ROOT/packages/agent-harness/harness/feedback/state/state.json" > /dev/null 2>&1
rc=$?
if [ $rc -eq 0 ]; then pass "agent-harness state valid"; else fail "agent-harness state valid (got exit $rc)"; fi

# ── Test 2: missing required fields → must exit non-zero ─────────────────
TMP_INVALID=$(mktemp)
echo '{"_schema":"harness-state-v2","version":"2.0.0"}' > "$TMP_INVALID"
python3 "$VALIDATOR" "$TMP_INVALID" > /dev/null 2>&1
rc=$?
if [ $rc -eq 1 ]; then pass "missing required fields → rejected"; else fail "missing required fields (got exit $rc)"; fi
rm -f "$TMP_INVALID"

# ── Test 3: wrong schema version → must exit non-zero ──────────────────
TMP_WRONG=$(mktemp)
echo '{"_schema":"harness-v1","version":"1.0.0","project":"x","checkpoints":{},"gates":{}}' > "$TMP_WRONG"
python3 "$VALIDATOR" "$TMP_WRONG" > /dev/null 2>&1
rc=$?
if [ $rc -eq 1 ]; then pass "wrong schema version → rejected"; else fail "wrong schema version (got exit $rc)"; fi
rm -f "$TMP_WRONG"

# ── Test 4: healing fields valid ─────────────────────────────────────────
TMP_HEAL=$(mktemp)
cat > "$TMP_HEAL" << 'EOF'
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "project": "test",
  "checkpoints": {"CP0":"pending","CP1":"pending","CP2":"pending","CP3":"pending","CP4":"pending"},
  "gates": {"init":"pending","plan":"pending","exec":"pending","verify":"pending","complete":"pending"},
  "healing": {
    "enabled": true,
    "maxAttempts": 3,
    "currentAttempt": 1,
    "lastAttempt": null,
    "lastError": null,
    "retryHistory": [
      {"attempt":1,"timestamp":"2026-04-30T10:00:00Z","failedGates":["lint"],"errorSummary":"unused var","filesTouched":["a.js"],"status":"failed"}
    ],
    "autoHeal": true
  },
  "metrics": {"tasksCompleted":0,"tasksBlocked":0},
  "autonomy": {"level":4,"requireApprovalFor":[],"autoMergeOnCI":false}
}
EOF
python3 "$VALIDATOR" "$TMP_HEAL" > /dev/null 2>&1
rc=$?
if [ $rc -eq 0 ]; then pass "healing fields valid"; else fail "healing fields valid (got exit $rc)"; fi
rm -f "$TMP_HEAL"

# ── Test 5: extra gate keys allowed ──────────────────────────────────────
TMP_GATES=$(mktemp)
cat > "$TMP_GATES" << 'EOF'
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "project": "test",
  "checkpoints": {"CP0":"completed","CP1":"completed","CP2":"completed","CP3":"completed","CP4":"completed"},
  "gates": {"init":"passed","plan":"passed","exec":"passed","verify":"passed","complete":"passed","custom_gate":"passed"},
  "metrics": {"tasksCompleted":1,"tasksBlocked":0},
  "autonomy": {"level":4,"requireApprovalFor":[],"autoMergeOnCI":false}
}
EOF
python3 "$VALIDATOR" "$TMP_GATES" > /dev/null 2>&1
rc=$?
if [ $rc -eq 0 ]; then pass "extra gate keys allowed"; else fail "extra gate keys allowed (got exit $rc)"; fi
rm -f "$TMP_GATES"

# ── Test 6: autonomy.level out of range → must fail ─────────────────────
TMP_RANGE=$(mktemp)
cat > "$TMP_RANGE" << 'EOF'
{
  "_schema": "harness-state-v2",
  "version": "2.0.0",
  "project": "test",
  "checkpoints": {"CP0":"completed","CP1":"completed","CP2":"completed","CP3":"completed","CP4":"completed"},
  "gates": {"init":"passed","plan":"passed","exec":"passed","verify":"passed","complete":"passed"},
  "metrics": {"tasksCompleted":1,"tasksBlocked":0},
  "autonomy": {"level":99,"requireApprovalFor":[],"autoMergeOnCI":false}
}
EOF
python3 "$VALIDATOR" "$TMP_RANGE" > /dev/null 2>&1
rc=$?
if [ $rc -eq 1 ]; then pass "autonomy.level > 9 → rejected"; else fail "autonomy.level range check (got exit $rc)"; fi
rm -f "$TMP_RANGE"

# ── Test 7: nuwax state valid ─────────────────────────────────────────────
python3 "$VALIDATOR" "$ROOT/packages/nuwax-harness/harness/feedback/state/state.json" > /dev/null 2>&1
rc=$?
if [ $rc -eq 0 ]; then pass "nuwax-harness state valid"; else fail "nuwax-harness state valid (got exit $rc)"; fi

# ── Summary ───────────────────────────────────────────────────────────────
echo ""
echo "==================================="
echo "  Results: $PASS passed, $FAIL failed"
echo "==================================="
[ $FAIL -eq 0 ]
