#!/usr/bin/env node
/**
 * @harnesskit/agent-harness
 * Control theory engineering workflow for Claude Code / Cursor / Codex / OpenCode
 */
const path = require('path');

module.exports = {
  name: '@harnesskit/agent-harness',
  version: '1.0.0',
  description: 'Control theory engineering workflow for AI coding agents',
  main: path.join(__dirname, 'harness'),
  scripts: {
    verify: 'bash scripts/verify.sh',
    'update-state': 'bash scripts/update-state.sh',
    'open-pr': 'bash ../../scripts/open-pr.sh',
  },
};
