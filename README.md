# Sika Corp AI Agent Project

Voice AI agent integration for Sika Corp using interactive decision trees, ServiceNow IT helpdesk automation, and an abstracted telephony layer that supports RingCentral (and can be easily swapped for Twilio, Vapi.ai, or other systems).

## Project Structure

```
sika-ai-agent/
├── backend/                  # FastAPI backend server and webhook handlers
│   └── webhooks/             # ServiceNow and telephony webhook endpoints
├── telephony/                # Abstracted phone system layer (RingCentral, Twilio, etc.)
├── integrations/             # ServiceNow API integration with OAuth2
├── scripts/                  # Python scripts for various agent functions
├── trees/                    # JSON decision tree definitions
├── config/                   # Configuration and environment settings
└── README.md                 # This file
```

## Features

- First Call Resolution Agent (Target: 70% FCR)
- IAM Password Reset & Account Unlock Agent (Target: 95%+ FCR)
- Interactive JSON Decision Trees (No ML required)
- ServiceNow REST API Integration with OAuth2
- Abstracted Telephony Layer supporting RingCentral, Twilio, Vapi.ai

## Phone System Compatibility

This project uses an **abstracted telephony interface** that can be swapped between:
- ✅ **RingCentral** (Primary - default implementation)
- Twilio (Alternative)
- Vapi.ai native telephony (Alternative)
- Other SIP-based providers via adapter pattern

Configuration is handled via `config/telephony.yaml` to enable zero-code switching.

## API Keys & Configuration

This project integrates with:
- RingCentral / Telephony Provider (Phone system)
- ServiceNow (IT helpdesk automation, OAuth2)
- AWS Lambda or Serverless Platform (Webhook hosting)

Configuration details and API keys should be stored securely in the Obsidian vault at `/C:/Users/madco/Documents/Obsidian/API-Keys/.env.api-keys`.

## Setup Instructions

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables from your API keys vault and `config/telephony.yaml`

3. Run the backend server:
   ```bash
   uvicorn backend.server:app --host 0.0.0.0 --port 8000
   ```