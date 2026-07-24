"""
Password Reset Audit Log Logger
Logs password reset/unlock attempts to the password_reset_log table
"""
import psycopg2
from datetime import datetime


def log_password_reset_attempt(
    employee_id: str, 
    user_sys_id: str, 
    reset_method: str,  # 'on_prem_ad', 'azure_ad_only', 'hybrid_synced'
    result: str,        # 'success', 'failed'
    error_message: str = None,
    duration_ms: int = None,
    db_connection_string: str = None
) -> bool:
    """
    Log password reset attempt for audit compliance.
    
    Args:
        employee_id: Employee ID from ServiceNow sys_user table
        user_sys_id: ServiceNow sys_user record sys_id
        reset_method: Directory type path used ('on_prem_ad', 'azure_ad_only', 'hybrid_synced')
        result: 'success' or 'failed'
        error_message: Failure details for debugging (optional)
        duration_ms: Time taken for the operation in milliseconds (optional)
        db_connection_string: PostgreSQL connection string
    
    Returns:
        bool: True if logging was successful, False otherwise
    """
    try:
        conn = psycopg2.connect(db_connection_string)
        cursor = conn.cursor()
        
        # Insert into password_reset_log table
        cursor.execute("""
            INSERT INTO password_reset_log 
            (employee_id, user_sys_id, reset_method, result, error_message, duration_ms, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            employee_id, 
            user_sys_id, 
            reset_method, 
            result, 
            error_message, 
            duration_ms,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error logging password reset attempt: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False


def log_password_unlock_attempt(
    employee_id: str, 
    user_sys_id: str, 
    unlock_method: str,  # 'on_prem_ad', 'azure_ad_only', 'hybrid_synced'
    result: str,         # 'success', 'failed'
    error_message: str = None,
    duration_ms: int = None,
    db_connection_string: str = None
) -> bool:
    """
    Log account unlock attempt for audit compliance.
    Uses the same password_reset_log table but with method indicating unlock operation.
    """
    try:
        conn = psycopg2.connect(db_connection_string)
        cursor = conn.cursor()
        
        # Insert into password_reset_log table (using reset_method field to indicate unlock)
        cursor.execute("""
            INSERT INTO password_reset_log 
            (employee_id, user_sys_id, reset_method, result, error_message, duration_ms, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            employee_id, 
            user_sys_id, 
            f"unlock_{unlock_method}", 
            result, 
            error_message, 
            duration_ms,
            datetime.now()
        ))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error logging account unlock attempt: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        return False