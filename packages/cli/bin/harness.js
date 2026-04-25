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
  if (exists(path.join(dir, "package.json"))) {
    const pkg = JSON.parse(fs.readFileSync(path.join(dir, "package.json"), "utf8"));
    if (pkg.name && pkg.name.includes("nuwax")) return "nuwax";
    if (pkg.dependencies?.electron || pkg.devDependencies?.electron) return "electron";
  }
  return "generic";
}

function readState(projectDir) {
  const stateFile = path.join(projectDir, "harness/feedback/state/state.json");
  if (fs.existsSync(stateFile)) {
    return JSON.parse(fs.readFileSync(stateFile, "utf8"));
  }
  return null;
}

// ── Commands ────────────────────────────────────────────────────────────────

// harness init [type] [target-dir]
function initCommand(type, targetDir) {
  const target = path.resolve(targetDir || process.cwd());
  const HarnessType = type || detectProjectType(target);

  const pkgMap = {
    nuwax: "@harnesskit/nuwax-harness",
    electron: "@harnesskit/electron-harness",
    agent: "@harnesskit/agent-harness",
    generic: "@harnesskit/generic-harness",
  };

  const pkgName = pkgMap[HarnessType] || pkgMap.generic;
  const srcHarness = path.join(PKG_ROOT, "../", `${pkgName.replace("@harnesskit/", "")}-harness/harness`);
  const srcBase = path.join(PKG_ROOT, "../agent-harness/harness/base");

  log.info(`Initializing harness in: ${target}`);
  log.info(`Type: ${HarnessType} (${pkgName})`);

  // Create harness dir
  const harnessDir = path.join(target, "harness");
  fs.mkdirSync(harnessDir, { recursive: true });
  fs.mkdirSync(path.join(harnessDir, "feedback/state"), { recursive: true });

  // Copy base harness
  try {
    if (fs.existsSync(srcBase)) {
      copyDir(srcBase, path.join(harnessDir, "base"));
      log.ok("Base harness installed");
    }
    if (fs.existsSync(srcHarness)) {
      copyDir(srcHarness, path.join(harnessDir, "overlay"));
      log.ok("Overlay harness installed");
    }
  } catch (e) {
    log.warn("Some files not found — continuing");
  }

  // Write state.json
  const stateFile = path.join(harnessDir, "feedback/state/state.json");
  const state = {
    _schema: "harness-state-v2",
    version: "2.0.0",
    project: path.basename(target),
    type: "generic",
    platform: "agent-desktop",
    lastUpdated: new Date().toISOString(),
    checkpoints: {
      CP0: "pending",
      CP1: "pending",
      CP2: "pending",
      CP3: "pending",
      CP4: "pending",
    },
    gates: {
      init: "pending",
      plan: "pending",
      exec: "pending",
      verify: "pending",
      complete: "pending",
    },
    metrics: {
      tasksCompleted: 0,
      tasksBlocked: 0,
    },
    autonomy: {
      level: 4,
      requireApprovalFor: [],
      autoMergeOnCI: false,
    },
  };

  fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
  log.ok(`State initialized: ${stateFile}`);

  console.log(chalk.green("\n✅ Harness initialized successfully!"));
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
      const c = chalk;
      console.log(`\n${c.bold("Harness State")} — ${state.project}`);
      console.log(`CP0: ${state.checkpoints.CP0}  CP1: ${state.checkpoints.CP1}  CP2: ${state.checkpoints.CP2}  CP3: ${state.checkpoints.CP3}  CP4: ${state.checkpoints.CP4}`);
      console.log(`Gate — init: ${state.gates.init}  plan: ${state.gates.plan}  exec: ${state.gates.exec}  verify: ${state.gates.verify}  complete: ${state.gates.complete}`);
      console.log(`Autonomy: L${state.autonomy?.level || 4}`);
      console.log(`Tasks: ${state.metrics.tasksCompleted} completed, ${state.metrics.tasksBlocked} blocked\n`);
      break;
    }
    case "start": {
      if (!args) {
        log.err("Usage: harness state start <task-description>");
        process.exit(1);
      }
      state.lastUpdated = new Date().toISOString();
      state.gates.init = "in_progress";
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
      log.ok(`Task started: ${args}`);
      break;
    }
    case "done": {
      state.gates.init = "passed";
      state.gates.plan = "passed";
      state.gates.exec = "passed";
      state.gates.verify = "passed";
      state.metrics.tasksCompleted = (state.metrics.tasksCompleted || 0) + 1;
      state.lastUpdated = new Date().toISOString();
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
      log.ok("Task marked as done");
      break;
    }
    case "blocked": {
      if (!args) {
        log.err("Usage: harness state blocked <reason>");
        process.exit(1);
      }
      state.gates.exec = "blocked";
      state.metrics.tasksBlocked = (state.metrics.tasksBlocked || 0) + 1;
      state.lastUpdated = new Date().toISOString();
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
      log.warn(`Blocked: ${args}`);
      break;
    }
    case "gate": {
      const [gateName, gateStatus] = args ? args.split(" ") : [];
      if (!gateName || !gateStatus) {
        log.err("Usage: harness state gate <name> <passed|failed|pending>");
        process.exit(1);
      }
      if (state.gates[gateName]) {
        state.gates[gateName] = gateStatus;
        state.lastUpdated = new Date().toISOString();
        fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
        log.ok(`Gate '${gateName}' → ${gateStatus}`);
      } else {
        log.err(`Unknown gate: ${gateName}`);
      }
      break;
    }
    case "cp": {
      const [cpName, cpStatus] = args ? args.split(" ") : [];
      if (!cpName || !cpStatus) {
        log.err("Usage: harness state cp <CP0-CP4> <completed|failed|pending>");
        process.exit(1);
      }
      if (state.checkpoints[cpName]) {
        state.checkpoints[cpName] = cpStatus;
        state.lastUpdated = new Date().toISOString();
        fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
        log.ok(`Checkpoint '${cpName}' → ${cpStatus}`);
      } else {
        log.err(`Unknown checkpoint: ${cpName}`);
      }
      break;
    }
    case "level": {
      const level = parseInt(args, 10);
      if (![1, 2, 3, 4, 5, 6, 7, 8, 9].includes(level)) {
        log.err("Autonomy level must be 1-9");
        process.exit(1);
      }
      state.autonomy = state.autonomy || {};
      state.autonomy.level = level;
      state.autonomy.autoMergeOnCI = level >= 5;
      state.lastUpdated = new Date().toISOString();
      fs.writeFileSync(stateFile, JSON.stringify(state, null, 2));
      log.ok(`Autonomy level → L${level}`);
      break;
    }
    default:
      log.err(`Unknown state command: ${cmd}`);
      console.log("Usage: harness state <show|start|done|blocked|gate|cp|level>");
      process.exit(1);
  }
}

// harness benchmark [project]
function benchmarkCommand(projectDir) {
  const target = path.resolve(projectDir || process.cwd());
  log.info(`Running benchmark: ${target}`);

  const script = path.join(ROOT, "tools/benchmark/runner.py");
  if (!fs.existsSync(script)) {
    log.err("Benchmark script not found");
    process.exit(1);
  }

  try {
    const out = execSync(`python3 "${script}" --project "${target}" --output text`, {
      cwd: ROOT,
      stdio: "inherit",
    });
  } catch (e) {
    // runner.py exits non-zero on low scores, but we still want to show output
    // so we just warn
    log.warn("Benchmark completed with issues");
  }
}

// harness open-pr [args]
function openPrCommand(args) {
  const script = path.join(ROOT, "scripts/open-pr.sh");
  if (!fs.existsSync(script)) {
    log.err("open-pr.sh not found");
    process.exit(1);
  }

  try {
    const fullCmd = `bash "${script}" ${args}`;
    execSync(fullCmd, { stdio: "inherit", cwd: ROOT });
  } catch (e) {
    log.err("open-pr.sh failed");
    process.exit(1);
  }
}

// ── Main CLI ─────────────────────────────────────────────────────────────────
const program = new Command();

program
  .name("harness")
  .description("Harness CLI — Engineering workflow for AI coding agents")
  .version("1.0.0");

program
  .command("init [type] [target-dir]")
  .description("Initialize harness in a project (type: nuwax|electron|generic)")
  .action(initCommand);

program
  .command("benchmark [project-dir]")
  .description("Run harness benchmark scoring")
  .action(benchmarkCommand);

program
  .command("state <cmd> [args]")
  .description("Manage harness state (show|start|done|blocked|gate|cp|level)")
  .action(stateCommand);

program
  .command("verify [project-dir]")
  .description("Run harness verification")
  .action((dir) => {
    const target = path.resolve(dir || process.cwd());
    const script = path.join(PKG_ROOT, "../agent-harness/scripts/verify.sh");
    if (fs.existsSync(script)) {
      execSync(`bash "${script}"`, { stdio: "inherit", cwd: target });
    } else {
      log.err("verify.sh not found");
    }
  });

program
  .command("open-pr [args]")
  .description("Open PR after CP3 (delegates to scripts/open-pr.sh)")
  .action(openPrCommand);

program
  .command("help")
  .description("Show this help")
  .action(() => program.help());

program.parse(process.argv);
