# SF CLI Wrapper Fix

## Problem

`sf` command fails with:
```
Error: Cannot find module 'C:\Users\madco\AppData\Local\hermes\node\node_modules\@salesforce\cli\bin\run.js'
```

The `sf.cmd` wrapper at `/c/Users/madco/AppData/Local/hermes/node/sf.cmd` points to a missing `node_modules/@salesforce/cli/bin/run.js`.

## Fix

Install the CLI into the Hermes node environment:
```bash
cd /c/Users/madco/AppData/Local/hermes/node
npm install @salesforce/cli
```

Verify:
```bash
cd /c/Users/madco/AppData/Local/hermes/node
./sf --version
# Should show: @salesforce/cli/2.x.x win32-x64 node-v24.x.x
```

## Root Cause

The Hermes node environment has its own `node_modules/` directory. The `sf.cmd` wrapper was installed via `winget` but the actual CLI module wasn't present. The Hermes node path (`/c/Users/madco/AppData/Local/hermes/node`) is where Hermes manages its own npm packages.

## Verification

After fix:
1. `./sf --version` works
2. `./sf org list` shows connected orgs
3. `npx @salesforce/mcp --help` works (may show "Could not find file for command: retire" — that's harmless)
