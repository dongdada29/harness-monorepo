#!/usr/bin/env node
/**
 * @harnesskit/electron-harness
 * Electron + Ant Design harness for AI coding agents
 */
const path = require('path');

module.exports = {
  name: '@harnesskit/electron-harness',
  version: '1.0.0',
  description: 'Electron + Ant Design harness for AI coding agents',
  main: path.join(__dirname, 'harness'),
  scripts: {
    verify: 'bash scripts/verify.sh',
    'update-state': 'bash scripts/update-state.sh',
    'open-pr': 'bash ../../scripts/open-pr.sh',
  },
};
