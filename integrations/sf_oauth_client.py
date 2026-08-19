"""
Salesforce OAuth2 Client
Handles Authorization Code flow + Refresh Token for Sika Corp AI Agent.
Tokens are stored in memory (local dev) — persist to encrypted file for production.
"""
import httpx
import os
import json
import time
from typing import Optional, Dict, Any


class SFTokenStore:
    """Simple token storage — file-backed for local dev, memory for ephemeral."""

    def __init__(self, token_file: Optional[str] = None):
        if token_file is None:
            # Store in project data dir
            data_dir = os.path.join(os.path.dirname(__file__), '..', '.data')
            os.makedirs(data_dir, exist_ok=True)
            self.token_file = os.path.join(data_dir, 'sf_tokens.json')
        else:
            self.token_file = token_file
        self._tokens: Dict[str, Any] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'r') as f:
                    self._tokens = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._tokens = {}

    def _save(self):
        with open(self.token_file, 'w') as f:
            json.dump(self._tokens, f, indent=2)

    @property
    def access_token(self) -> Optional[str]:
        return self._tokens.get('access_token')

    @property
    def refresh_token(self) -> Optional[str]:
        return self._tokens.get('refresh_token')

    @property
    def instance_url(self) -> Optional[str]:
        return self._tokens.get('instance_url')

    @property
    def expires_at(self) -> Optional[float]:
        return self._tokens.get('expires_at')

    @property
    def is_expired(self) -> bool:
        if not self.expires_at:
            return True
        # Consider expired 60s before actual expiry
        return time.time() >= (self.expires_at - 60)

    def save_tokens(self, access_token: str, refresh_token: str,
                    instance_url: str, expires_in: int = 3600):
        self._tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'instance_url': instance_url,
            'expires_at': time.time() + expires_in,
        }
        self._save()

    def clear(self):
        self._tokens = {}
        self._save()


class SFOAuthClient:
    """Salesforce OAuth2 client with Authorization Code + Refresh Token flows."""

    def __init__(self, client_id: str, client_secret: str,
                 sf_base_url: str = 'https://login.salesforce.com',
                 token_store: Optional[SFTokenStore] = None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.sf_base_url = sf_base_url.rstrip('/')
        self.token_store = token_store or SFTokenStore()

    @property
    def auth_url(self) -> str:
        return f"{self.sf_base_url}/services/oauth2/authorize"

    @property
    def token_url(self) -> str:
        return f"{self.sf_base_url}/services/oauth2/token"

    def get_authorization_url(self, redirect_uri: str, scope: str = 'api refresh_token openid',
                              state: Optional[str] = None) -> str:
        """Build the authorization URL to redirect users to."""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'scope': scope,
        }
        if state:
            params['state'] = state
        # Build URL manually to avoid encoding issues
        query = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{self.auth_url}?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.token_url,
                data={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'redirect_uri': redirect_uri,
                }
            )
            response.raise_for_status()
            data = response.json()
            self.token_store.save_tokens(
                access_token=data['access_token'],
                refresh_token=data.get('refresh_token', ''),
                instance_url=data['instance_url'],
                expires_in=data.get('expires_in', 3600),
            )
            return data

    async def refresh_access_token(self) -> str:
        """Refresh the access token using the refresh token."""
        refresh_token = self.token_store.refresh_token
        if not refresh_token:
            raise ValueError("No refresh token available. Complete OAuth flow first.")

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                self.token_url,
                data={
                    'grant_type': 'refresh_token',
                    'refresh_token': refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                }
            )
            response.raise_for_status()
            data = response.json()
            self.token_store.save_tokens(
                access_token=data['access_token'],
                refresh_token=data.get('refresh_token', refresh_token),
                instance_url=data.get('instance_url', self.token_store.instance_url),
                expires_in=data.get('expires_in', 3600),
            )
            return data['access_token']

    async def get_access_token(self) -> str:
        """Get a valid access token, refreshing if necessary."""
        if self.token_store.is_expired and self.token_store.refresh_token:
            return await self.refresh_access_token()
        if self.token_store.access_token:
            return self.token_store.access_token
        raise ValueError("No access token available. Complete OAuth flow first.")

    def is_authenticated(self) -> bool:
        return bool(self.token_store.access_token and not self.token_store.is_expired)

    def clear_tokens(self):
        self.token_store.clear()
