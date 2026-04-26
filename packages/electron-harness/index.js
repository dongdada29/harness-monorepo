#!/usr/bin/env node
/**
 * @harnesskit/electron-harness
 * Electron + Ant Design harness for AI coding agents
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
    project: projectName || "electron-project",
    type: "tech",
    platform: "electron",
    lastUpdated: new Date().toISOString(),
    checkpoints: { CP0: "pending", CP1: "pending", CP2: "pending", CP3: "pending", CP4: "pending" },
    gates: { init: "pending", plan: "pending", exec: "pending", verify: "pending", complete: "pending" },
    metrics: { tasksCompleted: 0, tasksBlocked: 0 },
    autonomy: { level: 4, requireApprovalFor: [], autoMergeOnCI: false },
    tech: { framework: "electron", ui: "antd", builder: "electron-builder" },
    recentChanges: [],
    taskHistory: [],
  };
  saveState(cwd, state);
  return state;
}

// Electron-specific gates: lint → typecheck → test → build → package
function runGates(cwd) {
  const ELECTRON_GATES = [
    { name: "lint", cmd: "npm run lint", desc: "ESLint" },
    { name: "typecheck", cmd: "npx tsc --noEmit", desc: "TypeScript check" },
    { name: "test", cmd: "npm test", desc: "Tests" },
    { name: "build", cmd: "npm run build", desc: "Build" },
    { name: "package", cmd: "npm run package", desc: "Package (.exe/.dmg)" },
  ];

  let allPassed = true;
  for (const gate of ELECTRON_GATES) {
    try {
      console.log("  Running: " + gate.desc);
      execSync(gate.cmd, { cwd, stdio: "inherit", timeout: 300000 });
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
  console.log("[CP0] Electron harness initialized. Framework: " + (updated.tech?.framework || "electron"));
  return updated;
}

function runCP1(cwd, task) {
  const state = loadState(cwd);
  if (!state) { console.error("[CP1] No harness state. Run 'electron-harness init' first."); process.exit(1); }
  state.currentTask = task;
  state.taskStatus = "planning";
  state.checkpoints.CP1 = "in_progress";
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
  console.log("[CP1] Planning: " + task);
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
  console.log("[CP2] Executing (Electron + Ant Design workflow)...");
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
  console.log("[CP3] Running Electron quality gates...");
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
  console.log("@harnesskit/electron-harness - Electron + Ant Design harness\n");
  console.log("Commands:");
  console.log("  init              Initialize Electron harness");
  console.log("  state             Show current state");
  console.log("  verify            Run Electron-specific quality gates");
  console.log("  run <task>        Run full CP0→CP4 workflow");
  process.exit(0);
}

switch (cmd) {
  case "init":
    initState(cwd);
    console.log("✅ Electron harness initialized in " + cwd);
    break;
  case "state": {
    const s = loadState(cwd);
    if (!s) { console.log("No harness state."); process.exit(1); }
    console.log("\nElectron Harness State — " + s.project);
    console.log("CP0:" + s.checkpoints.CP0 + " CP1:" + s.checkpoints.CP1 + " CP2:" + s.checkpoints.CP2 + " CP3:" + s.checkpoints.CP3 + " CP4:" + s.checkpoints.CP4);
    console.log("Framework: " + (s.tech?.framework || "electron") + " | UI: " + (s.tech?.ui || "antd"));
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
    if (!task) { console.error("Usage: electron-harness run <task>"); process.exit(1); }
    runCP0(cwd);
    runCP1(cwd, task);
    const approved = args.includes("--approve") || args.includes("-y");
    if (!approved) {
      console.log("\n⚠️  Task: " + task + " — CP1 planning complete. Re-run with --approve.");
      process.exit(0);
    }
    if (!runCP3(cwd)) { console.log("\n❌ Gates failed at CP3."); process.exit(1); }
    runCP4(cwd);
    console.log("\n🎉 Task '" + task + "' completed on Electron!");
    break;
  }
  default:
    console.error("Unknown command: " + cmd);
    console.error("Usage: electron-harness <init|state|verify|run>");
    process.exit(1);
}