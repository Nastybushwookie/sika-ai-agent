"""
Salesforce REST API client for Sika Corp AI Agent.
Wraps all Salesforce REST endpoints used by Vapi function tools.
"""
import httpx
from typing import Optional, Dict, Any, List
from .sf_oauth_client import SFOAuthClient


class SFRestClient:
    """Salesforce REST API client — thin wrapper over SFOAuthClient."""

    def __init__(self, oauth_client: SFOAuthClient):
        self.oauth = oauth_client

    @property
    def instance_url(self) -> str:
        url = self.oauth.token_store.instance_url
        if not url:
            raise ValueError("Not authenticated. Complete OAuth flow first.")
        return url.rstrip('/')

    def _base_url(self, api_version: str = 'v60.0') -> str:
        return f"{self.instance_url}/services/data/{api_version}"

    async def _get_token(self) -> str:
        return await self.oauth.get_access_token()

    async def _request(self, method: str, path: str,
                       data: Optional[Dict] = None,
                       params: Optional[Dict] = None,
                       api_version: str = 'v60.0') -> Dict[str, Any]:
        """Make an authenticated request to Salesforce."""
        token = await self._get_token()
        base = self._base_url(api_version)
        url = f"{base}/{path.lstrip('/')}"

        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }

        async with httpx.AsyncClient(timeout=30) as client:
            if method.upper() == 'GET':
                response = await client.get(url, headers=headers, params=params)
            elif method.upper() == 'POST':
                response = await client.post(url, headers=headers, json=data)
            elif method.upper() == 'PUT':
                response = await client.put(url, headers=headers, json=data)
            elif method.upper() == 'PATCH':
                response = await client.patch(url, headers=headers, json=data)
            elif method.upper() == 'DELETE':
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            if response.status_code == 401:
                # Token expired — try refresh once
                if self.oauth.token_store.refresh_token:
                    await self.oauth.refresh_access_token()
                    token = await self._get_token()
                    headers['Authorization'] = f'Bearer {token}'
                    if method.upper() == 'GET':
                        response = await client.get(url, headers=headers, params=params)
                    elif method.upper() == 'POST':
                        response = await client.post(url, headers=headers, json=data)
                    elif method.upper() == 'PUT':
                        response = await client.put(url, headers=headers, json=data)
                    elif method.upper() == 'PATCH':
                        response = await client.patch(url, headers=headers, json=data)
                    elif method.upper() == 'DELETE':
                        response = await client.delete(url, headers=headers)
                else:
                    raise ValueError("Access token expired and no refresh token available.")

            if response.status_code >= 400:
                try:
                    errors = response.json()
                except Exception:
                    errors = response.text
                raise RuntimeError(f"Salesforce API error ({response.status_code}): {errors}")

            if response.text:
                return response.json()
            return {}

    # ── Record Operations ─────────────────────────────────────────

    async def create_record(self, sobject: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a record (Lead, Contact, Account, etc.)."""
        return await self._request('POST', f'sobjects/{sobject}', data=data)

    async def get_record(self, sobject: str, record_id: str) -> Dict[str, Any]:
        """Get a single record by ID."""
        return await self._request('GET', f'sobjects/{sobject}/{record_id}')

    async def update_record(self, sobject: str, record_id: str,
                            data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a record."""
        return await self._request('PATCH', f'sobjects/{sobject}/{record_id}', data=data)

    async def delete_record(self, sobject: str, record_id: str) -> Dict[str, Any]:
        """Delete a record."""
        return await self._request('DELETE', f'sobjects/{sobject}/{record_id}')

    async def query(self, soql: str) -> List[Dict[str, Any]]:
        """Execute a SOQL query."""
        result = await self._request('GET', 'query', params={'q': soql})
        return result.get('records', [])

    async def search(self, query_text: str) -> List[Dict[str, Any]]:
        """Execute a SOSL search."""
        result = await self._request('GET', 'search', params={'q': query_text})
        return result.get('searchRecords', [])

    async def describe_sobject(self, sobject: str) -> Dict[str, Any]:
        """Get the schema/metadata for an object."""
        return await self._request('GET', f'sobjects/{sobject}/describe')

    async def list_records(self, sobject: str, limit: int = 200,
                           fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """List records with optional field selection."""
        field_list = ','.join(fields) if fields else '*'
        soql = f"SELECT {field_list} FROM {sobject} LIMIT {limit}"
        return await self.query(soql)

    # ── Vapi Tool Operations ──────────────────────────────────────

    async def create_lead(self, first_name: str, last_name: str,
                          company: Optional[str] = None,
                          email: Optional[str] = None,
                          phone: Optional[str] = None,
                          source: Optional[str] = None,
                          notes: Optional[str] = None) -> Dict[str, Any]:
        """Create a Salesforce Lead — used by Vapi tool sf_create_lead."""
        data = {
            'FirstName': first_name,
            'LastName': last_name,
        }
        if company:
            data['Company'] = company
        if email:
            data['Email'] = email
        if phone:
            data['Phone'] = phone
        if source:
            data['LeadSource'] = source
        if notes:
            data['Description'] = notes

        result = await self.create_record('Lead', data)
        return {
            'ok': True,
            'recordId': result.get('id'),
            'url': f"{self.instance_url}/lightning/r/Lead/{result.get('id')}/view",
            'data': result,
        }

    async def find_lead_or_contact(self, email: Optional[str] = None,
                                    phone: Optional[str] = None) -> Dict[str, Any]:
        """Search for an existing Lead or Contact by email or phone."""
        results = {'leads': [], 'contacts': [], 'found': False}

        if email:
            # Search Leads (escape single quotes to prevent SOQL injection)
            safe_email = email.replace("'", "''")
            leads = await self.query(
                f"SELECT Id, FirstName, LastName, Company, Email, Phone FROM Lead WHERE Email = '{safe_email}' LIMIT 5"
            )
            results['leads'] = leads

            # Search Contacts
            contacts = await self.query(
                f"SELECT Id, FirstName, LastName, Account.Name, Phone FROM Contact WHERE Email = '{safe_email}' LIMIT 5"
            )
            results['contacts'] = contacts

        if phone:
            safe_phone = phone.replace("'", "''")
            leads = await self.query(
                f"SELECT Id, FirstName, LastName, Company, Email, Phone FROM Lead WHERE Phone = '{safe_phone}' LIMIT 5"
            )
            results['leads'] = leads

            contacts = await self.query(
                f"SELECT Id, FirstName, LastName, Account.Name, Phone FROM Contact WHERE Phone = '{safe_phone}' LIMIT 5"
            )
            results['contacts'] = contacts

        results['found'] = len(results['leads']) + len(results['contacts']) > 0
        return results

    async def create_task(self, who_id: str, subject: str,
                          description: Optional[str] = None,
                          due_date: Optional[str] = None) -> Dict[str, Any]:
        """Create a Salesforce Task — used by Vapi tool sf_create_task."""
        data = {
            'WhoId': who_id,
            'Subject': subject,
        }
        if description:
            data['Description'] = description
        if due_date:
            data['WhatId'] = who_id  # Link task to same record
            data['ActivityDate'] = due_date

        result = await self.create_record('Task', data)
        return {
            'ok': True,
            'recordId': result.get('id'),
            'url': f"{self.instance_url}/lightning/r/Task/{result.get('id')}/view",
            'data': result,
        }

    async def log_call_summary(self, record_id: str, summary: str,
                                disposition: Optional[str] = None) -> Dict[str, Any]:
        """Log a call summary as a Note or Task on a record."""
        # Create a Task with the call summary
        task_data = {
            'WhatId': record_id,
            'Subject': f'Call Summary - {disposition or "General"}',
            'Description': summary,
            'Status': 'Completed',
            'Type': 'Call',
        }
        result = await self.create_record('Task', task_data)
        return {
            'ok': True,
            'recordId': result.get('id'),
            'url': f"{self.instance_url}/lightning/r/Task/{result.get('id')}/view",
            'data': result,
        }

    async def create_contact(self, first_name: str, last_name: str,
                              email: Optional[str] = None,
                              phone: Optional[str] = None,
                              account_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a Salesforce Contact."""
        data = {
            'FirstName': first_name,
            'LastName': last_name,
        }
        if email:
            data['Email'] = email
        if phone:
            data['Phone'] = phone
        if account_id:
            data['AccountId'] = account_id

        result = await self.create_record('Contact', data)
        return {
            'ok': True,
            'recordId': result.get('id'),
            'url': f"{self.instance_url}/lightning/r/Contact/{result.get('id')}/view",
            'data': result,
        }

    async def create_account(self, name: str,
                              phone: Optional[str] = None,
                              website: Optional[str] = None,
                              industry: Optional[str] = None) -> Dict[str, Any]:
        """Create a Salesforce Account."""
        data = {'Name': name}
        if phone:
            data['Phone'] = phone
        if website:
            data['Website'] = website
        if industry:
            data['Industry'] = industry

        result = await self.create_record('Account', data)
        return {
            'ok': True,
            'recordId': result.get('id'),
            'url': f"{self.instance_url}/lightning/r/Account/{result.get('id')}/view",
            'data': result,
        }
