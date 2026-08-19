# Vapi + Salesforce Integration Pattern

Use when building a Vapi.ai voice agent that needs Salesforce CRM operations.

## Why Not the Official MCP Server?

Vapi expects HTTP function tools (POST endpoints returning JSON). The official `@salesforce/mcp` server uses stdio — incompatible with Vapi's function tool model.

## Architecture

```
Vapi.ai → POST /vapi/tools → Your FastAPI Server → Salesforce REST API
```

## Files

| File | Purpose |
|------|---------|
| `integrations/sf_oauth_client.py` | OAuth2 Authorization Code + Refresh Token |
| `integrations/sf_rest_client.py` | REST wrapper with Vapi tool methods |
| `backend/webhooks/sf_webhook.py` | Vapi webhook endpoint + OAuth callback |
| `config/settings.yaml` | Salesforce credentials |

## Key Steps

1. Create Salesforce Connected App (App Manager → New Connected App)
2. Set callback URL to your tunnel + `/oauth/salesforce/callback`
3. Update config with client_id/client_secret
4. Mount router in FastAPI server
5. Tunnel locally (ngrok or Cloudflare)
6. Start server on port 8000
7. Create Vapi Function Tools pointing to your tunnel URL

## Tunneling

- **Cloudflare Tunnel** (preferred, unlimited): `cloudflared tunnel run <name>`
- **ngrok** (free, 1 tunnel): `ngrok http 8000`
- **Tailscale** (private only): phone accesses `http://100.x.x.x:8000`

## Pitfalls

- OAuth callback must match Connected App exactly (including trailing slash)
- Never commit client_secret — use env vars
- ngrok free tier = 1 tunnel only
- cloudflared winget install doesn't update PATH — download binary directly
