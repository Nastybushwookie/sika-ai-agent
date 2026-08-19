---
name: salesforce-vapi-integration
description: Use when building Salesforce + Vapi integrations locally.
version: 1.0.0
author: Hermes Agent
platforms: [windows]
---

# Salesforce + Vapi Integration Skill

## When to Use

Building a Vapi voice agent that calls Salesforce (leads, contacts, accounts, tasks, SOQL queries).

## Architecture (4 files)

| File | Purpose |
|------|---------|
| `integrations/sf_oauth_client.py` | OAuth2 Authorization Code + Refresh Token flow |
| `integrations/sf_rest_client.py` | REST wrapper — record CRUD, SOQL, SOSL, Vapi tool ops |
| `backend/webhooks/sf_webhook.py` | Vapi function tool webhook + OAuth callback |
| `config/settings.yaml` | Salesforce credentials (client_id, client_secret) |

## Quick Start

1. **Create Salesforce Connected App** — App Manager → New Connected App → enable OAuth → capture Consumer Key/Secret.
2. **Set callback URL** to `https://<your-tunnel>/oauth/salesforce/callback`
3. **Update config** with client_id/client_secret in `settings.yaml` under `salesforce:`
4. **Mount router** in `backend/server.py`: `app.include_router(sf_webhook_router)`
5. **Tunnel** (ngrok or Cloudflare) for local dev
6. **Start server**: `uvicorn backend.server:app --port 8000`

## Vapi Function Tools

Webhook URL: `https://<tunnel>/vapi/tools`

Available tools (all snake_case, ≤64 chars):
- `sf_create_lead` — create Lead
- `sf_find_lead_or_contact` — search by email/phone
- `sf_create_task` — create Task
- `sf_log_call_summary` — log call as Task
- `sf_create_contact` — create Contact
- `sf_create_account` — create Account
- `sf_query` — SOQL
- `sf_search` — SOSL
- `sf_auth_url` / `sf_check_auth` / `sf_clear_auth` — auth management

## Tunnel Options

### Cloudflare Tunnel (free, unlimited tunnels) — Preferred
```bash
# Install — winget MSI doesn't update PATH
curl -L -o C:/Users/madco/cloudflared.exe "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe"

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create <name>

# Set DNS route
cloudflared tunnel route dns <name> <subdomain>.<domain>

# Start tunnel
cloudflared tunnel run <name>
```

### ngrok (free, 1 tunnel only)
```bash
ngrok http 8000
curl -s http://127.0.0.1:4040/api/tunnels | grep public_url
```
**Limitation**: Free tier = 1 tunnel. Use Cloudflare when you need Vapi + LM Studio simultaneously.

### Tailscale (private network)
- Only useful if Vapi can reach your Tailscale network (not typical)
- Your computer's Tailscale IP → phone accesses `http://100.x.x.x:8000`

## Token Storage

Tokens saved to `integrations/.data/sf_tokens.json` by default. Override via `token_file` in config.

## Common Pitfalls

- **401 after first call**: Token expires in ~1 hour. The REST client auto-refreshes if refresh_token exists.
- **OAuth callback mismatch**: Callback URL in Connected App must exactly match the tunnel URL + `/oauth/salesforce/callback`
- **ngrok free tier**: Only 1 tunnel. Kill one to start the other.
- **Cloudflare domain required**: Can't create routes without a domain on Cloudflare.
- **Sandbox vs Production**: Use `https://test.salesforce.com` for sandbox orgs.