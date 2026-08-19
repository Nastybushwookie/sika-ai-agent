---
name: salesforce-mcp-http-wrapper
description: Expose stdio-based Salesforce MCP as HTTP API for Vapi.
---

# Salesforce MCP HTTP Wrapper

## Trigger
Use when you need to expose the Salesforce MCP server (which is stdio-based, NOT HTTP) to a service that requires HTTP — typically Vapi.ai function tools, webhooks, or any REST API consumer.

## Why This Exists
The official `@salesforce/mcp` server communicates via **stdio** (standard input/output), not HTTP. It cannot be tunneled with Cloudflare/ngrok directly. To expose Salesforce MCP tools to Vapi or any HTTP-based consumer, you need an HTTP wrapper that calls the `sf` CLI directly.

## Implementation

### 1. Create the wrapper project
```bash
mkdir -p /c/Users/madco/projects/sf-mcp-official/http-wrapper
cd /c/Users/madco/projects/sf-mcp-official/http-wrapper
npm init -y
npm install express cors uuid
```

### 2. Write server.js
The server should:
- Use `express` to create HTTP endpoints
- Use `child_process.execFile` to call `sf.cmd` directly (NOT the MCP stdio protocol)
- Map tool names to `sf` CLI commands (query, upsert, etc.)
- Expose a `/vapi/tools` endpoint compatible with Vapi function tool format
- Expose a `/tools` endpoint listing available tools
- Expose a `/health` endpoint for verification

### 3. Start the server (USER MUST RUN MANUALLY ON WINDOWS)

⚠️ **Terminal commands hang on Windows foreground mode** — `taskkill`, `netstat`, and other process-management commands will timeout in foreground terminal calls. Instead:

- **For code changes**: Use `write_file` / `patch` tools directly (no terminal needed). The skill author's approach is to write the full server.js via file write, then have the user kill old processes and start fresh.
- **Server startup**: Tell user to run `node server.js` in their own PowerShell/terminal. Do NOT try to background it from inside Hermes terminal — it will timeout.
- **For killing existing servers**: User should run `taskkill /F /IM node.exe` themselves, or use the browser dev tools approach.

```bash
# User runs this manually:
cd C:\Users\madco\projects\sf-mcp-official\http-wrapper
node server.js
```
Server runs on port 3001 by default.

## Architecture Patterns

### Vapi ↔ Salesforce Bridge (Pure Tool Calling)
The base `server.js` exposes SF CLI operations as REST endpoints for Vapi function tools. No email, no CRM processing — just the clean Vapi function calling wrapper.

Endpoints:
- `GET /health` — health check
- `GET /tools` — list available SF tools  
- `POST /vapi/tools` — execute SF tool calls (Vapi webhook)
- `POST /vapi/call-end` — receives call-complete events from Vapi

### Email + CRM Automation Version
The enhanced version (`server-with-email-automation.js`) adds:

1. **Structured call data emails** to `agentbushwookiee@gmail.com` with HTML body + JSON payload attachment
2. **CRM processing**: match caller phone → find Account/Contact, create Leads/Cases from action items and next steps  
3. **Notify mode**: optional `NOTIFY_TO` env var for FYI copies
4. **Manual CRM trigger**: `/vapi/crm/process` endpoint

Architecture:
```
Vapi Call Complete → /vapi/call-end → Format structured payload → Send as EMAIL
                                                         ↓
                                                Your AI Agent (listens to inbox)
                                                         ↓
                                                   Reads email, extracts data
                                                         ↓
                                               Updates Salesforce records
```

The wrapper formats the call data into a structured email that your agent can parse and act on. The CRM function does:
- **Phone match** → find Account → create/update Contact linked to it
- **No account found** → create Lead with `Source: Vapi AI Call`  
- **Action items / next steps** → create Salesforce Cases from each item

### Email Credentials
- Sender: `vapi-agent@smartscaleai.net`
- Recipient (processing): `agentbushwookiee@gmail.com`
  - App password: `pfrlkggfpolxtpqu`  
- Optional notify recipient: set via `NOTIFY_TO` env var

### Structured Payload Format (JSON attachment)
```json
{
  "_type": "vapi_call_complete",
  "callId": "...",
  "timestamp": "...", 
  "assistant": "Sika Assistant",
  "callerNumber": "+1555...",
  "durationSecs": 245,
  "customer": { "name": "...", "company": "...", "email": "...", "phone": "..." },
  "intent": "...",
  "summary": ["..."],
  "actionItems": ["..."], 
  "nextSteps": ["..."]
}
```

### Migration Path (if needed)  
If you want to use the email automation again in the future:
1. Copy `server-with-email-automation.js` → `server.js`
2. Restart the server on port 3001
3. Configure `NOTIFY_TO` env var if you want personal notifications

## Cloudflare Tunnel
The named tunnel `tunnel.smartscaleai.net` routes to port 3001 (SF MCP HTTP wrapper).

### 4. Expose via tunnel
```bash
ngrok http 3001
```
This gives you a public URL for Vapi function tools.

## Key Implementation Details

### SF CLI Path on Windows

**Critical:** On Windows, `execFile('sf.cmd', ...)` fails with `EINVAL` when called from Node inside Git Bash/MSYS because MSYS mangles paths with backslashes. The fix is to use **dynamic PATH detection** (just `'sf.cmd'`) and spawn via `cmd.exe /c`:

```javascript
const SF_CLI = process.platform === 'win32' ? 'sf.cmd' : 'sf'; // dynamic PATH detection, not hardcoded path

function runSfCommand(args, timeout = 90000) {  // 90s — CLI startup + auth check takes ~15-30s
    return new Promise((resolve) => {
        const proc = execFile('cmd.exe', ['/c', SF_CLI, ...args], 
            { timeout, maxBuffer: 1024 * 1024 }, (error, stdout, stderr) => {
                if (error) { resolve({ error: stderr || error.message }); return; }
                try { resolve(JSON.parse(stdout)); }
                catch { resolve({ raw: stdout.trim() }); }
            });
        proc.on('error', () => resolve({ error: `Failed to run sf CLI` }));
    });
}
```

**Key points:**
- Use **dynamic detection via PATH**: `const SF_CLI = process.platform === 'win32' ? 'sf.cmd' : 'sf';` — do NOT use hardcoded paths like `C:\\Users\\...\\sf.cmd`. MSYS mangles backslash paths, causing `spawn EINVAL`. Simple names like `'sf.cmd'` avoid this.
- Always wrap in `'cmd.exe'` with `'/c'` flag, even on Windows — Node's execFile can't spawn `.cmd` directly from bash contexts
- Set timeout to **90s minimum** — SF CLI startup + auth check takes 15-30s; Vapi times out at ~30s

### Vapi-Compatible Endpoint (Handles Both Payload Formats)

Vapi sends `toolCallList` inside a `message` wrapper. The server must check both nesting levels:

```javascript
app.post('/vapi/tools', async (req, res) => {
    const body = req.body;
    
    // Check BOTH locations for toolCallList
    let toolCallList = null;
    if (body.toolCallList && Array.isArray(body.toolCallList)) {
        toolCallList = body.toolCallList;
    } else if (body.message?.toolCallList && Array.isArray(body.message.toolCallList)) {
        // Vapi's actual format: wraps inside message object
        toolCallList = body.message.toolCallList;
    }
    
    // Format 1: Simple legacy call
    if (!toolCallList && body.tool_name) {
        const result = await executeTool(body.tool_name, body.parameters || {});
        return res.json({ results: [{ 
            toolCallId: body.toolCallId || uuidv4(),
            result: { ok: true, data: result } 
        }] });
    }
    
    // Format 2: Vapi native payload (toolCallList inside message)
    if (toolCallList) {
        const results = [];
        for (const call of toolCallList) {
            let name, args;
            
            // Vapi sends: { id, function: { name, arguments } }
            if (call.function && typeof call.function === 'object') {
                name = call.function.name;
                try { args = JSON.parse(call.function.arguments || '{}'); } catch { args = {}; }
            }
            // Fallback: { id, name, arguments }
            else if (call.name && call.arguments) {
                name = call.name;
                try { args = typeof call.arguments === 'string' ? JSON.parse(call.arguments) : call.arguments || {}; } catch { args = {}; }
            }
            
            if (!name) {
                results.push({ toolCallId: call.id, result: { ok: false, error: 'No function name' } });
                continue;
            }
            
            try {
                const result = await executeTool(name, args);
                const hasError = result.error || (result.raw && result.raw.includes('ERROR'));
                results.push({ 
                    toolCallId: call.id,
                    result: { ok: !hasError, data: hasError ? null : result, error: hasError ? result.error : undefined }
                });
            } catch (error) {
                results.push({ toolCallId: call.id, result: { ok: false, error: error.message || String(error) } });
            }
        }
        // Vapi expects exactly this shape — NO extra fields, just "results" array
        return res.json({ results });
    }
    
    res.status(400).json({ results: [], error: 'Invalid request format' });
});
```

**Vapi's actual webhook payload (what the agent actually sends):**
```json
{
  "message": {
    "type": "tool-calls",
    "toolCallList": [
      {
        "id": "eYf9qW3jPrHqL3evkzESZBDy2sSoc0tF",
        "function": {
          "name": "sf_create_lead",
          "arguments": "{\"company\":\"Test Corp\",\"firstName\":\"John\"}"
        }
      }
    ]
  }
}
```

**Vapi's expected response format (must match exactly):**
```json
{
  "results": [
    {
      "toolCallId": "eYf9qW3jPrHqL3evkzESZBDy2sSoc0tF",
      "result": {
        "ok": true,
        "data": { ... tool result ... }
      }
    }
  ]
}
```

⚠️ **Critical:** The `results` array is the ONLY field. Do NOT include `id`, `status`, `message`, or any other top-level keys — Vapi will silently discard them and report "No result returned".

## Troubleshooting: "Unexpected endpoint or method" Error

**Symptom**: Vapi returns "Failed to fetch" or "Unexpected endpoint" when calling `/vapi/tools`

**Root cause**: The HTTP wrapper is not receiving the request from Cloudflare tunnel. This usually means:

1. **Server isn't running**: Check `curl http://localhost:<port>/health` locally
2. **Route handler missing**: Verify `app.post('/vapi/tools', ...)` exists in server.js
3. **Tunnel forwarding incorrectly**: Check cloudflared process is active and logging traffic
4. **WAF blocking**: Cloudflare security rules may block POST requests - check dashboard → Security → Events

**Debugging steps**:
1. Run `curl http://localhost:3001/vapi/tools -X POST -H "Content-Type: application/json" -d '{"tool_name":"sf_get_user_info"}'` locally — should return tool results or error, NOT HTML
2. If local call fails with HTML/error page → Express route not registered properly
3. If local works but tunnel doesn't → Check cloudflared logs for routing errors
4. If WAF blocking → Disable "Under Attack Mode" temporarily in Cloudflare dashboard

## Common Pitfalls
1. **Never try to tunnel the MCP server directly** — it's stdio-only, use an HTTP wrapper instead
2. **The "spawn EINVAL" error on Windows from Git Bash/MSYS:** Node's `execFile` cannot spawn `.cmd` files directly when running under MSYS paths. Fix: pass full path to `sf.cmd` and wrap in `'cmd.exe'` with `'/c'` flag, e.g. `execFile('cmd.exe', ['/c', SF_CLI_FULL_PATH, ...args], ...)`
3. **Timeout too short:** SF CLI startup + auth check takes 15-30s. Set timeout to **90s minimum** in `runSfCommand`. Vapi's webhook timeout is ~30s — if the CLI takes longer, Vapi reports "No result returned" even though your server got a valid response
4. **Wrong Vapi payload nesting:** Vapi sends `toolCallList` inside `body.message.toolCallList`, NOT at the top level. Always check both: `body.toolCallList[]` and `body.message?.toolCallList[]`
5. **Wrong response shape causes "No result returned":** Vapi ONLY reads a top-level `results` array with `{ toolCallId, result: { ok, data } }`. Any extra fields (`id`, `status`, `message`) are silently ignored by Vapi's parser
6. **Route not responding through tunnel:** If local curl works but tunnel returns HTML/404/"Unexpected endpoint", the Express route is registered correctly locally but cloudflared may be routing to wrong port or another service. Verify with `netstat -ano | findstr :3001` and check cloudflared config
7. **`sf org login web` must run in a local terminal** — it opens browser OAuth; the HTTP wrapper Node process just reads the auth file on disk after login succeeds

## Cloudflare Tunnel Setup via API Token (with two subdomains)

### 1. Create tunnel via API
```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/{account-id}/tunnels" \
  -H "Authorization: Bearer {token}" \
  -d '{"name":"my-tunnel","conns":[]}'
# Returns: id, secret (TunnelSecret)
```

### 2. Create DNS records (one per hostname you want to route)
```bash
# For contact.smartscaleai.net → LM Studio port 1234
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone-id}/dns_records" \
  -H "Authorization: Bearer {token}" \
  -d '{"type":"CNAME","name":"contact","content":"<tunnel-id>.cfargotunnel.com","ttl":1,"proxied":true}'

# For tunnel.smartscaleai.net → HTTP wrapper port 3001 (Vapi)
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone-id}/dns_records" \
  -H "Authorization: Bearer {token}" \
  -d '{"type":"CNAME","name":"tunnel","content":"<tunnel-id>.cfargotunnel.com","ttl":1,"proxied":true}'
```

### 3. Save tunnel credentials (named as `tunnel.json`, not `credentials.json`)
Create `~/.cloudflared/tunnel.json`:
```json
{
  "AccountTag": "{account-id}",
  "TunnelID": "<tunnel-id>",
  "TunnelSecret": "<secret>"
}
```

### 4. Create config.yaml with multiple hostnames/routes
```yaml
tunnel: <tunnel-id>
credentials-file: C:\Users\madco\.cloudflared\tunnel.json

ingress:
  - hostname: contact.smartscaleai.net
    service: http://localhost:1234   # LM Studio
  - hostname: tunnel.smartscaleai.net
    service: http://localhost:3001   # HTTP wrapper (Vapi)
  - service: http_status:404         # catch-all
```

### 5. Start the tunnel
```bash
cd "C:\Program Files (x86)\cloudflared"
.\cloudflared.exe tunnel --config "C:\Users\madco\.cloudflared\tunnel.yaml" run
```

⚠️ If you update config.yaml, **restart cloudflared** (`taskkill /F` the process, then rerun) to pick up changes. The old process caches its config and won't re-read on its own.

## Files
- `server.js` — Main HTTP server with tool implementations
- `package.json` — Dependencies (express, cors, uuid)
