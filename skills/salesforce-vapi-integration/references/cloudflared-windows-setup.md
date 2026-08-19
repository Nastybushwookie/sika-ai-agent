# Cloudflared Windows Setup

## Install
```bash
winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
```

## Authenticate
```bash
cloudflared login
```
Opens browser — click "Allow" to authorize Cloudflare account.

## Create Tunnel
```bash
cloudflared tunnel create sika-agent
```
Creates tunnel ID + config in `~/.cloudflared/`.

## Configure Routes
Edit `~/.cloudflared/<tunnel-id>.yaml`:
```yaml
tunnel: <tunnel-id>
credentials-file: C:/Users/madco/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: sf.sika-agent.example.com
    service: http://localhost:8000
  - hostname: lm.sika-agent.example.com
    service: http://localhost:1234
  - service: http_status:404
```

## Start Tunnel
```bash
cloudflared tunnel run sika-agent
```

## Public URLs
- `https://sf.sika-agent.example.com` → Vapi webhook (port 8000)
- `https://lm.sika-agent.example.com` → LM Studio (port 1234)

## Notes
- Free tier = unlimited tunnels
- Requires a domain on Cloudflare
- DNS records created automatically on first run
- Run as background process for production use
