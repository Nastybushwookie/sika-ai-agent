"""
Sika Corp AI Agent FastAPI Backend Server
Handles webhooks from Vapi.ai, telephony providers, and ServiceNow integrations
"""
from fastapi import FastAPI, HTTPException, Request, Header, Body
from fastapi.responses import JSONResponse
try:
    from fastapi.responses import XMLResponse
except ImportError:
    from fastapi.responses import HTMLResponse as XMLResponse
import httpx
import yaml
import os
import json
from typing import Dict, Any, Optional
from datetime import datetime

# Import components — use correct paths for project structure
import sys
import os

# Add both project root and backend directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.dirname(os.path.abspath(__file__))

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# decision_tree_engine is in the backend directory, so import it with its full path
from backend.decision_tree_engine import DecisionTreeEngine
from integrations.snow_oauth_client import SnowOAuthClient
from backend.webhooks.sf_webhook import router as sf_webhook_router
from telephony.interface import TelephonyAdapterFactory
from scripts.hr_status_verification import verify_employee_active_service_now
from scripts.rate_limit_checker import check_rate_limit, check_rate_limit_webhook
from scripts.password_reset_logger import log_password_reset_attempt

app = FastAPI(
    title="Sika Corp AI Agent Backend",
    description="Backend API for Sika Corp IT Support AI Agent with abstracted telephony layer",
    version="1.0.0"
)

# Load configuration
config = {}
try:
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'settings.yaml')
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
except Exception as e:
    print(f"Warning: Could not load config settings: {str(e)}")

# Initialize components
decision_tree_engine = DecisionTreeEngine()
snow_client = None
telephony_provider = None

# Load decision trees
tree_files = [
    os.path.join(os.path.dirname(__file__), '..', 'trees', 'network_connectivity.json'),
    # Additional trees would be loaded here
]

for tree_file in tree_files:
    if os.path.exists(tree_file):
        try:
            decision_tree_engine.load_tree(tree_file)
        except Exception as e:
            print(f"Warning: Could not load tree {tree_file}: {str(e)}")

# Initialize ServiceNow client if credentials are available
snow_config = config.get('servicenow', {})
if snow_config.get('client_id') and snow_config.get('client_secret'):
    snow_base_url = snow_config.get('base_url', 'https://sikanow.sika.com')
    snow_client = SnowOAuthClient(
        base_url=snow_base_url,
        client_id=snow_config['client_id'],
        client_secret=snow_config['client_secret']
    )

# Initialize telephony provider
telephony_config = config.get('telephony', {})
if telephony_config.get('provider_type'):
    provider_type = telephony_config['provider_type']
    try:
        telephony_provider = TelephonyAdapterFactory.get_provider(provider_type)
        
        # Extract provider-specific config
        provider_cfg = {}
        if provider_type == 'ringcentral':
            provider_cfg = telephony_config.get('ringcentral', {})
        elif provider_type == 'twilio':
            provider_cfg = telephony_config.get('twilio', {})
        elif provider_type == 'vapi_ai':
            provider_cfg = telephony_config.get('vapi_ai', {})
            
        # Add webhook base URL to config
        webhook_base = config.get('webhooks', {}).get('base_url', 'https://api.yourcompany.com')
        provider_cfg['webhook_base_url'] = webhook_base
        
        telephony_provider.initialize(provider_cfg)
    except Exception as e:
        print(f"Warning: Could not initialize telephony provider {provider_type}: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "Sika Corp AI Agent Backend",
        "status": "running",
        "version": "1.0.0",
        "telephony_provider": telephony_config.get('provider_type', 'not_configured'),
        "servicenow_integration": "configured" if snow_client else "not_configured",
        "decision_trees_loaded": len(decision_tree_engine.trees)
    }

@app.get("/api/health")
async def health_check():
    """Health check for monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": config.get('environment', 'development'),
        "telephony_provider": telephony_config.get('provider_type', 'not_configured')
    }


@app.post("/vapi/webhook")
async def vapi_webhook(request: Request, authorization: str = Header(None)):
    """
    Webhook endpoint for Vapi.ai events.
    Handles call.start, call.end, toolCall.create, and other Vapi events.
    """
    try:
        webhook_data = await request.json()
        event_type = webhook_data.get('eventType') or webhook_data.get('event')
        
        print(f"[Vapi Webhook] Received event: {event_type}")
        print(f"[Vapi Webhook] Data: {json.dumps(webhook_data, indent=2)}")
        
        # Handle toolCall.create events (function/tool calls by the LLM)
        if event_type in ['toolCall.create', 'tool_call.create']:
            tool_call = webhook_data.get('toolCall') or webhook_data.get('data', {}).get('toolCall')
            if tool_call:
                tool_name = tool_call.get('name')
                tool_params = tool_call.get('parameters', {})
                
                # Handle create_servicenow_incident tool call
                if tool_name == 'create_servicenow_incident':
                    result = await handle_create_incident_tool(tool_params)
                    
                    # Return the tool result to Vapi
                    return JSONResponse(status_code=200, content={
                        "toolCallId": tool_call.get('toolCallId'),
                        "result": result
                    })
                
                # Handle transfer_call tool call (warm transfer to human agent)
                elif tool_name == 'transfer_call':
                    # In Vapi, transfer_call is often handled natively via dashboard config,
                    # but if processed here, we'd trigger telephony transfer
                    if telephony_provider:
                        call_id = webhook_data.get('call', {}).get('id')
                        # Transfer destination would be configured or passed in parameters
                        transfer_dest = tool_params.get('destination', 'support_queue')
                        success = telephony_provider.transfer_call(call_id, transfer_dest)
                        
                        return JSONResponse(status_code=200, content={
                            "toolCallId": tool_call.get('toolCallId'),
                            "result": {"transferred": success, "destination": transfer_dest}
                        })
                    else:
                        return JSONResponse(status_code=200, content={
                            "toolCallId": tool_call.get('toolCallId'),
                            "result": {"transferred": False, "error": "Telephony provider not configured"}
                        })
                
                # Handle get_decision_tree_result tool call
                elif tool_name == 'get_decision_tree_result':
                    issue_type = tool_params.get('issue_type')
                    user_answer = tool_params.get('user_answer')
                    
                    if not decision_tree_engine.trees:
                        return JSONResponse(status_code=200, content={
                            "toolCallId": tool_call.get('toolCallId'),
                            "result": {"status": "error", "message": "No decision trees loaded"}
                        })
                        
                    try:
                        if not decision_tree_engine.current_issue_type and issue_type:
                            # Start a new troubleshooting session
                            tree_result = decision_tree_engine.start_troubleshooting(issue_type)
                            result_data = {
                                "status": "continue",
                                "question": tree_result["question"],
                                "options": tree_result["options"]
                            }
                        else:
                            # Process response in existing session
                            tree_result = decision_tree_engine.process_response(user_answer)
                            result_data = tree_result
                            
                        return JSONResponse(status_code=200, content={
                            "toolCallId": tool_call.get('toolCallId'),
                            "result": result_data
                        })
                    except Exception as e:
                        return JSONResponse(status_code=200, content={
                            "toolCallId": tool_call.get('toolCallId'),
                            "result": {"status": "error", "message": str(e)}
                        })
        
        # Handle call.start event
        elif event_type in ['call.start', 'call_start']:
            call_info = webhook_data.get('call') or {}
            print(f"[Vapi Webhook] Call started: {call_info.get('id')}")
            # Could log call start, initialize decision tree session, etc.
            
        # Handle call.end event
        elif event_type in ['call.end', 'call_end']:
            call_info = webhook_data.get('call') or {}
            print(f"[Vapi Webhook] Call ended: {call_info.get('id')}")
            # Could log call end, summarize conversation, etc.
            
        return JSONResponse(status_code=200, content={"status": "received", "eventType": event_type})
        
    except Exception as e:
        print(f"[Vapi Webhook] Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def handle_create_incident_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the create_servicenow_incident tool call from Vapi.ai."""
    if not snow_client:
        return {"error": "ServiceNow client not configured"}
        
    try:
        # Extract parameters from tool call
        first_name = params.get('first_name') or params.get('caller_first_name')
        last_name = params.get('last_name') or params.get('caller_last_name')
        short_description = params.get('short_description') or params.get('issue_description')
        
        if not first_name or not last_name:
            return {"error": "Missing caller name (first_name and last_name required)"}
            
        if not short_description:
            return {"error": "Missing issue description (short_description required)"}
            
        # Lookup user by name to get sys_id
        user = await snow_client.get_user_by_name(first_name, last_name)
        
        if not user:
            # Try email lookup if name fails
            email = params.get('caller_email')
            if email:
                user = await snow_client.get_user_by_email(email)
                
        if not user:
            return {"error": f"User not found for name: {first_name} {last_name}"}
            
        caller_sys_id = user.get('sys_id')
        
        # Check rate limits (if employee_id is available in params or user record)
        employee_id = user.get('employee_number') or user.get('u_employee_id')
        if employee_id:
            db_conn_str = config.get('database', {}).get('connection_string')
            if db_conn_str:
                allowed, limit_msg = check_rate_limit(employee_id, db_conn_str)
                if not allowed:
                    return {"error": f"Rate limit exceeded: {limit_msg}"}
                    
        # Verify employee active status (optional but recommended)
        is_active, verify_msg = await verify_employee_active_service_now(
            user_sys_id=caller_sys_id,
            instance_url=snow_client.base_url,
            headers={"Authorization": f"Bearer {await snow_client.get_access_token()}", "Accept": "application/json"}
        )
        
        if not is_active:
            return {"error": f"Employee status check failed: {verify_msg}"}
            
        # Create the incident
        impact = params.get('impact', '2')
        urgency = params.get('urgency', '2')
        
        incident = await snow_client.create_incident(
            caller_sys_id=caller_sys_id,
            short_description=short_description,
            impact=str(impact),
            urgency=str(urgency)
        )
        
        # Log the successful incident creation (audit trail)
        if config.get('database', {}).get('connection_string'):
            log_password_reset_attempt(
                employee_id=employee_id or caller_sys_id,
                user_sys_id=caller_sys_id,
                reset_method='incident_created_via_ai_agent',
                result='success',
                error_message=None,
                duration_ms=None,
                db_connection_string=config['database']['connection_string']
            )
            
        return {
            "status": "success",
            "incident_number": incident.get('number'),
            "sys_id": incident.get('sys_id'),
            "url": f"{snow_client.base_url}/nav_to.do?uri=incident.do?sys_id={incident.get('sys_id')}"
        }
        
    except Exception as e:
        print(f"[Incident Creation Tool Error]: {str(e)}")
        return {"error": f"Failed to create incident: {str(e)}"}


@app.post("/twilio/webhook")
async def twilio_webhook(request: Request):
    """
    Webhook endpoint for Twilio events.
    Returns TwiML responses for call routing and handling.
    """
    try:
        # In a real implementation, this would generate TwiML for call flow
        # For now, return a basic TwiML response that connects to the AI agent webhook
        
        twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Welcome to Sika Corp IT Support. Please describe your issue.</Say>
    <Gather numDigits="1" action="{config.get('webhooks', {}).get('base_url', 'https://api.yourcompany.com')}/twilio/gather-result" method="POST">
        <Say>Press 1 for network issues, 2 for password reset, 3 for software installation, or 4 to speak with a human agent.</Say>
    </Gather>
    <Redirect>{config.get('webhooks', {}).get('base_url', 'https://api.yourcompany.com')}/twilio/webhook</Redirect>
</Response>"""
        
        return XMLResponse(content=twiml_response, media_type="application/xml")
        
    except Exception as e:
        print(f"[Twilio Webhook] Processing error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/incidents/create")
async def create_incident_endpoint(request: Request):
    """Endpoint to create ServiceNow incidents programmatically (for testing or external triggers)."""
    if not snow_client:
        raise HTTPException(status_code=500, detail="ServiceNow client not configured")
        
    try:
        incident_data = await request.json()
        
        # Extract required fields
        caller_sys_id = incident_data.get('caller_sys_id') or incident_data.get('caller_id')
        short_description = incident_data.get('short_description') or incident_data.get('issue_description')
        
        if not caller_sys_id or not short_description:
            raise HTTPException(status_code=400, detail="Missing required fields: caller_sys_id and short_description")
            
        # Create the incident
        impact = incident_data.get('impact', '2')
        urgency = incident_data.get('urgency', '2')
        
        incident = await snow_client.create_incident(
            caller_sys_id=caller_sys_id,
            short_description=short_description,
            impact=str(impact),
            urgency=str(urgency)
        )
        
        return {
            "status": "success",
            "incident": incident,
            "number": incident.get('number'),
            "url": f"{snow_client.base_url}/nav_to.do?uri=incident.do?sys_id={incident.get('sys_id')}"
        }
    except Exception as e:
        print(f"[Incident Creation Error]: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create incident: {str(e)}")


# ── Salesforce Webhook Router (mounted at end) ───────────────────
app.include_router(sf_webhook_router)
