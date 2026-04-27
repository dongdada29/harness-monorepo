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
      console.log("\n" + chalk.bold("Harness State") + " — " + state.project);
      console.log("CP0: " + state.checkpoints.CP0 + "  CP1: " + state.checkpoints.CP1 + "  CP2: " + state.checkpoints.CP2 + "  CP3: " + state.checkpoints.CP3 + "  CP4: " + state.checkpoints.CP4);
      console.log("Gate — init: " + state.gates.init + "  plan: " + state.gates.plan + "  exec: " + state.gates.exec + "  verify: " + state.gates.verify + "  complete: " + state.gates.complete);
      console.log("Autonomy: L" + (state.autonomy?.level || 4));
      console.log("Tasks: " + state.metrics.tasksCompleted + " completed, " + state.metrics.tasksBlocked + " blocked\n");
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
    default:
      log.err("Unknown state command: " + cmd);
      console.log("Usage: harness state <show|start|done|blocked|gate|cp|level|stats|export>");
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

  // Update state
  if (state) {
    for (const r of results) {
      if (state.gates[r.gate] !== undefined) state.gates[r.gate] = r.status;
    }
    state.gates.verify = allPassed ? "passed" : "failed";
    state.lastUpdated = new Date().toISOString();
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

  // Check workspace
  const cwd = process.cwd();
  const stateFile = path.join(cwd, "harness/feedback/state/state.json");
  if (fs.existsSync(stateFile)) {
    log.ok("Harness initialized (harness/ found)");
    try {
      const state = JSON.parse(fs.readFileSync(stateFile, "utf8"));
      const cp = state.checkpoints;
      console.log(chalk.gray("    Project: " + state.project));
      console.log(chalk.gray("    CP0:" + cp.CP0 + " CP1:" + cp.CP1 + " CP2:" + cp.CP2 + " CP3:" + cp.CP3 + " CP4:" + cp.CP4));
    } catch (_) {}
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
    log.ok("CLI installed: " + cliBin);
  } else {
    log.warn("CLI not found (install via: npm install -g @harnesskit/cli)");
  }
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
  .argument("[project-dir]", "Target directory (default: cwd)")
  .action(testCommand);

program
  .command("state <cmd> [args...]")
  .description("Manage harness state (show|start|done|blocked|gate|cp|level)")
  .action(stateCommand);

program
  .command("verify [project-dir]")
  .description("Run quality gate verification (lint → typecheck → test → build)")
  .action(verifyCommand);

program
  .command("open-pr [args]")
  .description("Open PR after CP3")
  .action(openPrCommand);

program
  .command("clean [target-dir]")
  .description("Reset harness state to CP0 (clean project)")
  .action(cleanCommand);

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