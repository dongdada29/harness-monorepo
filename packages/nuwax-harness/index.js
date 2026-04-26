#!/usr/bin/env node
/**
 * @harnesskit/nuwax-harness
 * Nuwax Agent OS — tailored harness for Nuwax project workflow
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

function initState(cwd, projectName) {
  const state = {
    _schema: "harness-state-v2",
    version: "2.0.0",
    project: projectName || "nuwax-project",
    type: "business",
    platform: "nuwax",
    lastUpdated: new Date().toISOString(),
    checkpoints: { CP0: "pending", CP1: "pending", CP2: "pending", CP3: "pending", CP4: "pending" },
    gates: { init: "pending", plan: "pending", exec: "pending", verify: "pending", complete: "pending" },
    metrics: { tasksCompleted: 0, tasksBlocked: 0, mcpToolsInvoked: 0 },
    autonomy: { level: 4, requireApprovalFor: [], autoMergeOnCI: false },
    recentChanges: [],
    taskHistory: [],
    mcp: { tools: [], lastInvoked: null },
  };
  saveState(cwd, state);
  return state;
}

// ── Nuwax-specific gates ────────────────────────────────────────────────────
// For Nuwax: pnpm typecheck → pnpm build → electron-builder
function runGates(cwd) {
  const NUWAX_GATES = [
    { name: "typecheck", cmd: "cd " + cwd + " && pnpm typecheck", desc: "TypeScript check" },
    { name: "build", cmd: "cd " + cwd + " && pnpm build", desc: "Rust + Electron build" },
    { name: "package", cmd: "cd " + cwd + " && pnpm package", desc: "Package (.dmg/.exe)" },
  ];

  let allPassed = true;
  for (const gate of NUWAX_GATES) {
    try {
      console.log("  Running: " + gate.desc);
      execSync(gate.cmd, { stdio: "inherit", timeout: 300000 });
      console.log("  ✅ " + gate.desc);
    } catch (e) {
      console.log("  ❌ " + gate.desc + " FAILED");
      allPassed = false;
    }
  }
  return allPassed;
}

// ── MCP integration helpers ────────────────────────────────────────────────
function trackMCPUsage(cwd, toolName) {
  const state = loadState(cwd);
  if (!state) return;
  state.mcp = state.mcp || {};
  state.mcp.tools = state.mcp.tools || [];
  state.mcp.lastInvoked = new Date().toISOString();
  state.metrics = state.metrics || {};
  state.metrics.mcpToolsInvoked = (state.metrics.mcpToolsInvoked || 0) + 1;
  if (!state.mcp.tools.includes(toolName)) state.mcp.tools.push(toolName);
  state.lastUpdated = new Date().toISOString();
  saveState(cwd, state);
}

// ── CP Workflow ─────────────────────────────────────────────────────────────
function runCP0(cwd) {
  const state = loadState(cwd);
  if (!state) initState(cwd);
  const updated = loadState(cwd);
  updated.checkpoints.CP0 = "completed";
  updated.lastUpdated = new Date().toISOString();
  saveState(cwd, updated);
  console.log("[CP0] Nuwax harness initialized.");
  console.log("[CP0] Platform: nuwax | Autonomy: L" + updated.autonomy.level);
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
  console.log("[CP1] Planning: " + task);
  // Check for MCP tools usage
  const nuwaxModules = path.join(HARNESS_DIR, "projects/nuwax/modules.md");
  if (fs.existsSync(nuwaxModules)) {
    console.log("  [INFO] Loading Nuwax module constraints...");
  }
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
  console.log("[CP2] Executing (Rust + Electron workflow)...");
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
  console.log("[CP3] Running Nuwax quality gates...");
  const gatesOk = runGates(cwd);
  if (!gatesOk) {
    state.checkpoints.CP3 = "failed";
    state.taskStatus = "verify_failed";
    saveState(cwd, state);
    console.log("[CP3] ❌ Gates failed.");
    return state;
  }
  console.log("[CP3] ✅ All gates passed.");
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

// ── CLI entry ────────────────────────────────────────────────────────────────
const [,, cmd, ...args] = process.argv;
const cwd = process.cwd();

if (!cmd) {
  console.log("@harnesskit/nuwax-harness - Nuwax Agent OS harness\n");
  console.log("Commands:");
  console.log("  init              Initialize Nuwax harness");
  console.log("  state             Show current state");
  console.log("  verify            Run Nuwax-specific quality gates");
  console.log("  run <task>        Run full CP0→CP4 workflow");
  console.log("  mcp <tool>        Track MCP tool usage");
  process.exit(0);
}

switch (cmd) {
  case "init": {
    initState(cwd);
    console.log("✅ Nuwax harness initialized in " + cwd);
    break;
  }
  case "state": {
    const s = loadState(cwd);
    if (!s) { console.log("No harness state. Run 'nuwax-harness init' first."); process.exit(1); }
    console.log("\nNuwax Harness State — " + s.project);
    console.log("CP0:" + s.checkpoints.CP0 + " CP1:" + s.checkpoints.CP1 + " CP2:" + s.checkpoints.CP2 + " CP3:" + s.checkpoints.CP3 + " CP4:" + s.checkpoints.CP4);
    console.log("Tasks: " + s.metrics.tasksCompleted + " completed, " + s.metrics.tasksBlocked + " blocked");
    console.log("MCP Tools invoked: " + (s.metrics.mcpToolsInvoked || 0));
    console.log("Autonomy: L" + (s.autonomy?.level || 4) + "\n");
    break;
  }
  case "verify": {
    if (!runGates(cwd)) { console.log("\n❌ Gates failed."); process.exit(1); }
    console.log("\n🎉 All gates passed!");
    break;
  }
  case "run": {
    const task = args.join(" ");
    if (!task) { console.error("Usage: nuwax-harness run <task>"); process.exit(1); }
    runCP0(cwd);
    runCP1(cwd, task);
    const approved = args.includes("--approve") || args.includes("-y");
    if (!approved) {
      console.log("\n⚠️  Task: " + task + " — CP1 planning complete.");
      console.log("Re-run with --approve to continue.");
      process.exit(0);
    }
    runCP2(cwd);
    runCP3(cwd);
    runCP4(cwd);
    console.log("\n🎉 Task '" + task + "' completed on Nuwax platform!");
    break;
  }
  case "mcp": {
    const toolName = args[0];
    if (!toolName) { console.error("Usage: nuwax-harness mcp <tool-name>"); process.exit(1); }
    trackMCPUsage(cwd, toolName);
    console.log("✅ MCP tool tracked: " + toolName);
    break;
  }
  default:
    console.error("Unknown command: " + cmd);
    console.error("Usage: nuwax-harness <init|state|verify|run|mcp>");
    process.exit(1);
}