---
name: salesforce-auth
description: "Salesforce authentication patterns — OAuth flows, token management, Connected Apps, security settings, and auth troubleshooting for AI agents and CI/CD."
version: 1.0.0
author: Hermes Agent
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags:
      - salesforce
      - authentication
      - oauth
      - security
      - connected-app
---

# Salesforce Authentication Patterns

## Authentication Overview

Salesforce uses OAuth 2.0 for authentication. Key flows:
- **Web Server Flow** (Authorization Code): Interactive login, refresh tokens
- **Username-Password Flow**: Automated auth, requires trusted IP ranges
- **JWT Bearer Flow**: Server-to-server, no user interaction
- **Refresh Token Flow**: Re-authenticate with existing refresh token

## sf CLI Authentication

### Standard Login (Web OAuth)
```bash
# Interactive login — opens browser for OAuth
sf org login web --alias sika-dev

# Dev Hub login (required for scratch orgs)
sf org login web --devhub --alias devhub

# Login to specific instance
sf org login web --instance-url https://login.salesforce.com --alias prod
```

### Username-Password Login (Automation)
```bash
# For CI/CD or automation (requires trusted IP ranges)
sf org login username \
  --username USERNAME \
  --password PASSWORD \
  --callback-url http://localhost:1717/ \
  --alias automation

# With security token
sf org login username \
  --username USERNAME \
  --password PASSWORD+SECURITY_TOKEN \
  --callback-url http://localhost:1717/
```

### SFDX URL Login (Token-based)
```bash
# Login using an existing SFDX URL (includes access token)
sf auth sfdx-url login --sfdx-url "https://login.salesforce.com/id/ORG_ID/USER_ID?access_token=ACCESS_TOKEN&instance_url=https://orgfarm-4344f57ecf.my.salesforce.com"

# Useful for sharing auth between machines or CI/CD
```

### Using Existing Access Token
```bash
# When you have an access token but no full CLI auth
# Set environment variables:
export SF_TARGET_ORG_INSTANCE_URL="https://orgfarm-4344f57ecf.my.salesforce.com"
export SF_TARGET_ORG_ACCESS_TOKEN="ACCESS_TOKEN"

# Then use sf commands — they'll use these env vars
sf org display --target-org williampullins@gmail.com
```

## Auth Management

### Check Auth Status
```bash
# List all authenticated orgs
sf org list

# Show detailed auth info
sf org auth show --target-org williampullins@gmail.com

# Show access token
sf org auth show-access-token --target-org williampullins@gmail.com

# Check if org is still valid
sf org display --target-org williampullins@gmail.com --json
# Look for "connectedStatus": "Connected"
```

### Refresh/Revoke Auth
```bash
# Refresh token (extends expiry)
sf auth refresh -t williampullins@gmail.com

# Revoke/unauthorize org
sf auth revoke -t williampullins@gmail.com

# Set default org
sf org set default --target-org williampullins@gmail.com

# Remove default org
sf org set default --unset
```

## Connected App Setup

### Creating a Connected App
```
1. Setup → App Manager → New Connected App
2. Fill in:
   - Connected App Name: Sika AI Agent
   - API Name: Sika_AI_Agent
   - Contact Email: your@email.com
3. Enable OAuth Settings:
   - Callback URL: https://YOUR_DOMAIN/oauth/callback
   - Selected OAuth Scopes:
     * access_and_manage_permissions
     * refresh_token, offline
     * api (REST API)
     * web (Web and Mobile)
     * id (Identity)
4. Generate Consumer Key and Secret
5. Save
```

### OAuth Scopes Reference
| Scope | Purpose |
|-------|---------|
| `api` | REST API access |
| `web` | Web and Mobile login |
| `refresh_token` | Offline access (refresh tokens) |
| `id` | Identity (user info) |
| `email` | User email address |
| `offline` | Offline access |
| `full` | Full access (all scopes) |
| `custom_permissions` | Custom permissions |

### Connected App Security Settings
```
- IP Relaxation: Enable for trusted networks
- Profile Assignment: Assign to specific profiles
- Permitted Users: Admin approved users / All users may self-authorize
- OAuth Policies:
  - Enable Deep Linking: Yes (for mobile)
  - Enable PKCE: Yes (recommended)
  - Session Timeout: 60 minutes (recommended)
```

## OAuth Flow for AI Agents

### Authorization Code Flow (Interactive)
```bash
# 1. Build authorization URL
AUTH_URL="https://login.salesforce.com/services/oauth2/authorize"
AUTH_URL+="?response_type=code"
AUTH_URL+="&client_id=YOUR_CONSUMER_KEY"
AUTH_URL+="&redirect_uri=https://YOUR_DOMAIN/oauth/callback"
AUTH_URL+="&scope=api refresh_token web"
AUTH_URL+="&state=CSRF_TOKEN"

# 2. User opens AUTH_URL in browser
# 3. User authorizes → redirected to callback with code
# 4. Exchange code for tokens:
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "code=AUTH_CODE" \
  -d "redirect_uri=https://YOUR_DOMAIN/oauth/callback"

# Response:
# {
#   "access_token": "ACCESS_TOKEN",
#   "instance_url": "https://orgfarm-4344f57ecf.my.salesforce.com",
#   "refresh_token": "REFRESH_TOKEN",
#   "signature": "SIG",
#   "scope": "api web refresh_token",
#   "id": "https://login.salesforce.com/id/ORG/USER",
#   "token_type": "Bearer"
# }
```

### Refresh Token Flow (Non-Interactive)
```bash
# Use refresh token to get new access token
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=refresh_token" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "refresh_token=REFRESH_TOKEN"

# Response:
# {
#   "access_token": "NEW_ACCESS_TOKEN",
#   "instance_url": "https://orgfarm-4344f57ecf.my.salesforce.com",
#   "issued_at": "1234567890",
#   "signature": "SIG",
#   "scope": "api web refresh_token",
#   "token_type": "Bearer"
# }
```

### JWT Bearer Flow (Server-to-Server)
```bash
# Generate JWT assertion
# 1. Create JWT with header and payload
# 2. Sign with Connected App's public key
# 3. Exchange JWT for access token
curl -X POST https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer" \
  -d "assertion=JWT_ASSERTION" \
  -d "client_id=YOUR_CONSUMER_KEY"
```

## Token Management for AI Agents

### Storing Tokens Securely
```bash
# In .env file (never commit to git):
SF_ACCESS_TOKEN=ACCESS_TOKEN
SF_INSTANCE_URL=https://orgfarm-4344f57ecf.my.salesforce.com
SF_CLIENT_ID=YOUR_CONSUMER_KEY
SF_CLIENT_SECRET=YOUR_CONSUMER_SECRET
SF_REFRESH_TOKEN=REFRESH_TOKEN

# In settings.yaml (use placeholders):
salesforce:
  base_url: "https://login.salesforce.com"
  client_id: "${SF_CLIENT_ID}"
  client_secret: "${SF_CLIENT_SECRET}"
  token_file: null  # Path to stored token file
```

### Token Expiry Handling
```python
# Token expiry times:
# - Access Token: 2 hours (default) or 24 hours (with refresh_token scope)
# - Refresh Token: 180 days (if "refresh_token" scope granted)
# - Session Timeout: 30 min to 12 hours (org settings)

# Check token validity:
# 1. Store token creation timestamp
# 2. Before API call, check if token is < 1 hour old
# 3. If expired, use refresh_token to get new access_token
# 4. If refresh_token expired, re-authenticate

def get_valid_token():
    if is_token_expired(access_token, 3600):  # 1 hour buffer
        new_token = refresh_access_token(refresh_token)
        access_token = new_token['access_token']
        refresh_token = new_token.get('refresh_token', refresh_token)
    return access_token
```

## Auth Troubleshooting

### Common Errors
| Error | Cause | Fix |
|-------|-------|-----|
| `INVALID_SESSION_ID` | Token expired/revoked | Refresh token or re-auth |
| `INSUFFICIENT_ACCESS` | No permission for object/field | Assign profile/permission set |
| `UNABLE_LOCK_ROW` | Concurrent access | Retry with backoff |
| `MAX_QUERY_LENGTH` | SOQL too long | Split queries, use LIMIT |
| `CANNOT_INSERT_UPDATE_ACTIVATE_ENTITY` | Trigger error | Check trigger logic |
| `INVALID_LOGIN` | Wrong credentials/IP | Check IP whitelist, credentials |
| `IP_RESTRICTION` | IP not whitelisted | Add IP to Connected App |
| `CONNECTION_TIMEOUT` | Network issue | Retry, check firewall |

### Debugging Auth Issues
```bash
# 1. Check if org is still connected
sf org list

# 2. Check auth details
sf org auth show --target-org williampullins@gmail.com

# 3. Check access token
sf org auth show-access-token --target-org williampullins@gmail.com

# 4. Try re-authorizing
sf auth revoke -t williampullins@gmail.com
sf org login web --alias williampullins@gmail.com

# 5. Check connected status
sf org display --json --target-org williampullins@gmail.com
# Look for "connectedStatus": "Connected"
```

### IP Whitelist for Connected Apps
```
1. Setup → App Manager → Connected App → Edit
2. OAuth Policies → IP Relaxation: Enable
3. Or add specific IP ranges to "IP Relaxation"
4. For production: Add production server IPs to "Permitted Users"
5. Test with: curl -I https://login.salesforce.com/services/oauth2/token
```

## Security Best Practices

### Token Security
1. **Never commit tokens to git** — use environment variables or secrets management
2. **Rotate tokens regularly** — at least every 90 days
3. **Use minimum scopes** — only request scopes you need
4. **Enable PKCE** — prevents authorization code interception
5. **Set session timeouts** — 60 minutes recommended
6. **Use IP restrictions** — limit access to trusted networks

### Connected App Security
1. **Assign to specific profiles** — not "All users"
2. **Enable OAuth policies** — PKCE, session timeout
3. **Monitor OAuth logins** — Setup → Security → OAuth App Access Audit
4. **Use separate Connected Apps** — dev vs prod
5. **Revoke unused apps** — cleanup regularly

### API Security
1. **Use HTTPS only** — never HTTP for API calls
2. **Rate limiting** — respect Salesforce API limits
3. **Batch operations** — use Bulk API for large datasets
4. **Cache tokens** — don't re-authenticate on every request
5. **Monitor API usage** — Setup → Security → API Usage

## References
- OAuth 2.0: https://developer.salesforce.com/docs/atlas.en-us.noversion.api_meta.meta/api_meta/auth_oauth_using_connected_app.htm
- JWT Bearer: https://developer.salesforce.com/docs/atlas.en-us.noversion.api_meta.meta/api_meta/auth_oauth_jwt.htm
- API Limits: https://developer.salesforce.com/docs/atlas.en-us.noversion.api_meta.meta/api_meta/api_limits.htm
- Security Best Practices: https://developer.salesforce.com/docs/atlas.en-us.noversion.security_manual.meta/security_manual/connect_oauth_jwt.htm
