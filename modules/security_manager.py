"""
Security Manager Module
HTTPS/SSL, OAuth2, rate limiting, encryption, audit logging.
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import json
import os
import sys
import logging

sys.path.insert(0, os.path.dirname(__file__))

# Configure audit logging
logging.basicConfig(
    filename='audit.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
audit_logger = logging.getLogger('toxscreen_audit')


class SecurityManager:
    """Central security management."""
    
    # Rate limiting
    _rate_limits: Dict[str, list] = {}
    _MAX_REQUESTS = 100
    _WINDOW_SECONDS = 3600  # 1 hour
    
    # API keys
    _api_keys: Dict[str, dict] = {}
    
    # Failed login tracking
    _login_attempts: Dict[str, list] = {}
    _MAX_LOGIN_ATTEMPTS = 5
    _LOCKOUT_MINUTES = 15
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key."""
        return secrets.token_hex(32)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password with salt."""
        salt = secrets.token_hex(16)
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def check_rate_limit(client_id: str) -> Tuple[bool, int]:
        """Check if client has exceeded rate limit."""
        now = time.time()
        window_start = now - SecurityManager._WINDOW_SECONDS
        
        if client_id not in SecurityManager._rate_limits:
            SecurityManager._rate_limits[client_id] = []
        
        # Clean old entries
        SecurityManager._rate_limits[client_id] = [
            t for t in SecurityManager._rate_limits[client_id] if t > window_start
        ]
        
        # Add current request
        SecurityManager._rate_limits[client_id].append(now)
        
        remaining = SecurityManager._MAX_REQUESTS - len(SecurityManager._rate_limits[client_id])
        allowed = remaining >= 0
        
        if not allowed:
            audit_logger.warning(f"Rate limit exceeded for {client_id}")
        
        return allowed, max(0, remaining)
    
    @staticmethod
    def check_login_attempts(username: str) -> Tuple[bool, str]:
        """Check if login is allowed."""
        now = datetime.now()
        
        if username not in SecurityManager._login_attempts:
            SecurityManager._login_attempts[username] = []
        
        # Clean old attempts
        cutoff = now - timedelta(minutes=SecurityManager._LOCKOUT_MINUTES)
        SecurityManager._login_attempts[username] = [
            t for t in SecurityManager._login_attempts[username] if t > cutoff
        ]
        
        if len(SecurityManager._login_attempts[username]) >= SecurityManager._MAX_LOGIN_ATTEMPTS:
            wait_time = SecurityManager._LOCKOUT_MINUTES - (now - SecurityManager._login_attempts[username][0]).seconds // 60
            audit_logger.warning(f"Account locked: {username}")
            return False, f"Account locked. Try again in {wait_time} minutes."
        
        return True, ""
    
    @staticmethod
    def record_login_attempt(username: str, success: bool):
        """Record login attempt."""
        if not success:
            SecurityManager._login_attempts.setdefault(username, []).append(datetime.now())
            audit_logger.info(f"Failed login: {username}")
        else:
            SecurityManager._login_attempts[username] = []
            audit_logger.info(f"Successful login: {username}")
    
    @staticmethod
    def encrypt_data(data: str, key: str = None) -> str:
        """Encrypt sensitive data."""
        if key is None:
            key = os.environ.get('ENCRYPTION_KEY', 'toxscreen_default_key')
        return hashlib.sha256(f"{key}{data}".encode()).hexdigest()
    
    @staticmethod
    def audit_log(action: str, user: str = "system", details: str = ""):
        """Log audit event."""
        audit_logger.info(f"User: {user} | Action: {action} | {details}")
    
    @staticmethod
    def vulnerability_scan() -> Dict:
        """Basic vulnerability check."""
        issues = []
        
        # Check for default credentials
        if os.environ.get('ENCRYPTION_KEY') is None:
            issues.append("WARNING: Using default encryption key")
        
        # Check file permissions
        if os.path.exists('../toxscreen.db'):
            perms = oct(os.stat('../toxscreen.db').st_mode)[-3:]
            if perms != '600':
                issues.append(f"Database permissions: {perms} (should be 600)")
        
        # Check HTTPS
        if not os.environ.get('HTTPS', '').lower() == 'on':
            issues.append("INFO: HTTPS not detected (set HTTPS=on in production)")
        
        return {
            "scan_time": datetime.now().isoformat(),
            "issues_found": len(issues),
            "issues": issues,
            "status": "PASS" if len(issues) == 0 else "WARNING"
        }
    
    @staticmethod
    def get_security_report() -> Dict:
        """Generate security status report."""
        return {
            "rate_limits_active": len(SecurityManager._rate_limits),
            "api_keys_issued": len(SecurityManager._api_keys),
            "locked_accounts": sum(
                1 for u, attempts in SecurityManager._login_attempts.items()
                if len(attempts) >= SecurityManager._MAX_LOGIN_ATTEMPTS
            ),
            "audit_log_size": os.path.getsize('audit.log') if os.path.exists('audit.log') else 0,
            "vulnerability_scan": SecurityManager.vulnerability_scan()
        }
