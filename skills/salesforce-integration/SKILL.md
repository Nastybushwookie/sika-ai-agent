---
name: salesforce-integration
description: "Use when building Salesforce integrations for AI agents."
version: 1.0.0
author: Hermes Agent + User (William Pulins)
platforms: [windows, linux, macos]
metadata:
  tags: [salesforce, oauth2, rest-api, vapi, webhook, connected-app, sika-agent]
---

# Salesforce Integration Patterns

## Overview

Patterns for building Salesforce connections for AI voice agents (Vapi.ai), including OAuth2 setup, REST API client, Vapi function tool webhooks, and tunneling for local development.

## Architecture

```
Vapi.ai Function Tool → Webhook → Your Server → Salesforce REST API
         ↓                                    ↓
    Tool Results                        Auth + Data Ops
```

## Step 1: Create Salesforce Connected App

In Salesforce Setup → App Manager → New Connected App:

| Setting | Value |
|---------|-------|
| Enable OAuth | Yes |
| Callback URL | `https://<YOUR_DOMAIN>/oauth/salesforce/callback` |
| OAuth Scopes | `openid`, `api`, `refresh_token` |

Capture: **Consumer Key** (client_id) and **Consumer Secret** (client_secret)

Note your org type:
- Production: `https://login.salesforce.com`
- Sandbox: `https://test.salesforce.com`
- My Domain: use your custom URL

## Step 2: OAuth2 Flow

### Authorization Code + Refresh Token

**Step A — Redirect to authorize:**
```
GET {base}/services/oauth2/authorize
  ?response_type=code
  &client_id=...
  &redirect_uri=...
  &scope=api refresh_token openid
  &state=...
```

**Step B — Exchange code for tokens:**
```
POST {base}/services/oauth2/token
  grant_type=authorization_code
  code=...
  client_id=...
  client_secret=...
  redirect_uri=...
```

**Step C — Refresh tokens when expired:**
```
POST {base}/services/oauth2/token
  grant_type=refresh_token
  refresh_token=...
  client_id=...
  client_secret=...
```

## Step 3: REST API Calls

Base URL: `{instance_url}/services/data/v60.0/`

Common endpoints:
- `POST /sobjects/{Object}/` — Create record
- `GET /sobjects/{Object}/{id}` — Get record
- `PATCH /sobjects/{Object}/{id}` — Update record
- `DELETE /sobjects/{Object}/{id}` — Delete record
- `GET /query?q=SELECT ...` — SOQL query
- `GET /search?q=FIND ...` — SOSL search

Headers:
- `Authorization: Bearer {access_token}`
- `Content-Type: application/json`

## Step 4: Vapi Function Tool Webhook

Your server needs a `/vapi/tools` endpoint that:
1. Receives tool calls from Vapi
2. Dispatches to the appropriate Salesforce operation
3. Returns results in Vapi's expected shape:

```json
{
  "results": [
    {
      "toolCallId": "the-tool-call-id",
      "result": { "ok": true, "data": "..." }
    }
  ]
}
```

## Step 5: Tunneling for Local Dev

Use Cloudflare Tunnel (free, unlimited tunnels) for local development:
```bash
cloudflared tunnel create <name>
cloudflared tunnel route dns <name> <subdomain.domain.com>
cloudflared tunnel run <name>
```

ngrok free tier = one tunnel per account. Use Cloudflare Tunnel when you need multiple (Vapi webhook + LM Studio simultaneously).

## Recommended Vapi Tools

| Tool Name | Purpose |
|-----------|---------|
| `sf_create_lead` | Create a Lead |
| `sf_find_lead_or_contact` | Search by email/phone |
| `sf_create_task` | Create a Task |
| `sf_log_call_summary` | Log call as Task |
| `sf_create_contact` | Create a Contact |
| `sf_create_account` | Create an Account |
| `sf_query` | Execute SOQL |
| `sf_search` | Execute SOSL |
| `sf_auth_url` | Get OAuth URL |
| `sf_check_auth` | Check auth status |

## Pitfalls

- **Never read tokens from `~/.sfdx/<username>.json`** — INVALID_AUTH_HEADER expires immediately. Use the SF CLI directly or store tokens in a file.
- **Dev Edition limits** — ~10 custom objects, restricted Apex. Check capacity before deploying custom objects.
- **Token refresh** — Always check token expiry before API calls; refresh automatically on 401.
- **Tunneling** — ngrok free = 1 tunnel. Cloudflare Tunnel = unlimited. Use Cloudflare for multi-service setups.

## Reference Files

See `references/` directory for:
- Connected App setup checklist
- Vapi webhook payload examples
- Salesforce REST API quick reference