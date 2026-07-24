"""
Sika Corp AI Agent FastAPI Backend Server
Handles webhooks from telephony providers and ServiceNow integrations
"""
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import JSONResponse
import httpx
import yaml
import os
from typing import Dict, Any

# Import components
from .decision_tree_engine import DecisionTreeEngine
from ..integrations.snow_oauth_client import SnowOAuthClient
from ..telephony.interface import TelephonyAdapterFactory

app = FastAPI(
    title="Sika Corp AI Agent Backend",
    description="Backend API for Sika Corp IT Support AI Agent with abstracted telephony layer",
    version="1.0.0"
)

# Load configuration
config = {}
try:
    with open("config/settings.yaml", "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Warning: Could not load config settings: {str(e)}")

# Initialize components
decision_tree_engine = DecisionTreeEngine()
snow_client = None

# Load decision trees
tree_files = [
    "trees/network_connectivity.json",
    # Additional trees would be loaded here
]

for tree_file in tree_files:
    if os.path.exists(tree_file):
        try:
            decision_tree_engine.load_tree(tree_file)
        except Exception as e:
            print(f"Warning: Could not load tree {tree_file}: {str(e)}")

# Initialize ServiceNow client if credentials are available
if config.get('servicenow', {}).get('client_id') and config.get('servicenow', {}).get('client_secret'):
    snow_base_url = config['servicenow'].get('base_url', 'https://sikanow.sika.com')
    snow_client = SnowOAuthClient(
        base_url=snow_base_url,
        client_id=config['servicenow']['client_id'],
        client_secret=config['servicenow']['client_secret']
    )

# Initialize telephony provider
telephony_provider = None
if config.get('telephony', {}).get('provider_type'):
    provider_type = config['telephony']['provider_type']
    try:
        telephony_provider = TelephonyAdapterFactory.get_provider(provider_type)
        
        # Extract provider-specific config
        provider_config = {}
        if provider_type == 'ringcentral':
            provider_config = config.get('telephony', {}).get('ringcentral', {})
        elif provider_type == 'twilio':
            provider_config = config.get('telephony', {}).get('twilio', {})
        elif provider_type == 'vapi_ai':
            provider_config = config.get('telephony', {}).get('vapi_ai', {})
            
        # Add webhook base URL to config
        provider_config['webhook_base_url'] = config.get('webhooks', {}).get('base_url', 'https://api.yourcompany.com')
        
        telephony_provider.initialize(provider_config)
    except Exception as e:
        print(f"Warning: Could not initialize telephony provider {provider_type}: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Sika Corp AI Agent Backend",
        "status": "running",
        "version": "1.0.0",
        "telephony_provider": config.get('telephony', {}).get('provider_type', 'not_configured'),
        "servicenow_integration": "configured" if snow_client else "not_configured"
    }

@app.get("/api/health")
async def health_check():
    """Health check for monitoring."""
    return {
        "status": "healthy",
        "timestamp": "2026-07-24T13:25:56.240Z",
        "environment": config.get('environment', 'development'),
        "telephony_provider": config.get('telephony', {}).get('provider_type', 'not_configured')
    }

@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, authorization: str = Header(None)):
    """Webhook endpoint for Vapi.ai or telephony provider events."""
    try:
        webhook_data = await request.json()
        
        # Log the incoming webhook data for debugging
        print(f"Received webhook data: {webhook_data}")
        
        # Process the webhook based on event type
        event_type = webhook_data.get('event')
        
        if event_type == 'call.start':
            # Handle call start event
            pass
        elif event_type == 'call.end':
            # Handle call end event
            pass
        elif 'toolCall' in str(webhook_data):
            # Handle tool calls (like incident creation)
            pass
            
        return JSONResponse(status_code=200, content={"status": "received"})
    except Exception as e:
        print(f"Webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    """Webhook endpoint for Twilio events."""
    try:
        # In a real implementation, this would return TwiML responses
        webhook_data = await request.form() if request.form else {}
        print(f"Received Twilio webhook data: {webhook_data}")
        
        return JSONResponse(status_code=200, content={"status": "received"})
    except Exception as e:
        print(f"Twilio webhook processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/incidents/create")
async def create_incident(request: Request):
    """Endpoint to create ServiceNow incidents programmatically."""
    if not snow_client:
        raise HTTPException(status_code=500, detail="ServiceNow client not configured")
        
    try:
        incident_data = await request.json()
        
        # Extract required fields
        caller_sys_id = incident_data.get('caller_sys_id')
        short_description = incident_data.get('short_description')
        
        if not caller_sys_id or not short_description:
            raise HTTPException(status_code=400, detail="Missing required fields: caller_sys_id and short_description")
            
        # Create the incident
        incident = await snow_client.create_incident(
            caller_sys_id=caller_sys_id,
            short_description=short_description,
            impact=incident_data.get('impact', '2'),
            urgency=incident_data.get('urgency', '2')
        )
        
        return {
            "status": "success",
            "incident": incident,
            "number": incident.get('number'),
            "url": f"{config['servicenow'].get('base_url', 'https://sikanow.sika.com')}/nav_to.do?uri=incident.do?sys_id={incident.get('sys_id')}"
        }
    except Exception as e:
        print(f"Incident creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create incident: {str(e)}")
