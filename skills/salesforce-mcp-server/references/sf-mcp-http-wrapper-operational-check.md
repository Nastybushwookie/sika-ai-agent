# SF MCP HTTP Wrapper — Operational Verification

## Quick Check

The wrapper runs on **port 3001**. Starting it (`node server.js`) prints:
```
SF MCP HTTP Wrapper running on http://localhost:3001
Available tools: sf_list_accounts, sf_get_account, sf_create_lead, ...
Email configured: agentbushwookiee@gmail.com
CRM processing: enabled (phone→Account, Leads/Cases from action items)
```

## Verification Steps

1. **Start it:** `cd ~/projects/sf-mcp-official/http-wrapper && node server.js`
2. **Test tool listing:** `curl -s http://localhost:3001/tools`
3. **Execute a tool** (critical — the wrapper uses POST to `/vapi/tools`, NOT GET on individual tool paths):
   ```bash
   curl -s -X POST http://localhost:3001/vapi/tools \
     -H 'Content-Type: application/json' \
     -d '{"tool_name":"sf_get_user_info","parameters":{}}'
   ```
   Success returns `{"results":[{"toolCallId":"...","result":{"ok":true,"data":{...}}}]}`
4. **Query data:**
   ```bash
   curl -s -X POST http://localhost:3001/vapi/tools \
     -H 'Content-Type: application/json' \
     -d '{"tool_name":"sf_list_accounts","parameters":{"limit":5}}'
   ```

## Common Pitfalls

- **Port confusion:** Runs on 3001, NOT 3000. Don't check 3000.
- **GET vs POST:** Tool execution requires `POST /vapi/tools` with JSON body. GET on `/tools/sf_list_accounts` returns "Cannot GET /tools/sf_list_accounts".
- **Tool names:** Exact names from the `/tools` list — `sf_list_accounts` (not `list_accounts` or `get_accounts`).
- **Timeout errors:** `sf` CLI commands can take up to 90s. The wrapper has a 90s timeout built in. Short timeouts (10-15s) will kill `sf` commands before they complete.
- **Windows path to sf CLI:** `C:\\Users\\madco\\AppData\\Local\\hermes\\node\\sf.cmd` — hardcoded in server.js line 63.
- **Background process:** Use `background=true` for the server, or start it locally. The terminal tool kills foreground server processes.

## Email Automation

- **Sending:** Built into the wrapper via nodemailer (no external install needed)
- **Reading:** Requires himalaya CLI installed OR raw Node.js IMAP script
- **Processing agent:** `agentbushwookiee@gmail.com` with app password `pfrlkggfpolxtpqu`
