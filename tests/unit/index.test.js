#!/usr/bin/env node
/**
 * harness-monorepo unit tests
 * Run with: node --test tests/unit/index.test.js
 */
"use strict";

const { test, describe, before } = require("node:test");
const assert = require("node:assert");
const path = require("path");
const fs = require("fs");
const os = require("os");

const ROOT = path.resolve(__dirname, "../..");
const CLI_BIN = path.join(ROOT, "packages/cli/bin/harness.js");

// ── Test utilities ───────────────────────────────────────────────────────────
function runCmd(cmd, cwd) {
  const { execSync } = require("child_process");
  try {
    return execSync(cmd, { cwd, encoding: "utf8", stdio: "pipe" });
  } catch (e) {
    return e.stdout?.toString() || e.stderr?.toString() || "";
  }
}

function runNode(script, args, cwd) {
  return runCmd("node " + script + " " + args.join(" "), cwd);
}

function mkdtemp() {
  return fs.mkdtempSync(path.join(os.tmpdir(), "harness-test-"));
}

// ── CLI tests ────────────────────────────────────────────────────────────────
describe("CLI: harness init", () => {
  test("init generic with package template", () => {
    const d = mkdtemp();
    const out = runNode(CLI_BIN, ["init", "generic", d], ROOT);
    assert.ok(fs.existsSync(path.join(d, "harness")));
    assert.ok(fs.existsSync(path.join(d, "harness/feedback/state/state.json")));
    assert.ok(fs.existsSync(path.join(d, "harness/base/constraints.md")));
    assert.ok(fs.existsSync(path.join(d, "harness/base/tasks")));
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("init with --template basic creates harness dir", () => {
    const d = mkdtemp();
const out = runNode(CLI_BIN, ["init", "generic", "--template", "basic", d], ROOT);
console.error("TEST harness exists:", fs.existsSync(path.join(d, "harness")));
assert.ok(fs.existsSync(path.join(d, "harness/feedback/state/state.json")), "state.json must exist");
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("init with --template advanced creates harness dir", () => {
    const d = mkdtemp();
    const out = runNode(CLI_BIN, ["init", "generic", "--template", "advanced", d], ROOT);
    assert.ok(fs.existsSync(path.join(d, "harness/feedback/state/state.json")), "state.json must exist");
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("state show works after init", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const out = runNode(CLI_BIN, ["state", "show"], d);
    assert.ok(out.includes("CP0:"));
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("state start works", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const out = runNode(CLI_BIN, ["state", "start", "test task"], d);
    assert.ok(out.includes("Task started") || out.includes("in_progress"));
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("state done works", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const out = runNode(CLI_BIN, ["state", "done"], d);
    assert.ok(out.includes("Task marked as done") || out.includes("passed"));
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("state gate updates gate status", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const out = runNode(CLI_BIN, ["state", "gate", "init", "passed"], d);
    assert.ok(out.includes("Gate") || out.includes("passed"));
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state.gates.init, "passed");
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("state cp updates checkpoint", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    runNode(CLI_BIN, ["state", "cp", "CP0", "completed"], d);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state.checkpoints.CP0, "completed");
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("state level sets autonomy level", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    runNode(CLI_BIN, ["state", "level", "7"], d);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state.autonomy.level, 7);
    assert.strictEqual(state.autonomy.autoMergeOnCI, true);
    fs.rmSync(d, { recursive: true, force: true });
  });
});

describe("CLI: harness verify", () => {
  test("verify runs on empty project", () => {
    const d = mkdtemp();
    fs.mkdirSync(path.join(d, "harness/feedback/state"), { recursive: true });
    fs.writeFileSync(path.join(d, "harness/feedback/state/state.json"), JSON.stringify({
      _schema: "harness-state-v2", version: "2.0.0",
      checkpoints: {}, gates: {}, metrics: {},
      lastUpdated: new Date().toISOString()
    }));
    const out = runNode(CLI_BIN, ["verify", d], ROOT);
    assert.ok(out.includes("Running Quality Gates") || out.includes("Gate"));
    fs.rmSync(d, { recursive: true, force: true });
  });
});

describe("CLI: harness --help", () => {
  test("shows usage", () => {
    const out = runNode(CLI_BIN, ["--help"], ROOT);
    assert.ok(out.includes("Usage:"));
    assert.ok(out.includes("init"));
    assert.ok(out.includes("state"));
    assert.ok(out.includes("verify"));
  });

  test("init --help shows template option", () => {
    const out = runNode(CLI_BIN, ["init", "--help"], ROOT);
    assert.ok(out.includes("--template"));
  });
});

describe("CLI: init type creates correct platform/type", () => {
  test("init nuwax creates nuwax platform", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "nuwax", d], ROOT);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state.platform, "nuwax");
    assert.strictEqual(state.type, "business");
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("init electron creates electron platform", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "electron", d], ROOT);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state.platform, "electron");
    assert.strictEqual(state.type, "tech");
    fs.rmSync(d, { recursive: true, force: true });
  });
});

// ── Package index.js tests ────────────────────────────────────────────────────
describe("packages: index.js CLI", () => {
  for (const [pkg, expectedCmds] of [
    ["agent-harness", ["init", "state", "verify", "run", "checkpoint"]],
    ["nuwax-harness", ["init", "state", "verify", "run", "mcp"]],
    ["electron-harness", ["init", "state", "verify", "run"]],
    ["generic-harness", ["init", "state", "verify", "run"]],
  ]) {
    const indexPath = path.join(ROOT, "packages", pkg, "index.js");

    test(`${pkg} --help shows commands`, () => {
      const out = runNode(indexPath, [], ROOT);
      for (const cmd of expectedCmds) {
        assert.ok(out.includes(cmd), `Expected '${cmd}' in help output`);
      }
    });

    test(`${pkg} init creates state.json`, () => {
      const d = mkdtemp();
      runNode(indexPath, ["init"], d);
      const statePath = path.join(d, "harness/feedback/state/state.json");
      assert.ok(fs.existsSync(statePath), `state.json not created by ${pkg} init`);
      const state = JSON.parse(fs.readFileSync(statePath, "utf8"));
      assert.strictEqual(state._schema, "harness-state-v2");
      fs.rmSync(d, { recursive: true, force: true });
    });
  }
});

// ── Schema tests ─────────────────────────────────────────────────────────────
describe("Schema: state.json format", () => {
  test("init creates v2 schema", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state._schema, "harness-state-v2");
    assert.strictEqual(state.version, "2.0.0");
    assert.ok(state.checkpoints);
    assert.ok(state.gates);
    assert.ok(state.metrics);
    assert.ok(state.autonomy);
    assert.ok(state.lastUpdated);
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("init creates all 5 checkpoints", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    for (const cp of ["CP0", "CP1", "CP2", "CP3", "CP4"]) {
      assert.strictEqual(state.checkpoints[cp], "pending");
    }
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("init creates all 5 gates", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    for (const gate of ["init", "plan", "exec", "verify", "complete"]) {
      assert.strictEqual(state.gates[gate], "pending");
    }
    fs.rmSync(d, { recursive: true, force: true });
  });

  test("autonomy defaults to L4 with autoMergeOnCI false", () => {
    const d = mkdtemp();
    runNode(CLI_BIN, ["init", "generic", d], ROOT);
    const state = JSON.parse(fs.readFileSync(path.join(d, "harness/feedback/state/state.json"), "utf8"));
    assert.strictEqual(state.autonomy.level, 4);
    assert.strictEqual(state.autonomy.autoMergeOnCI, false);
    fs.rmSync(d, { recursive: true, force: true });
  });
});

// ── Template tests ───────────────────────────────────────────────────────────
describe("Template: templates directory", () => {
  test("basic template exists", () => {
    assert.ok(fs.existsSync(path.join(ROOT, "templates/basic")));
  });

  test("advanced template exists", () => {
    assert.ok(fs.existsSync(path.join(ROOT, "templates/advanced")));
  });

  test("basic template has README", () => {
    assert.ok(fs.existsSync(path.join(ROOT, "templates/basic/README.md")));
  });

  test("advanced template has README", () => {
    assert.ok(fs.existsSync(path.join(ROOT, "templates/advanced/README.md")));
  });
});