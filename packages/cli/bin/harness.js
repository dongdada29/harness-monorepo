#!/usr/bin/env node
/**
 * @harnesskit/cli
 * One command to add AI agent engineering workflow to any project
 */
"use strict";

const { Command } = require("commander");
const chalk = require("chalk");
const path = require("path");
const fs = require("fs");
const { execSync } = require("child_process");

// ── Paths ────────────────────────────────────────────────────────────────────
const ROOT = path.resolve(__dirname, "../../..");
const PKG_ROOT = path.resolve(__dirname, "..");

// ── Log helpers ─────────────────────────────────────────────────────────────
const log = {
  info: (msg) => console.log(chalk.blue("  [INFO]"), msg),
  ok: (msg) => console.log(chalk.green("  [OK]  "), msg),
  warn: (msg) => console.log(chalk.yellow("  [WARN]"), msg),
  err: (msg) => console.error(chalk.red("  [ERR] "), msg),
};

// ── Utils ────────────────────────────────────────────────────────────────────
function exists(f) {
  try {
    fs.accessSync(path.join(PKG_ROOT, f));
    return true;
  } catch {
    return false;
  }
}

function copyDir(src, dst) {
  const cmd = `cp -r "${src}" "${dst}"`;
  try {
    execSync(cmd, { stdio: "pipe" });
    return true;
  } catch (e) {
    return false;
  }
}

function detectProjectType(dir) {
  const pkgFile = path.join(dir, "package.json");
  if (exists(pkgFile)) {
    try {
      const pkg = JSON.parse(fs.readFileSync(pkgFile, "utf8"));
      if (pkg.name && pkg.name.includes("nuwax")) return "nuwax";
      if (pkg.dependencies?.electron || pkg.devDependencies?.electron) return "electron";
    } catch (_) {}
  }
  return "generic";
}

function writeState(projectDir, state) {
  const stateFile = path.join(projectDir, "harness/feedback/state/state.json");
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
}

// Run a command, return { ok, stdout, stderr, time }
function runCmd(cmd, cwd) {
  const start = Date.now();
  try {
    const out = execSync(cmd, {
      cwd,
      stdio: ["ignore", "pipe", "pipe"],
      timeout: 120_000,
    });
    return { ok: true, stdout: out.toString(), stderr: "", time: Date.now() - start };
  } catch (e) {
    return { ok: false, stdout: e.stdout?.toString() || "", stderr: e.stderr?.toString() || "", time: Date.now() - start };
  }
}

// Parse gates from constraints.md (looks for "Gate N: <cmd> → <desc>")
function parseGates(constraintsPath) {
  const DEFAULT_GATES = [
    { name: "lint", cmd: "npm run lint", desc: "ESLint" },
    { name: "typecheck", cmd: "npx tsc --noEmit", desc: "TypeScript check" },
    { name: "test", cmd: "npm test", desc: "Tests" },
    { name: "build", cmd: "npm run build", desc: "Build" },
  ];
  if (!fs.existsSync(constraintsPath)) return DEFAULT_GATES;
  const content = fs.readFileSync(constraintsPath, "utf8");
  const gates = [];
  const re = /Gate\s+(\d+):\s*(.+?)\s*(?:→|->)\s*(.+)/gi;
  let m;
  while ((m = re.exec(content)) !== null) {
    gates.push({
      name: m[3].trim().toLowerCase().replace(/\s+/g, "_"),
      cmd: m[2].trim(),
      desc: m[3].trim(),
    });
  }
  return gates.length > 0 ? gates : DEFAULT_GATES;
}

// ── Commands ────────────────────────────────────────────────────────────────

// harness init [type] [target-dir] [--template package|basic|advanced]
function initCommand(type, targetDir, opts) {
  const target = path.resolve(targetDir || process.cwd());
  const HarnessType = type || detectProjectType(target);
  const template = opts?.template || "package";

  const pkgMap = {
    nuwax: "@harnesskit/nuwax-harness",
    electron: "@harnesskit/electron-harness",
    agent: "@harnesskit/agent-harness",
    generic: "@harnesskit/generic-harness",
  };

  const pkgName = pkgMap[HarnessType] || pkgMap.generic;
  log.info("Initializing harness in: " + target);
  log.info("Type: " + HarnessType + " (" + pkgName + ")");

  // Create harness dir
  const harnessDir = path.join(target, "harness");
  fs.mkdirSync(harnessDir, { recursive: true });
  fs.mkdirSync(path.join(harnessDir, "feedback/state"), { recursive: true });

  if (template === "package") {
    // Use package overlays
    const srcHarness = path.join(PKG_ROOT, "../", pkgName.replace("@harnesskit/", "") + "/harness");
    const srcBase = path.join(PKG_ROOT, "../agent-harness/harness/base");
    try {
      if (fs.existsSync(srcBase)) {
        copyDir(srcBase, path.join(harnessDir, "base"));
        log.ok("Base harness installed");
      }
    } catch (e) { log.warn("Base files not found — continuing"); }
    try {
      if (fs.existsSync(srcHarness)) {
        copyDir(srcHarness + "/.", harnessDir);
        log.ok("Type overlay installed");
      }
    } catch (e) { log.warn("Overlay not found — continuing"); }
  } else {
    // Use templates dir
    const templateDir = path.join(ROOT, "templates", template);
    if (!fs.existsSync(templateDir)) {
      log.err("Template '" + template + "' not found. Available: basic, advanced");
      process.exit(1);
    }
    copyDir(templateDir + "/.", harnessDir);
    log.ok("Template '" + template + "' installed");
  }

  // Write state.json (always v2)
  const stateFile = path.join(harnessDir, "feedback/state/state.json");
  const state = {
    _schema: "harness-state-v2",
    version: "2.0.0",
    project: path.basename(target),
    type: HarnessType === "generic" ? "generic" : HarnessType === "electron" ? "tech" : "business",
    platform: HarnessType === "nuwax" ? "nuwax" : HarnessType === "electron" ? "electron" : "agent-desktop",
    lastUpdated: new Date().toISOString(),
    checkpoints: { CP0: "pending", CP1: "pending", CP2: "pending", CP3: "pending", CP4: "pending" },
    gates: { init: "pending", plan: "pending", exec: "pending", verify: "pending", complete: "pending" },
    metrics: { tasksCompleted: 0, tasksBlocked: 0 },
    autonomy: { level: 4, requireApprovalFor: [], autoMergeOnCI: false },
  };
  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
  log.ok("State initialized: " + stateFile);

  console.log(chalk.green("\n✅ Harness initialized successfully!"));
  console.log(chalk.gray("  Template: " + template + "  |  Type: " + HarnessType));
  console.log(chalk.gray("  Next: harness state start <task>  to begin a task\n"));
}

// harness state <cmd> [args]
function stateCommand(cmd, args) {
  const projectDir = process.cwd();
  const stateFile = path.join(projectDir, "harness/feedback/state/state.json");
  if (!fs.existsSync(stateFile)) {
    log.err("No harness found. Run: harness init");
    process.exit(1);
  }
  const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));

  switch (cmd) {
    case "show": {
      const gates = state.gates || {};
      const heal = state.healing || {};
      const cp = state.checkpoints || {};
      const failedGates = Object.keys(gates).filter(k => gates[k] === "failed");
      console.log("\n" + chalk.bold("Harness State") + " — " + state.project);
      console.log("CP0: " + cp.CP0 + "  CP1: " + cp.CP1 + "  CP2: " + cp.CP2 + "  CP3: " + cp.CP3 + "  CP4: " + cp.CP4);
      console.log("Gate — init: " + gates.init + "  plan: " + gates.plan + "  exec: " + gates.exec + "  verify: " + gates.verify + "  complete: " + gates.complete)
        + (failedGates.length > 0 ? chalk.red("  ❌ " + failedGates.join(", ") + " failed") : chalk.gray("  🟢 all clear"));
      if (heal.enabled) {
        const histLen = (heal.retryHistory || []).length;
        console.log(chalk.gray("Healing:  ") + chalk.green("ON") + chalk.gray(" (attempt " + (heal.currentAttempt || 0) + "/" + (heal.maxAttempts || 3) + ", history: " + histLen + ")"));
      } else {
        console.log(chalk.gray("Healing:  OFF"));
      }
      console.log(chalk.gray("Autonomy: L" + (state.autonomy?.level || 4) + "  |  Tasks: " + (state.metrics?.tasksCompleted || 0) + " done, " + (state.metrics?.tasksBlocked || 0) + " blocked\n"));
      break;
    }
    case "start": {
      if (!args) { log.err("Usage: harness state start <task-description>"); process.exit(1); }
      state.lastUpdated = new Date().toISOString();
      state.gates.init = "in_progress";
      writeState(projectDir, state);
      log.ok("Task started: " + args);
      break;
    }
    case "done": {
      state.gates.init = "passed";
      state.gates.plan = "passed";
      state.gates.exec = "passed";
      state.gates.verify = "passed";
      state.metrics.tasksCompleted = (state.metrics.tasksCompleted || 0) + 1;
      state.lastUpdated = new Date().toISOString();
      writeState(projectDir, state);
      log.ok("Task marked as done");
      break;
    }
    case "blocked": {
      if (!args) { log.err("Usage: harness state blocked <reason>"); process.exit(1); }
      state.gates.exec = "blocked";
      state.metrics.tasksBlocked = (state.metrics.tasksBlocked || 0) + 1;
      state.lastUpdated = new Date().toISOString();
      writeState(projectDir, state);
      log.warn("Blocked: " + args);
      break;
    }
    case "gate": {
      const argsStr = Array.isArray(args) ? args.join(" ") : (args || ""); const [gateName, gateStatus] = argsStr ? argsStr.split(" ") : [];
      if (!gateName || !gateStatus) { log.err("Usage: harness state gate <name> <passed|failed|pending>"); process.exit(1); }
      if (state.gates[gateName] !== undefined) {
        state.gates[gateName] = gateStatus;
        state.lastUpdated = new Date().toISOString();
        writeState(projectDir, state);
        log.ok("Gate '" + gateName + "' → " + gateStatus);
      } else { log.err("Unknown gate: " + gateName); }
      break;
    }
    case "cp": {
      const argsStr2 = Array.isArray(args) ? args.join(" ") : (args || ""); const [cpName, cpStatus] = argsStr2 ? argsStr2.split(" ") : [];
      if (!cpName || !cpStatus) { log.err("Usage: harness state cp <CP0-CP4> <completed|failed|pending>"); process.exit(1); }
      if (state.checkpoints[cpName]) {
        state.checkpoints[cpName] = cpStatus;
        state.lastUpdated = new Date().toISOString();
        writeState(projectDir, state);
        log.ok("Checkpoint '" + cpName + "' → " + cpStatus);
      } else { log.err("Unknown checkpoint: " + cpName); }
      break;
    }
    case "level": {
      const level = parseInt(args, 10);
      if (![1,2,3,4,5,6,7,8,9].includes(level)) { log.err("Autonomy level must be 1-9"); process.exit(1); }
      state.autonomy = state.autonomy || {};
      state.autonomy.level = level;
      state.autonomy.autoMergeOnCI = level >= 5;
      state.lastUpdated = new Date().toISOString();
      writeState(projectDir, state);
      log.ok("Autonomy level → L" + level);
      break;
    }
    case "stats": {
      const m = state.metrics || {};
      console.log("\n" + chalk.bold("Metrics — " + state.project));
      console.log("  Tasks completed: " + (m.tasksCompleted || 0));
      console.log("  Tasks blocked:   " + (m.tasksBlocked || 0));
      console.log("  Avg duration:    " + ((m.averageTaskDuration || 0) / 1000).toFixed(1) + "s");
      console.log("  First-try pass:  " + ((m.firstTryPassRate || 0)) + "%");
      const recent = state.recentChanges?.length || 0;
      console.log("  Recent changes:  " + recent);
      console.log("");
      break;
    }
    case "export": {
      const output = JSON.stringify(state, null, 2);
      console.log(output);
      break;
    }
    case "history": {
      const tasks = state.taskHistory || [];
      const recent = state.recentChanges || [];
      console.log(chalk.bold("\n📋 Task History — " + state.project));
      console.log(chalk.gray("  (last " + Math.min(tasks.length, 20) + " of " + tasks.length + " tasks)\n"));
      if (tasks.length === 0) {
        console.log(chalk.gray("    No completed tasks yet."));
      } else {
        const recentTasks = [...tasks].reverse().slice(0, 10);
        for (const t of recentTasks) {
          const ts = t.completedAt ? t.completedAt.replace("T", " ").slice(0, 16) : "?";
          console.log("  " + chalk.green("✓") + "  " + ts + "  " + (t.task || ""));
        }
      }
      console.log();
      const heals = (state.healing?.retryHistory || []).slice(-5);
      if (heals.length > 0) {
        console.log(chalk.bold("🔧 Healing History"));
        console.log(chalk.gray("  (last " + heals.length + " attempts)\n"));
        for (const h of heals) {
          const ts = h.timestamp ? h.timestamp.replace("T", " ").slice(0, 16) : "?";
          const icon = h.status === "passed" ? chalk.green("✓") : chalk.red("✗");
          const gates = (h.failedGates || []).join(", ");
          const err = h.errorSummary ? h.errorSummary.slice(0, 50) : "";
          console.log("  " + icon + "  " + ts + "  " + chalk.gray("[" + gates + "]") + "  " + err);
        }
        console.log();
      }
      break;
    }
    default:
      log.err("Unknown state command: " + cmd);
      console.log("Usage: harness state <show|start|done|blocked|gate|cp|level|stats|export|history>");
      process.exit(1);
  }
}

// harness verify [project-dir]
function verifyCommand(projectDir) {
  const target = path.resolve(projectDir || process.cwd());
  console.log("\n" + chalk.bold("═".repeat(50)));
  console.log(chalk.bold("🔍 Running Quality Gates") + "  —  " + target);
  console.log(chalk.bold("═".repeat(50)) + "\n");

  // Load state
  const stateFile = path.join(target, "harness/feedback/state/state.json");
  let state = null;
  if (fs.existsSync(stateFile)) state = JSON.parse(fs.readFileSync(stateFile, "utf8"));

  // Parse gates
  const constraintsPath = path.join(target, "harness/base/constraints.md");
  const gates = parseGates(constraintsPath);
  const results = [];
  let allPassed = true;

  for (const gate of gates) {
    const label = gate.desc || gate.name;
    console.log(chalk.bold("Gate: " + label));
    console.log("   " + chalk.gray(gate.cmd));

    const result = runCmd(gate.cmd, target);
    const elapsed = ((result.time) / 1000).toFixed(1);

    if (result.ok) {
      console.log("   " + chalk.green("✅ Passed") + "  (" + elapsed + "s)\n");
      results.push({ gate: gate.name, status: "passed", time: result.time });
    } else {
      allPassed = false;
      const truncated = result.stdout.length > 500 ? result.stdout.slice(0, 500) + "\n... (truncated)" : result.stdout;
      console.log("   " + chalk.red("❌ Failed") + "  (" + elapsed + "s)");
      if (result.stderr) console.log("     " + chalk.red(result.stderr));
      if (truncated) console.log("     " + chalk.gray(truncated));
      console.log();
      results.push({ gate: gate.name, status: "failed", time: result.time, error: result.stdout });
    }
  }

  // Update state + healing
  if (state) {
    for (const r of results) {
      if (state.gates[r.gate] !== undefined) state.gates[r.gate] = r.status;
    }
    state.gates.verify = allPassed ? "passed" : "failed";
    state.lastUpdated = new Date().toISOString();

    // Update healing state when gates fail
    if (!allPassed) {
      state.healing = state.healing || { enabled: true, maxAttempts: 3, autoHeal: true };
      const failed = results.filter(r => r.status === "failed");
      state.healing.currentAttempt = (state.healing.currentAttempt || 0) + 1;
      state.healing.lastAttempt = new Date().toISOString();
      state.healing.lastError = failed.map(r => r.gate + ": " + (r.error || "").slice(0, 80)).join("; ");
      state.healing.retryHistory = state.healing.retryHistory || [];
      state.healing.retryHistory.push({
        attempt: state.healing.currentAttempt,
        timestamp: new Date().toISOString(),
        failedGates: failed.map(r => r.gate),
        errorSummary: state.healing.lastError.slice(0, 200),
        filesTouched: [],
        status: "failed"
      });
      if (state.healing.retryHistory.length > 20) state.healing.retryHistory = state.healing.retryHistory.slice(-20);
    }

    writeState(target, state);
  }

  console.log(chalk.bold("═".repeat(50)));
  if (allPassed) {
    console.log(chalk.green("🎉 All gates passed!\n"));
  } else {
    const failed = results.filter(r => r.status === "failed").map(r => r.gate).join(", ");
    console.log(chalk.red("❌ Gates failed: " + failed) + "\n");
  }
  process.exit(allPassed ? 0 : 1);
}

// harness benchmark [project]
function benchmarkCommand(projectDir) {
  const target = path.resolve(projectDir || process.cwd());
  log.info("Running benchmark: " + target);
  const script = path.join(ROOT, "tools/benchmark/runner.py");
  if (!fs.existsSync(script)) { log.err("Benchmark script not found"); process.exit(1); }
  try {
    execSync("python3 \"" + script + "\" --project \"" + target + "\" --output text", { cwd: ROOT, stdio: "inherit" });
  } catch (e) { log.warn("Benchmark completed with issues"); }
}

// harness test [project-dir]
function testCommand(projectDir) {
  const target = path.resolve(projectDir || process.cwd());
  const pkgFile = path.join(target, "package.json");
  if (!fs.existsSync(pkgFile)) { log.err("No package.json found in: " + target); process.exit(1); }

  // Detect test command
  try {
    const pkg = JSON.parse(fs.readFileSync(pkgFile, "utf8"));
    const testCmd = pkg.scripts?.test || "npm test";
    log.info("Running: " + testCmd);
    execSync(testCmd, { cwd: target, stdio: "inherit" });
    log.ok("Tests passed");
  } catch (e) {
    log.err("Tests failed (exit " + (e.status || 1) + ")");
    process.exit(e.status || 1);
  }
}

// harness log
function logCommand(targetDir, opts) {
  const target = path.resolve(targetDir || process.cwd());
  const stateFile = path.join(target, "harness/feedback/state/state.json");
  if (!fs.existsSync(stateFile)) { log.err("No harness found"); process.exit(1); }
  const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
  const changes = state.recentChanges || [];

  if (changes.length === 0) {
    console.log(chalk.gray("  No recent changes recorded."));
    return;
  }

  const limit = opts?.limit || 10;
  const reversed = [...changes].reverse().slice(0, limit);

  console.log("\n" + chalk.bold("Recent Changes — " + state.project));
  console.log(chalk.gray("  (last " + reversed.length + " of " + changes.length + ")\n"));
  for (const c of reversed) {
    const ts = c.timestamp ? c.timestamp.replace("T", " ").slice(0, 19) : "";
    const typeTag = "[" + (c.type || "?").toUpperCase().padEnd(10) + "]";
    const typeColor = c.type === "completed" ? chalk.green : c.type === "blocked" ? chalk.red : chalk.blue;
    console.log("  " + ts + "  " + typeColor(typeTag) + "  " + (c.description || ""));
  }
  console.log();
}

// harness diff [project-dir] [cp]
function diffCommand(projectDir, cpArg) {
  const target = path.resolve(projectDir || process.cwd());
  // Get CP checkpoint from args or latest
  const cp = cpArg || "HEAD";
  try {
    // Get changed files since last commit
    const out = execSync("git diff --name-only " + cp + " -- .", { cwd: target, encoding: "utf8", stdio: "pipe" });
    const files = out.trim().split("\n").filter(Boolean);
    if (files.length === 0) {
      console.log(chalk.gray("  No file changes since " + cp));
      return;
    }
    console.log("\n" + chalk.bold("Changed Files — " + target.split("/").pop()));
    console.log(chalk.gray("  Since: " + cp + "\n"));
    for (const f of files) {
      console.log("  " + chalk.blue("~") + "  " + f);
    }
    console.log(chalk.gray("\n  " + files.length + " file(s) changed\n"));
  } catch (e) {
    log.err("git diff failed: " + (e.stderr || e.message));
    process.exit(1);
  }
}

// harness score [project-dir]
function scoreCommand(projectDir) {
  const target = path.resolve(projectDir || process.cwd());
  const stateFile = path.join(target, "harness/feedback/state/state.json");
  if (!fs.existsSync(stateFile)) { log.err("No harness found"); process.exit(1); }

  const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
  const gates = state.gates || {};
  const heal = state.healing || {};
  const metrics = state.metrics || {};
  const autonomy = state.autonomy || {};

  // Gate score (40%)
  const gateKeys = Object.keys(gates);
  let gateScore = 50; // neutral baseline
  if (gateKeys.length > 0) {
    const failed = gateKeys.filter(k => gates[k] === "failed").length;
    const passed = gateKeys.filter(k => gates[k] === "passed").length;
    gateScore = Math.round(((passed + (gateKeys.length - failed) * 0.5) / gateKeys.length) * 100);
  }

  // Healing score (30%) — more retry history = lower autonomy quality
  const historyLen = (heal.retryHistory || []).length;
  const healScore = Math.max(0, 100 - historyLen * 25);

  // Metrics score (20%) — task completion ratio
  const completed = metrics.tasksCompleted || 0;
  const blocked = metrics.tasksBlocked || 0;
  const total = completed + blocked || 1;
  const metricScore = Math.round((completed / total) * 100);

  // Autonomy score (10%) — higher level = more autonomous
  const level = autonomy.level || 4;
  const autonomyScore = Math.min(100, Math.round((level / 9) * 100));

  const totalScore = Math.round(gateScore * 0.4 + healScore * 0.3 + metricScore * 0.2 + autonomyScore * 0.1);

  // Grade
  let grade, gradeColor;
  if (totalScore >= 90) { grade = "S"; gradeColor = chalk.green; }
  else if (totalScore >= 75) { grade = "A"; gradeColor = chalk.green; }
  else if (totalScore >= 60) { grade = "B"; gradeColor = chalk.blue; }
  else if (totalScore >= 40) { grade = "C"; gradeColor = chalk.yellow; }
  else { grade = "D"; gradeColor = chalk.red; }

  console.log(chalk.bold("\n📊 Harness Score — " + (state.project || target.split("/").pop())));
  console.log(chalk.gray("  Total: ") + gradeColor(grade) + chalk.gray("  ") + gradeColor(String(totalScore)) + chalk.gray("/100\n"));
  console.log(chalk.gray("  Gate Score   (40%) = ") + (gateScore >= 75 ? chalk.green : gateScore >= 50 ? chalk.yellow : chalk.red)(String(gateScore) + "/100"));
  console.log(chalk.gray("  Heal Score  (30%) = ") + (healScore >= 75 ? chalk.green : healScore >= 50 ? chalk.yellow : chalk.red)(String(healScore) + "/100") + chalk.gray("  (retry history: " + historyLen + ")"));
  console.log(chalk.gray("  Metric Score(20%) = ") + (metricScore >= 75 ? chalk.green : metricScore >= 50 ? chalk.yellow : chalk.red)(String(metricScore) + "/100") + chalk.gray("  (blocked: " + blocked + ")"));
  console.log(chalk.gray("  Autonomy Lv (10%) = ") + chalk.blue(String(autonomyScore) + "/100") + chalk.gray("  (L" + level + ")"));
  console.log();

  if (totalScore < 60) {
    console.log(chalk.yellow("  💡 Run `harness heal` to auto-repair failed gates"));
    console.log(chalk.yellow("  💡 Run `harness benchmark` for full evaluation\n"));
  } else {
    console.log(chalk.green("  ✅ Healthy — ready for next task\n"));
  }
}

// harness clean
function cleanCommand(targetDir) {
  const target = path.resolve(targetDir || process.cwd());
  const harnessDir = path.join(target, "harness");
  if (!fs.existsSync(harnessDir)) {
    log.warn("No harness found in: " + target);
    process.exit(0);
  }
  log.info("Cleaning harness state in: " + target);
  const stateFile = path.join(harnessDir, "feedback/state/state.json");
  if (fs.existsSync(stateFile)) {
    try {
      const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
      state.checkpoints = { CP0: "pending", CP1: "pending", CP2: "pending", CP3: "pending", CP4: "pending" };
      state.gates = { init: "pending", plan: "pending", exec: "pending", verify: "pending", complete: "pending" };
      state.healing = { enabled: true, maxAttempts: 3, currentAttempt: 0, lastAttempt: null, lastError: null, retryHistory: [], autoHeal: true };
      state.lastUpdated = new Date().toISOString();
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
      log.ok("State reset to CP0");
    } catch (e) { log.err("Failed to reset state: " + e.message); process.exit(1); }
  }
  log.ok("Clean complete");
}

// harness doctor
function doctorCommand() {
  console.log("\n" + chalk.bold("🔍 Harness Doctor"));
  console.log(chalk.gray("  Checking environment...\n"));
  let issues = 0;

  // Check Node version
  const nodeVersion = process.version.replace("v", "").split(".")[0];
  if (parseInt(nodeVersion) >= 18) {
    log.ok("Node.js " + process.version + " (>= 18 required)");
  } else {
    log.err("Node.js " + process.version + " (need >= 18)");
    issues++;
  }

  // Check workspace harness state
  const cwd = process.cwd();
  const stateFile = path.join(cwd, "harness/feedback/state/state.json");
  if (fs.existsSync(stateFile)) {
    log.ok("Harness initialized");
    try {
      const raw = fs.readFileSync(stateFile, "utf8");
      const state = JSON.parse(raw);
      console.log(chalk.gray("    Project:  " + (state.project || "unknown")));
      console.log(chalk.gray("    Schema:   " + (state._schema || "none") + " v" + (state.version || "?")));

      // Gate summary
      const gates = state.gates || {};
      const gateKeys = Object.keys(gates);
      if (gateKeys.length > 0) {
        const failed = gateKeys.filter(k => gates[k] === "failed").length;
        const icon = failed > 0 ? chalk.red("🔴 " + failed + " failed") : chalk.green("🟢 all clear");
        console.log(chalk.gray("    Gates:    ") + icon + chalk.gray(" (" + gateKeys.length + " gates)"));
      }

      // Healing summary
      const heal = state.healing;
      if (heal) {
        const icon = heal.enabled ? chalk.green("ON") : chalk.yellow("OFF");
        const attempt = heal.currentAttempt || 0;
        const max = heal.maxAttempts || 3;
        console.log(chalk.gray("    Healing:  ") + icon + chalk.gray(" (attempt " + attempt + "/" + max + ")"));
        if (heal.lastError) {
          console.log(chalk.red("    LastErr:  " + heal.lastError.slice(0, 60)));
        }
      } else {
        console.log(chalk.gray("    Healing:  not configured"));
      }

      // Check schema validity using state-validator
      const validator = path.join(ROOT, "tools/validator/state-validator.py");
      if (fs.existsSync(validator)) {
        try {
          const result = execSync("python3 \"" + validator + "\" \"" + stateFile + "\" 2>&1", { encoding: "utf8" });
          if (result.includes("✅") && !result.includes("❌")) {
            log.ok("Schema valid (harness-state-v2)");
          } else if (result.includes("❌")) {
            log.err("Schema invalid — run: python3 " + path.relative(cwd, validator));
            issues++;
          }
        } catch (e) {
          const out = e.stdout || e.stderr || "";
          if (out.includes("❌") || out.includes("failed")) {
            log.err("Schema validation failed");
            issues++;
          }
        }
      }
    } catch (e) {
      log.err("Malformed state.json: " + e.message);
      issues++;
    }
  } else {
    log.warn("No harness initialized (run: harness init)");
  }

  // Check required commands
  const requiredCmds = ["git", "node", "npm"];
  for (const cmd of requiredCmds) {
    try {
      execSync("which " + cmd, { stdio: "ignore" });
      log.ok(cmd + " available");
    } catch (_) {
      log.err(cmd + " not found");
      issues++;
    }
  }

  // Check CLI
  const cliBin = path.join(ROOT, "packages/cli/bin/harness.js");
  if (fs.existsSync(cliBin)) {
    log.ok("CLI: " + cliBin);
  } else {
    log.warn("CLI not found (install via: npm install -g @harnesskit/cli)");
  }
  console.log();
  console.log((issues === 0 ? chalk.green("✅ All checks passed") : chalk.red("❌ " + issues + " issue(s) found")));
  process.exit(issues > 0 ? 1 : 0);
}

// harness open-pr [args]
function openPrCommand(args) {
  const script = path.join(ROOT, "scripts/open-pr.sh");
  if (!fs.existsSync(script)) { log.err("open-pr.sh not found"); process.exit(1); }
  try {
    execSync("bash \"" + script + "\" " + args, { stdio: "inherit", cwd: ROOT });
  } catch (e) { log.err("open-pr.sh failed"); process.exit(1); }
}

// ── Main CLI ─────────────────────────────────────────────────────────────────
const program = new Command();
program
  .name("harness")
  .description("Harness CLI — Engineering workflow for AI coding agents")
  .version("1.0.0");

program
  .command("init")
  .description("Initialize harness in a project (type: nuwax|electron|generic)")
  .argument("[type]", "Project type (nuwax|electron|generic)")
  .argument("[target-dir]", "Target directory (default: cwd)")
  .option("-t, --template <name>", "Template: package|basic|advanced (default: package)")
  .action(initCommand);

program
  .command("benchmark [project-dir]")
  .description("Run harness benchmark scoring")
  .action(benchmarkCommand);

program
  .command("test [project-dir]")
  .description("Run project tests (npm test)")
  .action(testCommand);

program
  .command("state <cmd> [args...]")
  .description("Manage harness state (show|start|done|blocked|gate|cp|level|stats|history|export)")
  .action(stateCommand);

program
  .command("verify [project-dir]")
  .description("Run quality gate verification (lint → typecheck → test → build)")
  .action(verifyCommand);

program
  .command("heal [project-dir]")
  .description("Run CP4 self-healing loop (auto-repair failed gates)")
  .option("--dry-run", "Analyze errors without fixing")
  .option("--force", "Force retry even if max attempts reached")
  .option("--max <n>", "Max healing attempts")
  .action(function(projectDir, opts) {
    const target = path.resolve(projectDir || process.cwd());
    const stateFile = path.join(target, "harness/feedback/state/state.json");
    if (!fs.existsSync(stateFile)) { log.err("No harness found. Run: harness init"); process.exit(1); }
    // Delegate to agent-harness
    const agentHarness = path.join(ROOT, "packages/agent-harness/index.js");
    if (!fs.existsSync(agentHarness)) { log.err("agent-harness not found"); process.exit(1); }
    const healArgs = [];
    if (opts.dryRun) healArgs.push("--dry-run");
    if (opts.force) healArgs.push("--force");
    if (opts.max) healArgs.push(String(opts.max));
    const shellCmd = "node \"" + agentHarness + "\" heal " + healArgs.join(" ");
    try {
      execSync(shellCmd, { cwd: target, stdio: "inherit" });
    } catch (e) { process.exit(e.status || 1); }
  });

program
  .command("healing <on|off|status>")
  .description("Enable/disable self-healing (on|off|status)")
  .action(function(action) {
    const cwd2 = process.cwd();
    const stateFile = path.join(cwd2, "harness/feedback/state/state.json");
    if (!fs.existsSync(stateFile)) { log.err("No harness found. Run: harness init"); process.exit(1); }
    const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
    state.healing = state.healing || { enabled: true, maxAttempts: 3, autoHeal: true };
    if (action === "status") {
      console.log("\n🔧 Healing Status — " + state.project);
      console.log("  Enabled:     " + (state.healing.enabled ? "yes" : "no"));
      console.log("  Max attempts: " + state.healing.maxAttempts);
      console.log("  Current:     " + (state.healing.currentAttempt || 0));
      console.log("  Auto-heal:   " + (state.healing.autoHeal ? "yes" : "no"));
      if (state.healing.retryHistory?.length > 0) {
        console.log("  History:     " + state.healing.retryHistory.length + " attempt(s)");
        for (const h of state.healing.retryHistory.slice(-3)) {
          console.log("    [Attempt " + h.attempt + "] " + h.status + ": " + h.failedGates.join(", "));
        }
      }
      console.log("");
      return;
    }
    if (action === "on") { state.healing.enabled = true; state.healing.autoHeal = true; }
    if (action === "off") { state.healing.enabled = false; state.healing.autoHeal = false; }
    state.lastUpdated = new Date().toISOString();
    fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
    log.ok("Healing " + (action === "on" ? "enabled" : "disabled"));
  });

program
  .command("open-pr [args]")
  .description("Open PR after CP3")
  .action(openPrCommand);

program
  .command("clean [target-dir]")
  .description("Reset harness state to CP0 (clean project)")
  .action(cleanCommand);

program
  .command("score [project-dir]")
  .description("Show quick harness score from state.json (no benchmark run)")
  .action(scoreCommand);

program
  .command("doctor")
  .description("Check environment and harness status")
  .action(doctorCommand);

program
  .command("log [target-dir]")
  .description("Show recent changes from state.json")
  .option("-n, --limit <n>", "Number of entries to show", "10")
  .action(logCommand);

program
  .command("diff [project-dir] [cp]")
  .description("Show changed files since <cp> (default: HEAD)")
  .action(diffCommand);

program
  .command("help")
  .description("Show this help")
  .action(() => program.help());

program.parse(process.argv);