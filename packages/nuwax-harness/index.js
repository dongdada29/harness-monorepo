#!/usr/bin/env node
/**
 * @harnesskit/nuwax-harness
 * Nuwax Agent OS — tailored harness for Nuwax project workflow
 */
const path = require('path');

module.exports = {
  name: '@harnesskit/nuwax-harness',
  version: '1.0.0',
  description: 'Nuwax Agent OS harness — tailored for Nuwax project workflow',
  main: path.join(__dirname, 'harness'),
  scripts: {
    verify: 'bash scripts/verify.sh',
    'update-state': 'bash scripts/update-state.sh',
    'open-pr': 'bash ../../scripts/open-pr.sh',
  },
};
