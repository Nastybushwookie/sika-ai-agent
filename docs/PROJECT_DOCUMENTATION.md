# Sika Corp AI Agent — Project Documentation

> **Org**: `orgfarm-4344f57ecf.my.salesforce.com` (API v67.0)
> **Connected as**: `williampullins@gmail.com`
> **Last verified**: 2026-08-19

---

## 1. Overview

Sika Corp AI Agent is a voice-driven IT support and sales automation platform that connects an AI voice assistant (via Vapi.ai) to Salesforce CRM and ServiceNow ITSM. The system uses interactive decision trees for troubleshooting, abstracted telephony for phone-system-agnostic deployment, and REST API integrations for CRM/ITSM operations.

### Core Capabilities

| Capability | Description |
|---|---|
| **First Call Resolution Agent** | Target: 70% FCR — interactive decision trees for IT troubleshooting |
| **IAM Password Reset & Unlock Agent** | Target: 95%+ FCR — ServiceNow-backed password reset with employee verification |
| **Sales Discovery Voice Agent** | AI consultant that qualifies leads via phone, captures data in Salesforce |
| **ServiceNow Incident Creation** | AI creates incidents, verifies employee status, enforces rate limits |
| **Salesforce CRM Operations** | Leads, Contacts, Accounts, Tasks, Calls — all via Vapi function tools |

---

## 2. Architecture

```
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Vapi.ai    │────▶│  Backend     │────▶│ Salesforce    │
│  (Voice AI) │     │  (FastAPI)   │     │ (CRM)         │
└─────────────┘     │              │     └───────────────┘
                      │  ┌─────────┐ │
┌─────────────┐     │  │Decision  │ │
│ RingCentral │────▶│  │ Trees   │ │
│ (Telephony) │     │  └─────────┘ │
└─────────────┘     │              │
                      │  ┌─────────┐ │
┌─────────────┐     │  │ServiceNow│ │
│ Twilio      │────▶│  │ ITSM    │ │
│ (Telephony) │     │  └─────────┘ │
└─────────────┘     └──────────────┘
```

### Key Design Decisions

- **Abstracted telephony layer** — swap RingCentral ↔ Twilio ↔ Vapi.ai without changing core logic
- **JSON decision trees** — no ML required; pure JSON → Python engine
- **OAuth2 token persistence** — file-backed token store in `.data/sf_tokens.json`
- **Vapi function tools** — Salesforce operations exposed as callable tools to the LLM

---

## 3. Project Structure

```
sika-ai-agent/
├── backend/
│   ├── server.py                  # FastAPI main app (385 lines)
│   ├── decision_tree_engine.py    # JSON decision tree engine (76 lines)
│   └── webhooks/
│       └── sf_webhook.py          # Salesforce Vapi function tool handler (191 lines)
├── telephony/
│   ├── interface.py               # Abstract TelephonyProvider + factory (80 lines)
│   ├── ringcentral_provider.py   # RingCentral implementation (119 lines)
│   ├── twilio_provider.py        # Twilio implementation (100 lines)
│   └── vai_provider.py           # Vapi.ai implementation (126 lines)
├── integrations/
│   ├── sf_oauth_client.py         # Salesforce OAuth2 + token store (172 lines)
│   ├── sf_rest_client.py          # Salesforce REST API client (277 lines)
│   └── snow_oauth_client.py       # ServiceNow OAuth2 client (124 lines)
├── scripts/
│   ├── hr_status_verification.py  # Employee active verification (90 lines)
│   ├── rate_limit_checker.py      # Password reset rate limiting (63 lines)
│   ├── password_reset_logger.py   # Audit logging (104 lines)
│   ├── fix-sf-mcp-config.py       # SF MCP config fixer (58 lines)
│   └── fix-sf-mcp-config.bat      # Windows batch wrapper
├── trees/
│   └── network_connectivity.json  # Network troubleshooting decision tree
├── config/
│   └── settings.yaml              # Environment config (env vars for secrets)
├── docs/
│   ├── AI_Voice_Assistant_Sales_Agent_Prompt.txt  # Sales discovery prompt (784 lines)
│   └── PROJECT_DOCUMENTATION.md # This file
├── .gitignore
├── requirements.txt
└── README.md
```

**Total lines of code**: ~3,100+ across 15 Python files

---

## 4. Component Details

### 4.1 FastAPI Backend (`backend/server.py`)

**Endpoints:**
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Health check with service status |
| GET | `/api/health` | Monitoring health endpoint |
| POST | `/vapi/webhook` | Vapi.ai event handler (call.start/end, toolCall.create) |
| POST | `/twilio/webhook` | Twilio TwiML response generator |
| POST | `/api/incidents/create` | Programmatic ServiceNow incident creation |
| POST | `/vapi/tools` | Salesforce Vapi function tools dispatcher |
| POST | `/oauth/salesforce/callback` | OAuth2 authorization code callback |
| GET | `/salesforce/status` | Quick auth status check |

**Tool Call Handlers (Vapi → Salesforce):**
| Tool Name | Handler |
|-----------|---------|
| `sf_create_lead` | Create Lead sObject |
| `sf_find_lead_or_contact` | SOQL search by email/phone |
| `sf_create_task` | Create Task on Lead/Contact |
| `sf_log_call_summary` | Create Task with call notes |
| `sf_create_contact` | Create Contact |
| `sf_create_account` | Create Account |
| `sf_query` | SOQL query |
| `sf_search` | SOSL search |
| `sf_describe` | Describe sObject schema |
| `sf_get_record` | Get record by ID |
| `sf_update_record` | PATCH record |
| `sf_delete_record` | DELETE record |
| `sf_list_records` | List records with field selection |
| `sf_auth_url` | Generate OAuth authorization URL |
| `sf_check_auth` | Check auth status |
| `sf_clear_auth` | Clear stored tokens |

### 4.2 Decision Tree Engine (`backend/decision_tree_engine.py`)

JSON-driven troubleshooting engine. Trees are defined as JSON with nodes containing questions, options, and conditional next nodes or resolutions.

**Currently loaded trees:**
- `network_connectivity` — Full network diagnostic flow (DNS, WiFi, Ethernet, app-specific)

**Tree format:**
```json
{
  "issue_type": "network_connectivity",
  "root_node": { "id": "net_start", "question": "...", "options": [...] },
  "internal_access_check": { "id": "...", "question": "...", "options": [...] },
  ...
}
```

### 4.3 Salesforce Integration

**OAuth2 Flow:**
1. `sf_auth_url` generates authorization URL (Authorization Code + Refresh Token)
2. User completes OAuth in browser
3. Callback at `/oauth/salesforce/callback` exchanges code for tokens
4. Tokens persisted to `.data/sf_tokens.json`
5. Automatic refresh on 401 with refresh token available

**ServiceNow Integration:**
- Base URL: `https://sikanow.sika.com`
- OAuth2 Client Credentials flow
- Token caching with 5-minute safety buffer
- User lookup by name or email
- Incident creation with caller validation

### 4.4 Telephony Providers

All implement the `TelephonyProvider` interface:
- `initialize(config)` → bool
- `receive_inbound_call(phone_number)` → str (webhook URL)
- `initiate_outbound_call(destination, webhook)` → str (call ID)
- `transfer_call(call_id, dest)` → bool
- `end_call(call_id)` → bool
- `get_call_status(call_id)` → dict
- `send_sms(destination, message)` → bool

**Configured provider**: `ringcentral` (via `config/settings.yaml`)

### 4.5 HR Verification & Rate Limiting

**Employee Active Check** (`scripts/hr_status_verification.py`):
- Checks ServiceNow `sys_user.active` field
- Checks `u_termination_date` with 30-day grace period
- Also supports Azure AD (Microsoft Graph) and on-prem AD lookups

**Rate Limiting** (`scripts/rate_limit_checker.py`):
- Max 3 password resets per hour per employee
- Max 3 password resets per day per employee
- PostgreSQL-backed audit log

**Audit Logging** (`scripts/password_reset_logger.py`):
- Logs to `password_reset_log` table
- Tracks: employee_id, reset_method, result, error_message, duration_ms
- Supports both reset and unlock operations

### 4.6 Sales Discovery Agent Prompt (`docs/AI_Voice_Assistant_Sales_Agent_Prompt.txt`)

784-line personality-driven sales discovery prompt for Vapi.ai:
- Identity: AI Business Consultant helping SMBs with AI voice solutions
- Personality: Friendly, professional, curious, conversational
- Flow: Opening → Business Understanding → Lead Sources → Call Volume → Communication → Response Time → Missed Opportunities → Appointment Process → Admin Work → Pain Points → Goals → Qualification → Solution Mapping → Pricing → Closing
- Objection handling: Price, phone coverage, call volume, AI skepticism, setup difficulty
- Pricing tiers: Starter ($600 setup / $397mo), Complete ($1,000 setup / $500mo)

---

## 5. Configuration

### `config/settings.yaml`

```yaml
environment: development

servicenow:
  base_url: "https://sikanow.sika.com"
  client_id: "${SNOW_CLIENT_ID}"        # env var
  client_secret: "${SNOW_CLIENT_SECRET}" # env var
  integration_account: "vapi_incident_bot"

telephony:
  provider_type: "ringcentral"            # ringcentral | twilio | vapi_ai
  ringcentral:
    client_id: "${RC_CLIENT_ID}"
    client_secret: "${RC_CLIENT_SECRET}"
    username: "${RC_USERNAME}"
    extension: "${RC_EXTENSION}"
    password: "${RC_PASSWORD}"
    server: "https://platform.ringcentral.com"
    phone_number: "${RC_PHONE_NUMBER}"
  twilio:
    account_sid: "${TWILIO_ACCOUNT_SID}"
    auth_token: "${TWILIO_AUTH_TOKEN}"
    phone_number: "${TWILIO_PHONE_NUMBER}"
  vapi_ai:
    api_key: "${VAPI_API_KEY}"
    assistant_id: "${VAPI_ASSISTANT_ID}"

webhooks:
  base_url: "https://api.yourcompany.com"
  vapi_webhook_path: "/vapi/webhook"
  twilio_webhook_path: "/twilio/webhook"

salesforce:
  base_url: "https://login.salesforce.com"
  client_id: "${SF_CLIENT_ID}"
  client_secret: "${SF_CLIENT_SECRET}"
  token_file: null                       # auto: .data/sf_tokens.json
```

### Environment Variables Required

| Variable | Purpose |
|----------|---------|
| `SNOW_CLIENT_ID` | ServiceNow OAuth2 client ID |
| `SNOW_CLIENT_SECRET` | ServiceNow OAuth2 client secret |
| `RC_CLIENT_ID` | RingCentral app client ID |
| `RC_CLIENT_SECRET` | RingCentral app client secret |
| `RC_USERNAME` | RingCentral account username |
| `RC_EXTENSION` | RingCentral extension |
| `RC_PASSWORD` | RingCentral password |
| `RC_PHONE_NUMBER` | RingCentral assigned phone number |
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | Twilio phone number |
| `VAPI_API_KEY` | Vapi.ai API key |
| `VAPI_ASSISTANT_ID` | Vapi.ai assistant ID |
| `SF_CLIENT_ID` | Salesforce connected app consumer key |
| `SF_CLIENT_SECRET` | Salesforce connected app consumer secret |

---

## 6. Salesforce Org Details

| Property | Value |
|----------|-------|
| **Instance** | `orgfarm-4344f57ecf.my.salesforce.com` |
| **API Version** | 67.0 (Summer '26) |
| **Connected as** | `williampullins@gmail.com` |
| **Org ID** | `00Dhm000001EPwTEAW` |
| **Status** | Connected |

### Connected App (OAuth)

The project uses a Connected App for OAuth2 Authorization Code + Refresh Token flow. The connected app must be configured in the Salesforce org with:
- OAuth scopes: `api`, `refresh_token`, `openid`
- Callback URL: `http://localhost:8000/oauth/salesforce/callback` (dev) or production equivalent
- IP relaxations or trusted IPs for production

### Token Storage

Tokens are persisted to `.data/sf_tokens.json` (relative to project root). In production, this should be replaced with an encrypted file path or secrets manager.

---

## 7. Git History

| Commit | Date | Description |
|--------|------|-------------|
| `ac6930f` | 2026-08-18 | Complete webhook handlers, Vapi.ai tool call processing, incident creation workflow, and Twilio TwiML responses |
| `8311b46` | 2026-08-18 | Complete Sika AI Agent project with abstracted telephony layer supporting RingCentral, Twilio, and Vapi.ai |
| `4978f22` | 2026-07-24 | Initial commit: Sika Corp AI Agent project setup with core scripts |

---

## 8. Dependencies

```
requests>=2.31.0
python-dotenv>=1.0.0
fastapi>=0.104.0
uvicorn>=0.24.0
httpx>=0.26.0
ringcentral>=4.3.2
twilio>=8.10.0
pysnow>=0.7.16
pydantic>=2.5.0
PyYAML>=6.0.1
psycopg2          # (for password reset audit logging)
```

---

## 9. Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables
export SNOW_CLIENT_ID=...
export SNOW_CLIENT_SECRET=...
export RC_CLIENT_ID=...
export RC_CLIENT_SECRET=...
# ... (all env vars from section 5)

# 3. Run the server
uvicorn backend.server:app --host 0.0.0.0 --port 8000
```

---

## 10. Known Items / TODO

| Item | Priority | Notes |
|------|----------|-------|
| Missing `sf_oauth_client.py` in git | High | File exists but untracked |
| Missing `sf_rest_client.py` in git | High | File exists but untracked |
| Missing `webhooks/` dir in git | High | Untracked |
| Missing `docs/` dir in git | High | Untracked |
| Missing `fix-sf-mcp-config.py` in git | Medium | Untracked |
| Missing `fix-sf-mcp-config.bat` in git | Medium | Untracked |
| `.exe` files in git | Low | `Usersmadcohimalaya*.exe` — should be in .gitignore |
| `.zip` files in git | Low | `Usersmadcohimalaya.zip` — should be in .gitignore |
| Modified `server.py` not committed | Medium | Unstaged changes |
| Modified `settings.yaml` not committed | Medium | Unstaged changes |
| No remote configured | High | `git remote -v` returns empty — needs origin |

---

## 11. API Key Storage

Per README.md, API keys are stored in the Obsidian vault at:
`C:/Users/madco/Documents/Obsidian/API-Keys/.env.api-keys`

---

*Document generated: 2026-08-19*
