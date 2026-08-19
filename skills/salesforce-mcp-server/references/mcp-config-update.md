# Salesforce MCP Config — How to Update

## The Problem

The `hermes mcp add` CLI **does not exist** — it returns "No such command."
Direct `patch` on `config.yaml` is **blocked** by a security guard (agent cannot write to it).

## Working Paths

### Path 1: Guide the user to edit manually
The user must edit `C:/Users/madco/AppData/Local/hermes/config.yaml` directly:

```yaml
mcp_servers:
  sf:
    command: npx
    args:
      - -y
      - '@salesforce/mcp'
      - --orgs
      - williampullins@gmail.com    # ← your actual org alias, NOT DEFAULT_TARGET_ORG
      - --toolsets
      - all
      - --allow-non-ga-tools
    enabled: true
```

### Path 2: Use `sf` CLI to set the default org first
```bash
sf config set target-org williampullins@gmail.com
```
Then use the org alias (username) as the `--orgs` value.

## Common Mistake

The template `config-salesforce-mcp.yaml` uses `DEFAULT_TARGET_ORG` as a placeholder.
This is a **literal value** — the MCP server will look for an org literally named
`DEFAULT_TARGET_ORG` and fail. Replace it with your actual org alias/username.

## Verification

After updating config:
1. Restart Hermes
2. Check that `mcp_salesforce_*` tools appear in the tool list
3. Test with `sf org list` to confirm auth is working
