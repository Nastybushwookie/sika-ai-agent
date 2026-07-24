"""
HR Status Verification for Password Reset/Unlock Operations
Checks if user is an active employee in ServiceNow/HR system before any reset/unlock operation
"""
import psycopg2
from datetime import datetime, timedelta
import httpx


async def verify_employee_active_service_now(user_sys_id: str, instance_url: str, headers: dict) -> tuple[bool, str]:
    """
    Check if user is an active employee in ServiceNow/HR system
    
    Returns: (bool, str) - (is_active, message)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{instance_url}/api/now/table/sys_user/{user_sys_id}",
                headers=headers,
                params={"sysparm_fields": "active,u_termination_date"}
            )
        
        if response.status_code != 200:
            return False, f"Failed to look up user in ServiceNow: {response.text}"
        
        user_data = response.json()["result"]
        
        if not user_data.get("active", True):
            return False, f"Account {user_sys_id} is marked as inactive. Cannot reset password for terminated accounts."
        
        termination_date = user_data.get("u_termination_date")
        if termination_date:
            # Parse termination date
            try:
                term_dt = datetime.fromisoformat(termination_date.replace("Z", "+00:00"))
                days_since = (datetime.now() - term_dt).days
                
                # Allow resets within 30 days of termination (grace period)
                if days_since > 30:
                    return False, f"Account was terminated {days_since} days ago. Contact HR for reactivation."
            except ValueError:
                return False, f"Invalid termination date format: {termination_date}"
        
        return True, "User is active and eligible for password reset"
        
    except Exception as e:
        return False, f"Error verifying employee active status: {str(e)}"


async def verify_employee_active_azure(user_principal_name: str, graph_token: str) -> tuple[bool, str]:
    """
    Check Microsoft Graph for Azure AD user account status
    
    Returns: (bool, str) - (is_active, message)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://graph.microsoft.com/v1.0/users/{user_principal_name}/accountEnabled",
                headers={"Authorization": f"Bearer {graph_token}"}
            )
            
        if response.status_code == 200:
            is_active = response.json()
            return is_active, "Account is active in Azure AD"
        else:
            return False, f"Azure AD account lookup failed: {response.text}"
            
    except Exception as e:
        return False, f"Error checking Azure AD account status: {str(e)}"


def verify_employee_active_ad_powershell(sam_account_name: str, powershell_script: str) -> tuple[bool, str]:
    """
    Check on-prem Active Directory via PowerShell (called from ServiceNow flow or VPS endpoint)
    
    Returns: (bool, str) - (is_active, message)
    """
    try:
        # This would typically be executed via a PowerShell endpoint or ServiceNow Now Platform Script Execution
        # For demonstration purposes, we'll simulate the result
        
        # In a real implementation, this would execute the powershell_script against the domain controller
        # and check if the account is enabled and not expired
        
        # Simulated successful response for active account
        return True, "Account is active in on-prem AD"
        
    except Exception as e:
        return False, f"On-prem AD check failed: {str(e)}"