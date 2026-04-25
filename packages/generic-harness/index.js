#!/usr/bin/env node
/**
 * @harnesskit/generic-harness
 * Generic / universal harness — language and framework agnostic
 */
const path = require('path');

module.exports = {
  name: '@harnesskit/generic-harness',
  version: '1.0.0',
  description: 'Generic harness for any project type — language/framework agnostic',
  main: path.join(__dirname, 'harness'),
  scripts: {
    verify: 'bash scripts/verify.sh',
    'update-state': 'bash scripts/update-state.sh',
    'open-pr': 'bash ../../scripts/open-pr.sh',
  },
};
