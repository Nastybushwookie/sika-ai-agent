---
name: salesforce-mcp
description: "Salesforce MCP server patterns — use the official @salesforce/mcp server as default, configure it, and know when to build custom. Covers toolsets, flags, troubleshooting, and integration with Hermes Agent."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      - salesforce
      - mcp
      - salesforce-mcp-server
      - agentforce
---

# Salesforce MCP Server Patterns

## Default Answer: Use the Official Server

**Before considering building a custom Salesforce MCP server, always check the official `@salesforce/mcp` server first.** It is production-ready (v0.30.15, 252+ releases, 60+ tools, actively maintained by Salesforce).

Building from scratch would require rebuilding years of Salesforce engineering work. Only build custom when you need capabilities the official server cannot provide.

## Configuring the Official Server

### Hermes Agent (stdio via npx)
```yaml
mcp_servers:
  sf:
    command: "npx"
    args:
      - "-y"
      - "@salesforce/mcp@latest"
      - "--orgs"
      - "DEFAULT_TARGET_ORG"
      - "--toolsets"
      - "all"
      - "--allow-non-ga-tools"
    timeout: 180
    connect_timeout: 60
```

### Claude Code
```json
{
  "mcpServers": {
    "Salesforce DX": {
      "command": "npx",
      "args": ["-y", "@salesforce/mcp@latest",
               "--orgs", "DEFAULT_TARGET_ORG",
               "--toolsets", "all",
               "--allow-non-ga-tools"]
    }
  }
}
```

## Toolsets (select only what you need)

| Toolset | Purpose | Key Tools |
|---------|---------|-----------|
| `core` | Always enabled | `get_username`, `resume_tool_operation` |
| `data` | Data operations | `run_soql_query` |
| `metadata` | Deploy/retrieve | `deploy_metadata`, `retrieve_metadata` |
| `orgs` | Org management | `list_all_orgs`, `create_scratch_org`, `delete_org`, `open_org` |
| `users` | User management | `assign_permission_set` |
| `testing` | Testing | `run_apex_test`, `run_agent_test` |
| `lwc-experts` | LWC development | 30+ tools for LWC dev, testing, optimization |
| `code-analysis` | Static analysis | Security scanning, best practices |
| `aura-experts` | Aura migration | Aura-to-LWC migration tools |
| `devops` | DevOps Center | Pipeline tools |

## Configuration Flags

| Flag | Required | Description |
|------|----------|-------------|
| `--orgs` | YES | Orgs to authorize: `DEFAULT_TARGET_ORG`, `ALLOW_ALL_ORGS`, or specific alias |
| `--toolsets` | No | Comma-separated toolsets. Default: `core`. Use `all` for everything. |
| `--tools` | No | Individual tool names (can combine with --toolsets) |
| `--allow-non-ga-tools` | No | Enable NON-GA tools |
| `--debug` | No | Print debug logs |
| `--dynamic-tools` | No | (experimental) Load tools on demand |
| `--no-telemetry` | No | Disable telemetry |

## Troubleshooting

- **Tools not appearing**: Check `--toolsets` flag; default is `core` only (2 tools). Enable `data` for SOQL, etc.
- **Auth errors**: Verify `sf org list` shows connected orgs first. The server reads from existing sf CLI auth.
- **Node.js required**: Must be Node 20+. Check with `node --version`.
- **Context overload**: 60+ tools can overwhelm the LLM — prefer selecting specific toolsets.
- **NON-GA tools**: `create_scratch_org`, `delete_org`, `open_org` need `--allow-non-ga-tools`.

## Adding to Hermes Config — Important

**The `config.yaml` is protected against automated edits.** You cannot use `patch` or `write_file` on the config file directly. You also cannot use `hermes config set` for nested paths like `auxiliary.mcp.servers.*` — it will warn that the key is unrecognized.

**Correct approach:**
1. Run `hermes config edit` to open the file in your editor
2. Manually add the MCP server under `auxiliary.mcp.servers`
3. Or use the `hermes mcp add` CLI (may time out on Windows)

**Example config entry:**
```yaml
  mcp:
    servers:
      sf:
        command: npx
        args:
          - -y
          - @salesforce/mcp@latest
          - --orgs
          - DEFAULT_TARGET_ORG
          - --toolsets
          - all
          - --allow-non-ga-tools
        timeout: 180
        connect_timeout: 60
```

**After adding:** Restart the gateway or start a new session (`/reset`) for tools to appear.

## When to Build Custom

Only build a custom Salesforce MCP server when:
1. You need tools the official server cannot provide (e.g., specialized integrations)
2. You need to run without Node.js dependency
3. You need to modify the official server's behavior (fork it)

### Concrete Example: Vapi Voice Agent Integration

When building a Vapi.ai voice agent that needs Salesforce CRM operations, the official MCP server won't work because Vapi expects HTTP function tools, not MCP stdio servers. Build a custom integration using the `salesforce-vapi-integration` skill.

See `references/vapi-integration-pattern.md`.

## References

- `references/salesforce-dx-mcp-server.md` — Full tool list and quick config
- Repo: https://github.com/salesforcecli/mcp
- Docs: https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_mcp_server.htm