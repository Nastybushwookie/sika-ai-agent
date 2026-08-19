# Salesforce DX MCP Server — Known Issues & Workarounds

## Session-Specific Issues (2026-07-25)

### Issue 1: Python Script Auth Token Expiration
**Symptom**: Python scripts reading tokens from `~/.sfdx/williampullins@gmail.com.json` fail with `INVALID_AUTH_HEADER` error.

**Root Cause**: The access token expires between the `sf org login web` command and the Python script execution. The token in the JSON file becomes stale.

**Workaround**: Use the `sf` CLI directly instead of Python scripts with raw tokens. The MCP server approach avoids this entirely by using the CLI's internal auth management.

**Fix**: Always re-authenticate with `sf org login web` before running any Python scripts that use the token. Or better — use the MCP server which manages auth automatically.

### Issue 2: Developer Edition Deployment Limits
**Symptom**: "Not available for deploy for this organization" errors when deploying Apex classes/triggers.

**Root Cause**: Developer Edition has restrictions on Apex deployment via Metadata API.

**Workaround**: Use a Sandbox or Scratch Org for full deployment. The Developer Edition is suitable for demos and learning but has deployment restrictions.

**Custom Object Limit**: Developer Edition has a ~10 custom object limit. We hit this with 5 objects (within limit).

### Issue 3: SF CLI Command Syntax Changes
**Symptom**: `sf org set-default` and `sf org login username` commands not found.

**Root Cause**: This version of sf CLI (v2.144.6) has different command names than documented in older tutorials.

**Fix**: Use `sf org login web` for interactive auth. The `--set-default` flag works with login commands.

## General Issues

### Tool Discovery Timeout
The MCP server can take 30+ seconds to start and register all tools. If using `--toolsets all`, expect longer startup times due to 60+ tool registrations.

### Missing `--help` on Some Commands
`sf mcp --help` may show a picker menu instead of help text. Use `sf help mcp` or check the official docs.

### Deprecated Glob Warnings
npm install shows deprecation warnings for `glob`, `rimraf`, `inflight`, etc. These are transitive dependencies and do not affect functionality.
