---
name: salesforce-mcp-server
description: "Set up, configure, and troubleshoot the Salesforce DX MCP Server (@salesforce/mcp) for local AI agent integration with Salesforce orgs."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [salesforce, mcp, dx, server, integration, ai-agents]
---

# Salesforce DX MCP Server — Setup & Configuration

## Overview

The **Salesforce DX MCP Server** (`@salesforce/mcp`) is the official npm package that provides a local MCP server for interacting with Salesforce orgs. It gives Hermes Agent (and any other MCP client) native access to Salesforce data, metadata, and operations.

**Key advantage**: Uses existing `sf` CLI authentication — no separate Connected App, OAuth flow, or client ID/secret management needed.

## Quick Setup

### 1. Install the SF CLI (required first)

**Windows — critical distinction:** `winget install OpenCLICollective.salesforce-cli` installs the OLD `sfdx` CLI (sfdc.exe), NOT the new `sf` CLI. You must install the new CLI separately:

```bash
npm install -g @salesforce/cli
```

Verify:
```bash
sf --version
# Should show: @salesforce/cli/2.x.x win32-x64 node-v...
```

If `npm install -g` fails with ENOENT on `AppData/Roaming/npm`, create the directory first:
```bash
mkdir -p /c/Users/<user>/AppData/Roaming/npm
```

### 2. Install the MCP Package
```bash
npm install -g @salesforce/mcp
```

Verify:
```bash
npm list -g @salesforce/mcp
# Should show: @salesforce/mcp@x.x.x
```

### 3. Verify SF CLI Auth
```bash
sf org list
# Must show your org as "Connected"
```

**Critical**: The MCP server reads auth from `~/.sfdx/<username>.json`. If `sf org list` shows no connected orgs, the MCP server will fail.

### 3. Add to Hermes Config

**The `hermes mcp add` CLI does NOT exist** — it returns "No such command."
Direct `patch` on `config.yaml` is **blocked** by a security guard.

**Working path: Guide the user to edit `~/.hermes/config.yaml` manually.**

See `references/mcp-config-update.md` for the complete procedure.

**Critical:** `--orgs` must be your **actual org alias/username** from `sf org list` — NOT `DEFAULT_TARGET_ORG` (which is a placeholder, not a real value). The MCP server will look for an org literally named `DEFAULT_TARGET_ORG` and fail.

**Restart Hermes** after adding the config — MCP servers are discovered at startup only.

## Toolsets

| Toolset | Description | Key Tools |
|---------|-------------|-----------|
| `core` | Core DX tools (always enabled) | `get_username`, `resume_tool_operation` |
| `data` | Data management | `run_soql_query` |
| `orgs` | Org management | `list_all_orgs`, `create_scratch_org`, `delete_org` |
| `metadata` | Metadata deploy/retrieve | `deploy_metadata`, `retrieve_metadata` |
| `testing` | Test execution | `run_agent_test`, `run_apex_test` |
| `users` | User management | `assign_permission_set` |
| `mobile` | Mobile LWC development | 13 mobile LWC tools |
| `mobile-core` | Mobile core subset | `get_mobile_lwc_offline_analysis`, `get_mobile_lwc_offline_guidance` |
| `all` | Every tool in every toolset | Use sparingly — 60+ tools can overwhelm LLM context |

## Key Flags

| Flag | Description |
|------|-------------|
| `--orgs <value>` | **Required.** Which orgs to authorize. Values: `ALLOW_ALL_ORGS`, `DEFAULT_TARGET_ORG`, `DEFAULT_TARGET_DEV_HUB`, or `<username/alias>` |
| `--toolsets <value>` | Which toolsets to enable. Comma-separated. Default: `core` only. Use `all` to enable everything. |
| `--tools <value>` | Individual tools to enable (can combine with `--toolsets`). |
| `--allow-non-ga-tools` | Enable non-GA (preview) tools. |
| `--debug` | Print debug logs. |
| `--no-telemetry` | Disable telemetry. |
| `--dynamic-tools` | (experimental) Enable dynamic tool discovery to reduce initial context size. |

## Tool Naming Convention

Tools are registered with prefix `mcp_salesforce_<tool_name>`:
- `mcp_salesforce_run_soql_query`
- `mcp_salesforce_deploy_metadata`
- `mcp_salesforce_retrieve_metadata`
- `mcp_salesforce_run_apex_test`
- `mcp_salesforce_list_all_orgs`
- `mcp_salesforce_assign_permission_set`

## Troubleshooting

### "MCP SDK not available"
```bash
pip install mcp
```

### "No MCP servers configured"
Check `~/.hermes/config.yaml` has `mcp_servers` key with at least one entry.

### "Failed to connect to MCP server 'salesforce'"
1. Verify `sf org list` shows your org as Connected
2. Verify `npx -y @salesforce/mcp --help` works
3. Check `npm list -g @salesforce/mcp` shows the package installed
4. Verify the org has sufficient permissions (Developer Edition, Sandbox, or Trial orgs work best)

### "Tools not appearing"
- Check server is under `mcp_servers` (not `mcp` or `servers`)
- Verify YAML indentation
- Look at Hermes startup logs for connection messages
- Tools are prefixed `mcp_{server}_{tool}` — look for `mcp_salesforce_*`

### "Connection keeps dropping"
Retries up to 5 times with exponential backoff (1s, 2s, 4s, 8s, 16s, capped at 60s). If still failing, check server process and network connectivity.

## Pitfalls

- **Auth token expiration**: Python scripts reading tokens from `~/.sfdx/*.json` fail because tokens expire between CLI login and script execution. The MCP server approach avoids this by using `sf` CLI auth directly.
- **Developer Edition limits**: Custom object limit ~10, Apex deployment restricted in some org types. Use Sandbox or Scratch Org for full deployment.
- **Restart required**: Adding/removing MCP servers requires restarting the agent — no hot-reload.
- **Tool count**: Enabling `--toolsets all` registers 60+ tools that can overwhelm LLM context. Prefer specific toolsets.

## References

- [Official Docs](https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_mcp_server.htm)
- [GitHub](https://github.com/salesforcecli/mcp)
- [npm package](https://www.npmjs.com/package/@salesforce/mcp)
- [Release notes](https://github.com/forcedotcom/mcp/tree/main/releasenotes)

## Support Files

- `templates/config-salesforce-mcp.yaml` — Ready-to-use config snippet
- `references/known-issues.md` — Known issues and workarounds
- `references/sf-cli-wrapper-fix.md` — Fix for broken SF CLI wrapper (missing node_modules)
- `references/windows-sf-mcp-troubleshooting.md` — Windows-specific SF CLI + MCP setup diagnosis and fix
- `references/regular-org-user-creation.md` — How to create users in regular (non-scratch) orgs via `sf data create record`
- `references/sf-mcp-http-wrapper.md` — SF MCP HTTP wrapper project details and API reference
- `references/email-verification-fallback.md` — Raw Node.js TLS IMAP fallback when Himalaya CLI is unavailable
- `references/sf-mcp-http-wrapper-operational-check.md` — Quick verification steps, common pitfalls (port 3001, POST not GET, 90s timeout)
