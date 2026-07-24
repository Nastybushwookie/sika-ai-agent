"""
Rate Limit Checker for IAM Password Reset Agent
Enforces max 3 resets per hour, max 3 per day per employee
"""
import psycopg2
from datetime import datetime, timedelta


def check_rate_limit(employee_id: str, db_connection_string: str) -> tuple[bool, str]:
    """
    Check if employee has exceeded rate limits for password resets.
    
    Returns: (bool, str) - (is_allowed, message_if_not_allowed)
    """
    try:
        conn = psycopg2.connect(db_connection_string)
        cursor = conn.cursor()
        
        # Check hourly limit (max 3 per hour)
        one_hour_ago = datetime.now() - timedelta(hours=1)
        cursor.execute("""
            SELECT COUNT(*) FROM password_reset_log 
            WHERE employee_id = %s AND created_at >= %s AND result = 'success'
        """, (employee_id, one_hour_ago))
        hourly_count = cursor.fetchone()[0]
        
        if hourly_count >= 3:
            conn.close()
            return False, "Rate limit exceeded: Maximum 3 password resets per hour allowed."
        
        # Check daily limit (max 3 per day)
        one_day_ago = datetime.now() - timedelta(days=1)
        cursor.execute("""
            SELECT COUNT(*) FROM password_reset_log 
            WHERE employee_id = %s AND created_at >= %s AND result = 'success'
        """, (employee_id, one_day_ago))
        daily_count = cursor.fetchone()[0]
        
        if daily_count >= 3:
            conn.close()
            return False, "Rate limit exceeded: Maximum 3 password resets per day allowed."
        
        conn.close()
        return True, ""
        
    except Exception as e:
        return False, f"Error checking rate limits: {str(e)}"


def check_rate_limit_webhook(employee_id: str, db_connection_string: str) -> tuple[bool, dict]:
    """
    Webhook handler version of rate limit checker.
    Returns appropriate HTTP response if rate limited.
    """
    allowed, message = check_rate_limit(employee_id, db_connection_string)
    
    if not allowed:
        return False, {
            "status_code": 429,
            "error": "Too Many Requests",
            "message": message
        }
    
    return True, {}