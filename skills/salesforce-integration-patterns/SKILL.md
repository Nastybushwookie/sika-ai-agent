---
name: salesforce-integration-patterns
description: Review FastAPI/Python projects with Salesforce integration.
---

# Salesforce Integration Patterns

Use when building, reviewing, or debugging FastAPI/Python projects that integrate with Salesforce — OAuth flows, REST API clients, SOQL/SOSL queries, webhook handlers, and telephony adapter patterns.

## Trigger Conditions

- Reviewing a project that uses Salesforce (leads, contacts, accounts, tasks, incidents)
- Building OAuth2 integration with Salesforce
- Writing SOQL/SOSL queries from Python
- Integrating telephony (RingCentral, Twilio, Vapi.ai) with Salesforce
- Debugging Salesforce REST API errors

## Key Patterns

### 1. OAuth2 Authorization Code Flow

```python
# Token storage: file-backed for persistence, memory for dev
class SFTokenStore:
    # Stores access_token, refresh_token, instance_url, expires_at
    # Has 60s early expiry buffer to prevent race conditions
    pass

# Exchange code → tokens
async def exchange_code(self, code: str, redirect_uri: str):
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(token_url, data={
            'grant_type': 'authorization_code',
            'code': code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
        })
```

**Pitfalls:**
- Always use `httpx.AsyncClient(timeout=30)` — Salesforce tokens can be slow
- Save refresh_token even if not immediately needed — access tokens expire
- Consider expired 60s before actual expiry to prevent race conditions

### 2. SOQL Injection Prevention

**CRITICAL: Never interpolate user input directly into SOQL queries.**

```python
# WRONG — SQL injection vulnerability
leads = await self.query(
    f"SELECT ... FROM Lead WHERE Email = '{email}' LIMIT 5"
)

# RIGHT — escape single quotes
safe_email = email.replace("'", "''")
leads = await self.query(
    f"SELECT ... FROM Lead WHERE Email = '{safe_email}' LIMIT 5"
)
```

**Pitfalls:**
- Salesforce SOQL does NOT support bind variables (unlike SQL)
- Must escape single quotes manually: `'` → `''`
- Also escape for phone numbers, names, and any user-provided field
- This applies to `find_lead_or_contact` and similar search functions

### 3. Telephony Adapter Pattern

```python
class TelephonyProvider(ABC):
    @abstractmethod
    def initialize(self, config: Dict) -> bool: pass
    @abstractmethod
    def receive_inbound_call(self, phone_number: str) -> str: pass
    @abstractmethod
    def initiate_outbound_call(self, destination_phone: str, webhook_url: str) -> str: pass
    @abstractmethod
    def transfer_call(self, call_id: str, destination: str) -> bool: pass
    @abstractmethod
    def end_call(self, call_id: str) -> bool: pass
    @abstractmethod
    def get_call_status(self, call_id: str) -> Dict: pass
    @abstractmethod
    def send_sms(self, destination_phone: str, message: str) -> bool: pass

class TelephonyAdapterFactory:
    @staticmethod
    def get_provider(provider_type: str) -> TelephonyProvider:
        # 'ringcentral' → RingCentralProvider
        # 'twilio' → TwilioProvider
        # 'vapi_ai' → VapiAIProvider
        pass
```

**Pitfalls:**
- Config values like `${VAR}` in YAML are NOT auto-expanded — use `os.environ.get('VAR')` in code
- Each provider needs its own `initialize()` implementation
- Webhook base URL must be configured per-provider

### 4. FastAPI Webhook Handler Pattern

```python
@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, authorization: str = Header(None)):
    body = await request.json()
    tool_calls = body.get('toolCalls', [body])
    if not isinstance(tool_calls, list):
        tool_calls = [tool_calls]
    
    results = []
    for tc in tool_calls:
        tool_name = tc.get('name', '')
        tool_params = tc.get('parameters', {}) or {}
        result = await execute_tool(tool_name, tool_params)
        results.append({"toolCallId": tc.get('toolCallId'), "result": result})
    
    return JSONResponse(content={"results": results})
```

**Pitfalls:**
- Vapi may send single tool call OR wrapped in `toolCalls` array — handle both shapes
- Vapi may send `toolCallId` or `id` — check both
- Vapi may send `toolCalls` or single object — normalize to list first
- Always use `Header(None)` not `*** Header(None)` — `***` is a typo that crashes the app

## Quick Reference

| Endpoint | Purpose |
|----------|---------|
| `/vapi/tools` | Main Vapi function tool webhook |
| `/oauth/salesforce/callback` | OAuth2 authorization code callback |
| `/salesforce/status` | Quick auth check (no body needed) |

## Verification

- Check `/salesforce/status` — should return `{"authenticated": true/false, ...}`
- Check `/{root}` — should return service health with loaded components
- Verify all webhook endpoints respond to POST with proper status codes
