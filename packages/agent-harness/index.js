#!/usr/bin/env node
/**
 * @harnesskit/agent-harness
 * Control theory engineering workflow for Claude Code / Cursor / Codex / OpenCode
 */
"use strict";

const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

// ── Paths ────────────────────────────────────────────────────────────────────
const HARNESS_DIR = path.join(__dirname, "harness");
const BASE_DIR = path.join(HARNESS_DIR, "base");
const FEEDBACK_DIR = path.join(HARNESS_DIR, "feedback");
const STATE_FILE = path.join(FEEDBACK_DIR, "state/state.json");

// ── Schema ──────────────────────────────────────────────────────────────────
const REQUIRED_CHECKPOINTS = ["CP0", "CP1", "CP2", "CP3", "CP4"];
const REQUIRED_GATES = ["init", "plan", "exec", "verify", "complete"];

// ── State helpers ───────────────────────────────────────────────────────────
function loadState(cwd) {
  const file = path.join(cwd || process.cwd(), "harness/feedback/state/state.json");
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function saveState(cwd, state) {
  const file = path.join(cwd || process.cwd(), "harness/feedback/state/state.json");
  fs.writeFileSync(file, JSON.stringify(state, null, 2));
}

function initState(cwd, projectName, type, platform) {
  const state = {
    _schema: "harness-state-v2",
    version: "2.0.0",
    project: projectName || path.basename(cwd),
    type: type || "generic",
    platform: platform || "agent-desktop",
    lastUpdated: new Date().toISOString(),
    checkpoints: { CP0: "pending", CP1: "pending", CP2: "pending", CP3: "pending", CP4: "pending" },
    gates: { init: "pending", plan: "pending", exec: "pending", verify: "pending", complete: "pending" },
    metrics: { tasksCompleted: 0, tasksBlocked: 0 },
    autonomy: { level: 4, requireApprovalFor: [], autoMergeOnCI: false },
    recentChanges: [],
    taskHistory: [],
  };
  fs.mkdirSync(path.join(cwd, "harness/feedback/state"), { recursive: true });
  saveState(cwd, state);
  return state;
}

// ── CP Workflow ─────────────────────────────────────────────────────────────
function runCP0(cwd) {
  const state = loadState(cwd);
  if (!state) initState(cwd);
  const updated = loadState(cwd);
  updated.checkpoints.CP0 = "completed";
  updated.lastUpdated = new Date().toISOString();
  saveState(cwd, updated);
  console.log("[CP0] Harness initialized. State loaded.");
  return updated;
}

function runCP1(cwd, task) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP1] No harness state. Run 'harness init' first."); process.exit(1); }
  state.currentTask = task;
  state.taskStatus = "planning";
  state.checkpoints.CP1 = "in_progress";
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
  console.log("[CP1] Planning task: " + task);
  return state;
}

function runCP2(cwd) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP2] No harness state."); process.exit(1); }
  state.checkpoints.CP1 = "completed";
  state.checkpoints.CP2 = "in_progress";
  state.taskStatus = "executing";
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
  console.log("[CP2] Executing...");
  return state;
}

function runCP3(cwd) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP3] No harness state."); process.exit(1); }
  state.checkpoints.CP2 = "completed";
  state.checkpoints.CP3 = "in_progress";
  state.taskStatus = "verifying";
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
  console.log("[CP3] Running quality gates...");
  return state;
}

function runCP4(cwd) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP4] No harness state."); process.exit(1); }
  state.checkpoints.CP3 = "completed";
  state.checkpoints.CP4 = "completed";
  state.taskStatus = "completed";
  state.metrics.tasksCompleted = (state.metrics.tasksCompleted || 0) + 1;
  state.lastUpdated = new Date().toISOString();
  // Archive completed task
  if (state.currentTask) {
    state.taskHistory = state.taskHistory || [];
    state.taskHistory.push({ task: state.currentTask, completedAt: new Date().toISOString() });
    delete state.currentTask;
    delete state.taskStatus;
  }
  saveState(cwd, state);
  console.log("[CP4] Task completed!");
  return state;
}

// ── Gate runner ─────────────────────────────────────────────────────────────
function parseGates(cwd) {
  const constraintsFile = path.join(cwd, "harness/base/constraints.md");
  const DEFAULT_GATES = [
    { name: "lint", cmd: "npm run lint", desc: "ESLint" },
    { name: "typecheck", cmd: "npx tsc --noEmit", desc: "TypeScript check" },
    { name: "test", cmd: "npm test", desc: "Tests" },
    { name: "build", cmd: "npm run build", desc: "Build" },
  ];
  if (!fs.existsSync(constraintsFile)) return DEFAULT_GATES;
  const content = fs.readFileSync(constraintsFile, "utf8");
  const found = [];
  const re = /Gate\s+(\d+):\s*(.+?)\s*(?:→|->)\s*(.+)/gi;
  let m;
  while ((m = re.exec(content)) !== null) {
    found.push({ name: m[3].trim().toLowerCase().replace(/\s+/g, "_"), cmd: m[2].trim(), desc: m[3].trim() });
  }
  return found.length > 0 ? found : DEFAULT_GATES;
}

// Returns { passed: string[], failed: { name, desc, error }[], allPassed: boolean }
function runGates(cwd, gateList) {
  const gates = gateList || parseGates(cwd);
  const passed = [];
  const failed = [];
  for (const gate of gates) {
    try {
      execSync(gate.cmd, { cwd, stdio: "pipe", timeout: 120000 });
      console.log("  ✅ " + gate.desc);
      passed.push(gate.name);
    } catch (e) {
      const err = e.stdout?.toString() || e.stderr?.toString() || "";
      console.log("  ❌ " + gate.desc + " FAILED");
      failed.push({ name: gate.name, desc: gate.desc, error: err });
    }
  }
  return { passed, failed, allPassed: failed.length === 0 };
}

// ── Healing helpers ─────────────────────────────────────────────────────────
function initHealingState(cwd) {
  const state = loadState(cwd) || {};
  state.healing = {
    enabled: true,
    maxAttempts: 3,
    currentAttempt: 0,
    lastAttempt: null,
    lastError: null,
    retryHistory: [],
    autoHeal: true,
  };
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
  return state;
}

function recordHealingAttempt(cwd, attemptNum, failedGates, errorSummary, filesTouched, status) {
  const state = loadState(cwd);
  if (!state) return;
  state.healing = state.healing || {};
  state.healing.currentAttempt = attemptNum;
  state.healing.lastAttempt = new Date().toISOString();
  state.healing.lastError = errorSummary;
  state.healing.retryHistory = state.healing.retryHistory || [];
  state.healing.retryHistory.push({
    attempt: attemptNum,
    timestamp: new Date().toISOString(),
    failedGates,
    errorSummary,
    filesTouched: filesTouched || [],
    status,
  });
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
}

function getHealingConfig(cwd) {
  const state = loadState(cwd);
  if (!state) return { enabled: false, maxAttempts: 3, autoHeal: true };
  return {
    enabled: state.healing?.enabled !== false,
    maxAttempts: state.healing?.maxAttempts || 3,
    currentAttempt: state.healing?.currentAttempt || 0,
    autoHeal: state.healing?.autoHeal !== false,
    autonomyLevel: state.autonomy?.level || 4,
  };
}

/**
 * Run CP4 self-healing loop.
 * Returns: { success: boolean, attempts: number, reason?: string }
 */
function runHealingLoop(cwd, opts) {
  const cfg = getHealingConfig(cwd);
  if (!cfg.enabled) {
    console.log("\n⚠️  Healing is disabled. Enable with: agent-harness healing on");
    return { success: false, attempts: 0, reason: "healing_disabled" };
  }
  if (cfg.autonomyLevel < 3) {
    console.log("\n⚠️  Autonomy level L" + cfg.autonomyLevel + " — healing requires L3+");
    return { success: false, attempts: 0, reason: "autonomy_too_low" };
  }

  const max = opts?.maxAttempts || cfg.maxAttempts;
  const dryRun = opts?.dryRun || false;
  const force = opts?.force || false;
  const gates = parseGates(cwd);

  console.log("\n" + "=".repeat(50));
  console.log("🔄 CP4 Self-Healing Loop");
  console.log("=".repeat(50));
  console.log("  Max attempts: " + max);
  console.log("  Dry run:      " + (dryRun ? "yes" : "no"));
  console.log("  Force:        " + (force ? "yes" : "no"));
  console.log("");

  for (let attempt = (cfg.currentAttempt || 0) + 1; attempt <= max; attempt++) {
    console.log("\n── Attempt " + attempt + "/" + max + " ──");

    const result = runGates(cwd, gates);

    if (result.allPassed) {
      recordHealingAttempt(cwd, attempt, [], "All gates passed", [], "passed");
      console.log("\n🎉 All gates passed after " + attempt + " attempt(s)!");
      const s = loadState(cwd);
      s.gates.verify = "passed";
      s.lastUpdated = new Date().toISOString();
      saveState(cwd, s);
      return { success: true, attempts: attempt };
    }

    const failedNames = result.failed.map(f => f.name);
    const errorSummary = result.failed.map(f => f.desc + ": " + (f.error.split("\n")[0] || "unknown").slice(0, 100)).join(" | ");

    console.log("\n❌ Gates failed: " + failedNames.join(", "));
    console.log("   Error: " + errorSummary.slice(0, 120));

    if (dryRun) {
      console.log("\n[dry-run] Would attempt repair here.");
      recordHealingAttempt(cwd, attempt, failedNames, errorSummary, [], "failed");
      continue;
    }

    recordHealingAttempt(cwd, attempt, failedNames, errorSummary, [], "failed");

    if (!force && attempt >= max) {
      console.log("\n❌ Max attempts (" + max + ") reached. Requesting human intervention.");
      return { success: false, attempts: attempt, reason: "max_attempts" };
    }

    console.log("\n🔧 Analyzing and attempting repair...");
    console.log("   (Self-heal: Agent should now fix errors, then re-run 'agent-harness heal')");
    for (const f of result.failed) {
      console.log("     - Fix " + f.desc + " (" + f.name + ")");
      console.log("       Error: " + (f.error.split("\n")[0] || "").slice(0, 80));
    }
  }

  return { success: false, attempts: max, reason: "max_attempts" };
}

// ── CLI entry ────────────────────────────────────────────────────────────────
// Usage: node index.js <command> [args]
const [,, cmd, ...args] = process.argv;
const cwd = process.cwd();

if (!cmd) {
  console.log("@harnesskit/agent-harness - Control theory engineering workflow\n");
  console.log("Commands:");
  console.log("  run <task>        Run full CP0→CP4 workflow for a task");
  console.log("  verify            Run quality gates");
  console.log("  heal              Run CP4 self-healing loop");
  console.log("  healing <on|off>  Enable/disable self-healing");
  console.log("  state             Show current state");
  console.log("  init              Initialize harness in current project");
  console.log("  checkpoint <name> Set checkpoint (CP0-CP4)");
  process.exit(0);
}

switch (cmd) {
  case "init": {
    initState(cwd);
    console.log("✅ Harness initialized in " + cwd);
    break;
  }
  case "state": {
    const s = loadState(cwd);
    if (!s) { console.log("No harness state. Run 'harness init' first."); process.exit(1); }
    console.log("\nHarness State — " + s.project);
    console.log("CP0:" + s.checkpoints.CP0 + " CP1:" + s.checkpoints.CP1 + " CP2:" + s.checkpoints.CP2 + " CP3:" + s.checkpoints.CP3 + " CP4:" + s.checkpoints.CP4);
    console.log("Gate — init:" + s.gates.init + " plan:" + s.gates.plan + " exec:" + s.gates.exec + " verify:" + s.gates.verify + " complete:" + s.gates.complete);
    console.log("Autonomy: L" + (s.autonomy?.level || 4));
    console.log("Tasks: " + s.metrics.tasksCompleted + " completed, " + s.metrics.tasksBlocked + " blocked\n");
    break;
  }
  case "verify": {
    const gates = parseGates(cwd);
    const result = runGates(cwd, gates);
    const state = loadState(cwd);
    if (state) {
      for (const p of result.passed) state.gates[p] = "passed";
      for (const f of result.failed) state.gates[f.name] = "failed";
      state.gates.verify = result.allPassed ? "passed" : "failed";
      state.lastUpdated = new Date().toISOString();
      saveState(cwd, state);
    }
    if (!result.allPassed) { console.log("\n❌ Gates failed."); process.exit(1); }
    console.log("\n🎉 All gates passed!");
    break;
  }
  case "run": {
    const task = args.join(" ");
    if (!task) { console.error("Usage: agent-harness run <task>"); process.exit(1); }
    runCP0(cwd);
    runCP1(cwd, task);
    const approved = args.includes("--approve") || args.includes("-y");
    if (!approved) {
      console.log("\n⚠️  Task: " + task);
      console.log("CP1 planning complete. To continue, re-run with --approve flag.");
      process.exit(0);
    }
    runCP2(cwd);
    const gatesResult = runGates(cwd);
    if (!gatesResult.allPassed) { console.log("\n❌ Gates failed at CP3. Run 'agent-harness heal' to auto-repair."); process.exit(1); }
    runCP3(cwd);
    runCP4(cwd);
    console.log("\n🎉 Task '" + task + "' completed successfully!");
    break;
  }
  case "checkpoint": {
    const cp = args[0];
    if (!REQUIRED_CHECKPOINTS.includes(cp)) { console.error("Invalid checkpoint. Use: " + REQUIRED_CHECKPOINTS.join(", ")); process.exit(1); }
    const s = loadState(cwd);
    if (!s) { console.error("No harness state."); process.exit(1); }
    s.checkpoints[cp] = args[1] || "completed";
    s.lastUpdated = new Date().toISOString();
    saveState(cwd, s);
    console.log("Checkpoint " + cp + " → " + s.checkpoints[cp]);
    break;
  }
  case "heal": {
    const cfg = getHealingConfig(cwd);
    const healState = loadState(cwd);
    const verifyStatus = healState?.gates?.verify;
    if (verifyStatus !== "failed" && verifyStatus !== "pending") {
      console.log("\n⚠️  No failed gates to heal. Run 'agent-harness verify' first.");
      process.exit(3);
    }
    const opts = {
      maxAttempts: parseInt(args.find(a => /^\d+$/.test(a))) || undefined,
      dryRun: args.includes("--dry-run"),
      force: args.includes("--force"),
    };
    const result = runHealingLoop(cwd, opts);
    if (result.success) process.exit(0);
    else if (result.reason === "healing_disabled") process.exit(2);
    else process.exit(1);
  }
  case "healing": {
    const action = args[0];
    if (!action || !["on", "off", "status"].includes(action)) {
      console.error("Usage: agent-harness healing <on|off|status>"); process.exit(1);
    }
    const state = loadState(cwd) || {};
    state.healing = state.healing || { enabled: true, maxAttempts: 3, autoHeal: true };
    if (action === "status") {
      console.log("\n🔧 Healing Status — " + (state.project || cwd));
      console.log("  Enabled:     " + (state.healing.enabled ? "yes" : "no"));
      console.log("  Max attempts: " + state.healing.maxAttempts);
      console.log("  Current:     " + (state.healing.currentAttempt || 0));
      console.log("  Auto-heal:   " + (state.healing.autoHeal ? "yes" : "no"));
      if (state.healing.retryHistory?.length > 0) {
        console.log("  History:     " + state.healing.retryHistory.length + " attempt(s)");
        for (const h of state.healing.retryHistory.slice(-3)) {
          console.log("    [Attempt " + h.attempt + "] " + h.status + ": " + h.failedGates.join(", ") + " — " + (h.errorSummary || "").slice(0, 60));
        }
      }
      console.log("");
      break;
    }
    if (action === "on") { state.healing.enabled = true; state.healing.autoHeal = true; }
    if (action === "off") { state.healing.enabled = false; state.healing.autoHeal = false; }
    state.lastUpdated = new Date().toISOString();
    saveState(cwd, state);
    console.log("Healing " + (action === "on" ? "enabled" : "disabled"));
    break;
  }
  default:
    console.error("Unknown command: " + cmd);
    console.error("Usage: agent-harness <init|state|verify|run|checkpoint|heal|healing>");
    process.exit(1);
}