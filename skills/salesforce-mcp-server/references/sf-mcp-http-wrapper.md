# SF MCP HTTP Wrapper

## Overview

HTTP wrapper that exposes Salesforce MCP tools as REST endpoints. Bridges Vapi voice AI to Salesforce operations.

**Location:** `~/projects/sf-mcp-official/http-wrapper/`

**Port:** 3001

**Start:** `node server.js` (or `npm start`)

## Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/tools` | GET | List available tools |
| `/vapi/tools` | POST | Execute a Salesforce tool (Vapi webhook format) |
| `/vapi/crm/process` | POST | Process structured call data into CRM updates |

## Tool Call Format

```json
POST /vapi/tools
{
  "tool_name": "sf_list_accounts",
  "parameters": { "limit": 5 }
}
```

Or Vapi native format:
```json
{
  "toolCallList": [
    { "function": { "name": "sf_get_user_info", "arguments": "{}" } }
  ]
}
```

## Available Tools

`sf_list_accounts`, `sf_get_account`, `sf_create_lead`, `sf_list_contacts`, `sf_create_contact`, `sf_list_opportunities`, `sf_create_opportunity`, `sf_create_case`, `sf_get_user_info`, `sf_list_users`

## Email Configuration

Processing agent: `agentbushwookiee@gmail.com` (app password: `pfrlkggfpolxtpqu`)
Used for: CRM processing, structured call data emails

## Notes

- The wrapper uses nodemailer internally for sending; himalaya CLI is only needed for reading
- Salesforce CLI path: `C:\Users\madco\AppData\Local\hermes\node\sf.cmd`
- CRM processing maps phone numbers to Accounts, creates Leads/Cases from action items