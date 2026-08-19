# Windows SF CLI + MCP Server Troubleshooting

## Session 2026-07-30: Full diagnosis and fix

### Problem
"My Salesforce MCP" server failing to start with "The filename, directory name, or volume label syntax is incorrect" (Windows path error) and "Connection closed" during test.

### Root causes found
1. **`sf` CLI not on PATH** — `winget install OpenCLICollective.salesforce-cli` installs the OLD `sfdx` CLI (sfdc.exe in winget packages dir), not the new `sf` CLI. The new CLI must be installed separately via npm.
2. **`@salesforce/mcp` not installed globally** — npm package was completely absent.
3. **No `mcp_servers` section in config.yaml** — The config had zero MCP entries.
4. **`hermes mcp add` saves as disabled** — When connection test fails, the server is saved with `enabled: false`. Must manually enable.

### Complete fix procedure
```bash
# 1. Create npm global dir if missing
mkdir -p /c/Users/<user>/AppData/Roaming/npm

# 2. Install SF CLI (NEW, not sfdx)
npm install -g @salesforce/cli

# 3. Verify sf works
sf --version

# 4. Verify auth
sf org list

# 5. Install MCP package
npm install -g @salesforce/mcp

# 6. Add to Hermes config
hermes mcp add sf --command npx --args -y @salesforce/mcp --orgs DEFAULT_TARGET_ORG --toolsets all --allow-non-ga-tools

# 7. If connection test fails, manually enable in config.yaml
# Set enabled: true under mcp_servers.sf
```

### If `npx -y @salesforce/mcp` fails with "Could not find file for command: retire"
The npm bin directory has `sf-mcp-server` as the bin entry, not `@salesforce/mcp`. Use the binary directly:
```yaml
mcp_servers:
  sf:
    command: sf-mcp-server
    args:
      - --orgs
      - DEFAULT_TARGET_ORG
      - --toolsets
      - all
      - --allow-non-ga-tools
```

### Finding the installed SF CLI
If winget installed the old sfdx but `sf` is missing:
```bash
# Check winget packages dir
ls /c/Users/madco/AppData/Local/Microsoft/WinGet/Packages/OpenCLICollective.salesforce-cli_Microsoft.Winget.Source_8wekyb3d8bbwe/
# Contains: sfdc.exe (OLD CLI), not sf

# Check npm global bin
ls /c/Users/madco/AppData/Roaming/npm/ | grep sf
# Should show: sf, sf.cmd, sf.ps1, sf-mcp-server, etc.
```
