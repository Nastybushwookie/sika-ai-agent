---
name: salesforce-mcp-integration
description: "Set up and configure MCP servers for Salesforce — official salesforcecli/mcp server, hosted MCP servers, Composio Salesforce toolkits, and Hermes Agent integration patterns."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [salesforce, mcp, integration, agentforce, api, tooling]
---

# Salesforce MCP Integration — Complete Guide

## Overview

Salesforce has released a **GA MCP server** that provides native tool access for AI agents. This eliminates the need for manual REST API calls and token management.

## Official Salesforce MCP Server (GA)

### Repository
- **URL**: `salesforcecli/mcp` (GitHub)
- **Covers**: SObject CRUD, Flows, Invocable Apex, Apex REST, Data 360, Tableau
- **Status**: Generally Available (GA)

### Setup (Hosted — Easiest)
1. Log into Salesforce Setup
2. Navigate to **Integration → Salesforce MCP Servers**
3. Configure OAuth 2.0 connection
4. No code required — one-time config

### Setup (Self-Hosted)
```bash
# Install from salesforcecli repository
sf mcp install salesforcecli/mcp

# Or clone and configure manually
git clone https://github.com/salesforcecli/mcp
cd mcp
# Follow setup instructions for your environment
```

### Hermes Agent Configuration
```json
{
  "mcpServers": {
    "salesforce": {
      "command": "sf",
      "args": ["mcp", "serve"]
    }
  }
}
```

## Composio Salesforce MCP Toolkits

Composio offers Hermes-optimized Salesforce MCP toolkits:

| Toolkit | Scope | Best For |
|---------|-------|----------|
| `salesforce` | Core CRM (accounts, contacts, opportunities, cases) | General CRM operations |
| `salesforce_service_cloud` | Case management, knowledge base, omni-channel | Support teams |

### Setup via CLI
```bash
# Install Composio
composio add salesforce

# Start MCP server
composio mcp start
```

### Setup via MCP (Alternative)
```bash
# Install Composio Connect MCP
composio connect mcp --toolkit salesforce
```

## Hosted MCP vs Self-Hosted

| Feature | Hosted (Salesforce) | Self-Hosted |
|---------|---------------------|-------------|
| Config | Zero code, OAuth in Setup | Requires setup |
| Auth | OAuth 2.0 automatic | Manual token management |
| Offline | No (requires Salesforce connection) | Yes |
| Control | Salesforce-managed | Full control |
| Best for | Demos, quick setup | Production, offline needs |

## Common Pitfalls

### Auth Token Expiration
**Never** read access tokens from `~/.sfdx/<username>.json` for use in Python scripts or external tools. The token expires between the CLI auth command and script execution.

**Fix**: Always use `sf` CLI commands directly — they handle auth internally:
```bash
# RIGHT — use sf CLI directly
sf org list
sf project deploy start
sf data query --query "SELECT Id, Name FROM Account"
```

### Developer Edition Limitations
Before deploying to a Developer Edition:
- Custom object limit: ~10 objects
- Apex deployment may show "Not available for deploy for this organization"
- Use Sandbox or Scratch Org for full deployment

## Integration Tiers for Demos

### Tier 1 — High Impact
- Vapi.ai (voice AI)
- Twilio (SMS/voice)
- Slack (Customer 360)
- Tableau (live dashboards)
- DocuSign (eSignature)
- Stripe (payments)

### Tier 2 — Strong Differentiators
- HubSpot, QuickBooks, Jira, Zoom, Google Workspace, Microsoft 365, Zendesk, GitHub

### Tier 3 — Niche Power Players
- ServiceNow, Workday, Snowflake, Shopify, Calendly, Mailchimp, WooCommerce

## MCP Server Management (Agentforce)

```bash
# Create MCP server in API Catalog
sf agent mcp create --name myServer --server-url https://mcp.example.com --target-org myOrg

# List registered MCP servers
sf agent mcp list --status ACTIVE

# Fetch live assets from MCP server
sf agent mcp fetch --mcp-server-id 0XSxx0000000001 --target-org myOrg

# List assets (tools, prompts, resources)
sf agent mcp asset list --mcp-server-id 0XSxx0000000001 --target-org myOrg
```

## Key Resources

| Resource | URL |
|----------|-----|
| Official MCP Server | https://github.com/salesforcecli/mcp |
| Install & Configure Guide | https://developer.salesforce.com/docs/atlas.en-us.sfdx_dev.meta/sfdx_dev/sfdx_dev_mcp_server.htm |
| Hosted MCP Setup | https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/setup-overview.html |
| Custom Servers | https://developer.salesforce.com/docs/platform/hosted-mcp-servers/guide/custom-servers.html |
| Salesforce MCP vs REST API | https://www.scalekit.com/blog/salesforce-mcp-vs-api |
| Composio Salesforce | https://composio.dev/toolkits/salesforce/framework/hermes-agent |
