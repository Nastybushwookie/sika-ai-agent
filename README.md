# Sika Corp AI Agent Project

Voice AI agent integration for Sika Corp using Vapi.ai + Twilio + ServiceNow IT helpdesk automation.

## Project Structure

```
sika-ai-agent/
├── backend/          # Backend server code and APIs
├── scripts/          # Python scripts for various agent functions
├── docs/             # Documentation and planning files
└── README.md         # This file
```

## Features

- First Call Resolution Agent
- IAM Password Reset Agent  
- ServiceNow Webhook Integration
- HR Status Verification
- Rate Limit Checking

## API Keys & Configuration

This project integrates with:
- Vapi.ai (Voice agent platform)
- Twilio (Telephony services)
- ServiceNow (IT helpdesk automation)

Configuration details and API keys should be stored securely in the Obsidian vault at `/C:/Users/madco/Documents/Obsidian/API-Keys/.env.api-keys`.

## Setup Instructions

1. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure environment variables from your API keys vault

3. Run the backend server or scripts as needed