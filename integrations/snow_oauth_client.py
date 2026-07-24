"""
ServiceNow OAuth2 Client Integration
Handles authentication and API calls to ServiceNow REST API
"""
import httpx
from datetime import datetime, timedelta
import os


class SnowOAuthClient:
    """ServiceNow OAuth2 client with automatic token refresh."""
    
    def __init__(self, base_url: str, client_id: str, client_secret: str):
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires_at = datetime.min
        
    async def get_access_token(self) -> str:
        """
        Get OAuth2 access token with automatic refresh.
        
        Refreshes 5 minutes before expiry to ensure no downtime during calls.
        """
        # Check if we have a valid token (with 5-minute safety buffer)
        now = datetime.now()
        if self.access_token and now < self.token_expires_at - timedelta(minutes=5):
            return self.access_token
        
        # Request new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/oauth_token.do",
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                }
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                
                # Calculate expiry (usually 3600 seconds)
                expires_in = token_data.get("expires_in", 3600)
                self.token_expires_at = now + timedelta(seconds=expires_in - 300)  # 5 min buffer
                
                return self.access_token
            else:
                raise Exception(f"OAuth2 token request failed: {response.text}")
    
    async def get_user_by_name(self, first_name: str, last_name: str) -> dict | None:
        """Look up user by name using OAuth2."""
        token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/now/table/sys_user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                params={
                    "sysparm_query": f"name={first_name}+AND+last_name={last_name}",
                    "sysparm_limit": 1,
                    "sysparm_fields": "sys_id,name,email"
                }
            )
            
            if response.status_code == 200:
                results = response.json()["result"]
                return results[0] if results else None
            return None
            
    async def get_user_by_email(self, email: str) -> dict | None:
        """Look up user by email using OAuth2."""
        token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/now/table/sys_user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json"
                },
                params={
                    "sysparm_query": f"email={email}",
                    "sysparm_limit": 1,
                    "sysparm_fields": "sys_id,name,email"
                }
            )
            
            if response.status_code == 200:
                results = response.json()["result"]
                return results[0] if results else None
            return None
    
    async def create_incident(self, caller_sys_id: str, short_description: str, 
                             impact: str = "2", urgency: str = "2") -> dict:
        """Create incident via OAuth2 API."""
        token = await self.get_access_token()
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/now/table/incident",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                json={
                    "caller_id": caller_sys_id,
                    "short_description": short_description,
                    "impact": impact,
                    "urgency": urgency
                }
            )
            
            if response.status_code == 201:
                return response.json()["result"]
            else:
                raise Exception(f"ServiceNow API error: {response.text}")
