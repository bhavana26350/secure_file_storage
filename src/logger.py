import os
import datetime

LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'security_audit.log')

def log_security_event(event_type: str, details: str):
    """
    Appends a security event to the audit log.
    Simulates enterprise SIEM logging for Retail Security.
    """
    timestamp = datetime.datetime.now().isoformat()
    log_entry = f"[{timestamp}] [{event_type.upper()}] {details}\n"
    
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry)
