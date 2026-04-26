#!/usr/bin/env node
/**
 * @harnesskit/generic-harness
 * Generic / universal harness — language and framework agnostic
 */
"use strict";

const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

function loadState(cwd) {
  const file = path.join(cwd || process.cwd(), "harness/feedback/state/state.json");
  if (!fs.existsSync(file)) return null;
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function saveState(cwd, state) {
  const file = path.join(cwd || process.cwd(), "harness/feedback/state/state.json");
  fs.writeFileSync(file, JSON.stringify(state, null, 2));
}

function initState(cwd, projectName) {
  const state = {
    _schema: "harness-state-v2",
    version: "2.0.0",
    project: projectName || path.basename(cwd) || "generic-project",
    type: "generic",
    platform: "universal",
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

// Auto-detect gates from project scripts (package.json) or constraints.md
function detectGates(cwd) {
  // Try constraints.md first
  const constraintsFile = path.join(cwd, "harness/base/constraints.md");
  if (fs.existsSync(constraintsFile)) {
    const content = fs.readFileSync(constraintsFile, "utf8");
    const found = [];
    const re = /Gate\s+(\d+):\s*(.+?)\s*(?:→|->)\s*(.+)/gi;
    let m;
    while ((m = re.exec(content)) !== null) {
      found.push({ name: m[3].trim().toLowerCase().replace(/\s+/g, "_"), cmd: m[2].trim(), desc: m[3].trim() });
    }
    if (found.length > 0) return found;
  }

  // Fall back to package.json scripts
  const pkgFile = path.join(cwd, "package.json");
  if (fs.existsSync(pkgFile)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgFile, "utf8"));
      const scripts = pkg.scripts || {};
      const scriptMap = {
        lint: ["npm run lint", "ESLint"],
        typecheck: ["npx tsc --noEmit", "TypeScript check"],
        test: ["npm test", "Tests"],
        build: ["npm run build", "Build"],
      };
      const gates = [];
      for (const [key, [cmd, desc]] of Object.entries(scriptMap)) {
        if (scripts[key]) gates.push({ name: key, cmd: cmd, desc: desc });
      }
      return gates.length > 0 ? gates : [{ name: "test", cmd: "npm test", desc: "Tests" }];
    } catch (_) {}
  }

  return [{ name: "test", cmd: "npm test", desc: "Tests" }];
}

function runGates(cwd) {
  const gates = detectGates(cwd);
  let allPassed = true;
  for (const gate of gates) {
    try {
      console.log("  Running: " + gate.desc);
      execSync(gate.cmd, { cwd, stdio: "inherit", timeout: 120000 });
      console.log("  ✅ " + gate.desc);
    } catch (e) {
      console.log("  ❌ " + gate.desc + " FAILED");
      allPassed = false;
    }
  }
  return allPassed;
}

// ── CP workflow ─────────────────────────────────────────────────────────────
function runCP0(cwd) {
  const state = loadState(cwd);
  if (!state) initState(cwd);
  const updated = loadState(cwd);
  updated.checkpoints.CP0 = "completed";
  updated.lastUpdated = new Date().toISOString();
  saveState(cwd, updated);
  console.log("[CP0] Generic harness initialized.");
  return updated;
}

function runCP1(cwd, task) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP1] No harness state. Run 'generic-harness init' first."); process.exit(1); }
  state.currentTask = task;
  state.taskStatus = "planning";
  state.checkpoints.CP1 = "in_progress";
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
  console.log("[CP1] Planning: " + task);
  // Auto-detect project type and gates
  const gates = detectGates(cwd);
  console.log("  Detected " + gates.length + " quality gates: " + gates.map(g => g.name).join(", "));
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
  const gatesOk = runGates(cwd);
  state.checkpoints.CP3 = gatesOk ? "completed" : "failed";
  state.taskStatus = gatesOk ? "completed" : "verify_failed";
  saveState(cwd, state);
  return gatesOk;
}

function runCP4(cwd) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP4] No harness state."); process.exit(1); }
  state.checkpoints.CP4 = "completed";
  state.taskStatus = "completed";
  state.metrics.tasksCompleted = (state.metrics.tasksCompleted || 0) + 1;
  state.lastUpdated = new Date().toISOString();
  if (state.currentTask) {
    state.taskHistory = state.taskHistory || [];
    state.taskHistory.push({ task: state.currentTask, completedAt: new Date().toISOString() });
    delete state.currentTask;
    delete state.taskStatus;
  }
  saveState(cwd, state);
  console.log("[CP4] ✅ Task completed!");
  return state;
}

// ── CLI ───────────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;
const cwd = process.cwd();

if (!cmd) {
  console.log("@harnesskit/generic-harness - Generic / universal harness\n");
  console.log("Commands:");
  console.log("  init              Initialize generic harness");
  console.log("  state             Show current state");
  console.log("  verify            Run auto-detected quality gates");
  console.log("  run <task>        Run full CP0→CP4 workflow");
  process.exit(0);
}

switch (cmd) {
  case "init":
    initState(cwd);
    console.log("✅ Generic harness initialized in " + cwd);
    break;
  case "state": {
    const s = loadState(cwd);
    if (!s) { console.log("No harness state."); process.exit(1); }
    console.log("\nGeneric Harness State — " + s.project);
    console.log("CP0:" + s.checkpoints.CP0 + " CP1:" + s.checkpoints.CP1 + " CP2:" + s.checkpoints.CP2 + " CP3:" + s.checkpoints.CP3 + " CP4:" + s.checkpoints.CP4);
    console.log("Tasks: " + s.metrics.tasksCompleted + " completed, " + s.metrics.tasksBlocked + " blocked");
    console.log("Autonomy: L" + (s.autonomy?.level || 4) + "\n");
    break;
  }
  case "verify":
    if (!runGates(cwd)) { console.log("\n❌ Gates failed."); process.exit(1); }
    console.log("\n🎉 All gates passed!");
    break;
  case "run": {
    const task = args.join(" ");
    if (!task) { console.error("Usage: generic-harness run <task>"); process.exit(1); }
    runCP0(cwd);
    runCP1(cwd, task);
    const approved = args.includes("--approve") || args.includes("-y");
    if (!approved) {
      console.log("\n⚠️  Task: " + task + " — CP1 planning complete. Re-run with --approve.");
      process.exit(0);
    }
    if (!runCP3(cwd)) { console.log("\n❌ Gates failed at CP3."); process.exit(1); }
    runCP4(cwd);
    console.log("\n🎉 Task '" + task + "' completed!");
    break;
  }
  default:
    console.error("Unknown command: " + cmd);
    console.error("Usage: generic-harness <init|state|verify|run>");
    process.exit(1);
}