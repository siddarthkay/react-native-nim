#!/usr/bin/env node

const { main } = require('../src/index.js');
main().catch((err) => {
  console.error(`\n  ${err.message}`);
  process.exit(1);
});
