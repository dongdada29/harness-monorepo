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
function runGates(cwd) {
  const constraintsFile = path.join(cwd, "harness/base/constraints.md");
  const DEFAULT_GATES = [
    { name: "lint", cmd: "npm run lint", desc: "ESLint" },
    { name: "typecheck", cmd: "npx tsc --noEmit", desc: "TypeScript check" },
    { name: "test", cmd: "npm test", desc: "Tests" },
    { name: "build", cmd: "npm run build", desc: "Build" },
  ];

  let gates = DEFAULT_GATES;
  if (fs.existsSync(constraintsFile)) {
    const content = fs.readFileSync(constraintsFile, "utf8");
    const found = [];
    const re = /Gate\s+(\d+):\s*(.+?)\s*(?:→|->)\s*(.+)/gi;
    let m;
    while ((m = re.exec(content)) !== null) {
      found.push({ name: m[3].trim().toLowerCase().replace(/\s+/g, "_"), cmd: m[2].trim(), desc: m[3].trim() });
    }
    if (found.length > 0) gates = found;
  }

  let allPassed = true;
  for (const gate of gates) {
    try {
      execSync(gate.cmd, { cwd, stdio: "ignore", timeout: 120000 });
      console.log("  ✅ " + gate.desc);
    } catch (e) {
      console.log("  ❌ " + gate.desc + " FAILED");
      allPassed = false;
    }
  }
  return allPassed;
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
    if (!runGates(cwd)) { console.log("\n❌ Gates failed."); process.exit(1); }
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
    const gatesOk = runGates(cwd);
    if (!gatesOk) { console.log("\n❌ Gates failed at CP3."); process.exit(1); }
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
  default:
    console.error("Unknown command: " + cmd);
    console.error("Usage: agent-harness <init|state|verify|run|checkpoint>");
    process.exit(1);
}