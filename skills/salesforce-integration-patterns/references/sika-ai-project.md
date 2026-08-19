# Sika Corp AI Agent — Architecture Reference

Concrete example of a FastAPI + Salesforce + ServiceNow + Telephony project.

## Project Layout

```
sika-ai-agent/
├── backend/
│   ├── server.py              # FastAPI app, webhook handlers
│   ├── decision_tree_engine.py # JSON decision tree engine
│   └── webhooks/sf_webhook.py # Salesforce tool router
├── integrations/
│   ├── sf_oauth_client.py     # Salesforce OAuth2 (Authorization Code + Refresh)
│   ├── sf_rest_client.py      # Salesforce REST API wrapper
│   └── snow_oauth_client.py   # ServiceNow OAuth2 client
├── telephony/
│   ├── interface.py           # TelephonyProvider ABC + TelephonyAdapterFactory
│   ├── ringcentral_provider.py
│   ├── twilio_provider.py
│   └── vai_provider.py
├── trees/                     # JSON decision tree definitions
├── config/settings.yaml       # Environment config (no auto-expansion)
└── scripts/                   # Audit/rate-limit/logging utilities
```

## Key Files

| File | Purpose |
|------|---------|
| `backend/server.py` | FastAPI app, `/vapi/webhook`, `/twilio/webhook`, `/api/incidents/create` |
| `backend/decision_tree_engine.py` | JSON-driven troubleshooting trees (no ML) |
| `integrations/sf_oauth_client.py` | SFOAuthClient + SFTokenStore (file-backed, 60s early expiry) |
| `integrations/sf_rest_client.py` | SFRestClient — SOQL/SOSL, leads, contacts, accounts, tasks |
| `integrations/snow_oauth_client.py` | ServiceNow OAuth2 (client_credentials flow) |
| `telephony/interface.py` | TelephonyProvider ABC + TelephonyAdapterFactory |

## Config Pattern (settings.yaml)

```yaml
environment: development
servicenow:
  base_url: "https://sikanow.sika.com"
  client_id: "${SNOW_CLIENT_ID}"      # NOT auto-expanded — use os.environ.get()
  client_secret: "${SNOW_CLIENT_SECRET}"
telephony:
  provider_type: "ringcentral"
  ringcentral:
    client_id: "${RC_CLIENT_ID}"
    ...
salesforce:
  base_url: "https://login.salesforce.com"
  client_id: "${SF_CLIENT_ID}"
  client_secret: "${SF_CLIENT_SECRET}"
  token_file: null
```

**CRITICAL:** `${VAR}` placeholders are NOT auto-expanded. Code must use `os.environ.get('VAR')` or explicit expansion.

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health check |
| GET | `/api/health` | Monitoring health check |
| POST | `/vapi/webhook` | Vapi.ai event handler (call.start, call.end, toolCall.create) |
| POST | `/twilio/webhook` | Twilio TwiML generator |
| POST | `/api/incidents/create` | ServiceNow incident creation |
| POST | `/vapi/tools` | Salesforce tool execution router |
| POST | `/oauth/salesforce/callback` | OAuth2 code callback |
| GET | `/salesforce/status` | Auth status check |

## Common Pitfalls

1. **`*** Header(None)` syntax error** — should be `Header(None)`. The `***` was a typo that crashes the entire module on import.
2. **SOQL injection** — `find_lead_or_contact` interpolates email/phone directly. Must escape `'` → `''`.
3. **Missing psycopg2** — rate limit checker and password reset logger need it for PostgreSQL.
4. **Telephony provider not installed** — RingCentral SDK not in requirements.txt.
5. **Azure AD check endpoint wrong** — `/users/{upn}/accountEnabled` is not valid Graph API.
