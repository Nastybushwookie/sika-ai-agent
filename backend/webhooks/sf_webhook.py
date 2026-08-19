"""
Vapi function tool webhook handler for Salesforce operations.
This endpoint receives tool calls from Vapi and dispatches them to the appropriate
Salesforce REST operation.
"""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
import os
import sys

# Add parent path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.sf_oauth_client import SFOAuthClient, SFTokenStore
from integrations.sf_rest_client import SFRestClient
from fastapi import APIRouter

router = APIRouter()

# Global state — initialized on first request
_sf_oauth: SFOAuthClient = None
_sf_rest: SFRestClient = None


def _get_sf_clients() -> tuple:
    """Lazy initialize Salesforce clients from config."""
    global _sf_oauth, _sf_rest
    if _sf_oauth is None:
        # Load config
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    '..', 'config', 'settings.yaml')
        import yaml
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        sf_config = config.get('salesforce', {})
        sf_base_url = sf_config.get('base_url', 'https://login.salesforce.com')
        client_id = sf_config.get('client_id', os.environ.get('SF_CLIENT_ID', ''))
        client_secret = sf_config.get('client_secret', os.environ.get('SF_CLIENT_SECRET', ''))

        if not client_id or not client_secret:
            raise HTTPException(status_code=500, detail="Salesforce credentials not configured")

        token_file = sf_config.get('token_file')
        token_store = SFTokenStore(token_file=token_file) if token_file else SFTokenStore()
        _sf_oauth = SFOAuthClient(client_id=client_id, client_secret=client_secret,
                                   sf_base_url=sf_base_url, token_store=token_store)
        _sf_rest = SFRestClient(_sf_oauth)

    return _sf_oauth, _sf_rest


# ── Vapi Function Tool Endpoints ──────────────────────────────────

@router.post("/vapi/tools")
async def vapi_tools_webhook(request: Request):
    """
    Main Vapi function tool webhook.
    Receives tool calls from Vapi and returns results in Vapi's expected shape.
    """
    try:
        body = await request.json()
        tool_calls = body.get('toolCalls', [body]) if not isinstance(body.get('toolCalls'), list) else body.get('toolCalls', [])

        # Vapi may send a single tool call or wrapped in different shapes
        if not isinstance(tool_calls, list):
            tool_calls = [tool_calls]

        results = []
        for tc in tool_calls:
            tool_call_id = tc.get('toolCallId') or tc.get('id') or f"call_{id(tc)}"
            tool_name = tc.get('name', '')
            tool_params = tc.get('parameters', {}) or {}

            result = await _execute_sf_tool(tool_name, tool_params)
            results.append({
                "toolCallId": tool_call_id,
                "result": result
            })

        return JSONResponse(content={"results": results})

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"results": [{"toolCallId": "unknown", "result": {"ok": False, "error": str(e)}}]}
        )


async def _execute_sf_tool(tool_name: str, params: dict) -> dict:
    """Execute a Salesforce tool and return result."""
    oauth, rest = _get_sf_clients()

    tool_map = {
        'sf_create_lead': rest.create_lead,
        'sf_find_lead_or_contact': rest.find_lead_or_contact,
        'sf_create_task': rest.create_task,
        'sf_log_call_summary': rest.log_call_summary,
        'sf_create_contact': rest.create_contact,
        'sf_create_account': rest.create_account,
        'sf_query': rest.query,
        'sf_search': rest.search,
        'sf_describe': rest.describe_sobject,
        'sf_get_record': rest.get_record,
        'sf_update_record': rest.update_record,
        'sf_delete_record': rest.delete_record,
        'sf_list_records': rest.list_records,
        'sf_auth_url': lambda p: {'authorization_url': oauth.get_authorization_url(p.get('redirect_uri', ''))},
        'sf_check_auth': lambda p: {'authenticated': oauth.is_authenticated(), 'instance_url': oauth.token_store.instance_url},
        'sf_clear_auth': lambda p: (oauth.clear_tokens(), {'ok': True, 'message': 'Tokens cleared'}),
    }

    handler = tool_map.get(tool_name)
    if not handler:
        return {"ok": False, "error": f"Unknown tool: {tool_name}. Available: {list(tool_map.keys())}"}

    try:
        # Check auth for tools that need it
        needs_auth = tool_name not in ('sf_auth_url', 'sf_check_auth', 'sf_clear_auth')
        if needs_auth and not oauth.is_authenticated():
            return {
                "ok": False,
                "error": "Not authenticated. Complete OAuth flow at: " + oauth.get_authorization_url(
                    redirect_uri=params.get('callback_uri', 'http://localhost:8000/oauth/salesforce/callback')
                )
            }

        result = await handler(params)
        return result
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── OAuth Callback ───────────────────────────────────────────────

@router.post("/oauth/salesforce/callback")
async def sf_oauth_callback(request: Request):
    """
    OAuth2 authorization code callback.
    Receives the code from Salesforce and exchanges it for tokens.
    """
    try:
        oauth, rest = _get_sf_clients()
        body = await request.json()
        code = body.get('code') or body.get('authorization_code')

        if not code:
            # Try form data
            form = await request.form()
            code = form.get('code')

        if not code:
            return JSONResponse(
                status_code=400,
                content={"error": "No authorization code received"}
            )

        callback_uri = body.get('callback_uri') or body.get('redirect_uri') or 'http://localhost:8000/oauth/salesforce/callback'
        token_data = await oauth.exchange_code(code, callback_uri)

        return JSONResponse(content={
            "ok": True,
            "message": "Salesforce OAuth completed successfully",
            "instance_url": oauth.token_store.instance_url,
            "access_token_set": True,
        })
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"OAuth callback failed: {str(e)}"}
        )


# ── Quick Auth Check (no body needed) ────────────────────────────

@router.get("/salesforce/status")
async def sf_status():
    """Quick check: is Salesforce connected?"""
    try:
        oauth, rest = _get_sf_clients()
        return {
            "authenticated": oauth.is_authenticated(),
            "instance_url": oauth.token_store.instance_url,
            "token_expiring_soon": oauth.token_store.is_expired if oauth.token_store.access_token else False,
        }
    except Exception as e:
        return {"error": str(e), "authenticated": False}
