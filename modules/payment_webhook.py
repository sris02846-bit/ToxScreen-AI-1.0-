"""
Razorpay Payment Webhook Module
Handles payment verification and auto-upgrades user tiers.
"""

import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database import set_user_tier, get_user_tier

# Razorpay webhook secret (use environment variable in production)
WEBHOOK_SECRET = "toxscreen_webhook_secret_2024"

# Payment link to tier mapping
PAYMENT_TIER_MAP = {
    "rzp.io/rzp/WxjqLwMo": "pro",
    "rzp.io/rzp/JafzcGNI": "enterprise"
}


def verify_razorpay_signature(webhook_body: str, signature: str) -> bool:
    """
    Verify Razorpay webhook signature.
    
    Args:
        webhook_body: Raw webhook body
        signature: X-Razorpay-Signature header
        
    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        WEBHOOK_SECRET.encode(),
        webhook_body.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature)


def process_payment_webhook(payload: Dict) -> Dict:
    """
    Process Razorpay payment webhook.
    Auto-upgrades user tier on successful payment.
    
    Args:
        payload: Webhook payload from Razorpay
        
    Returns:
        Result dictionary
    """
    event = payload.get("event", "")
    
    if event == "payment.captured":
        payment_data = payload.get("payload", {}).get("payment", {}).get("entity", {})
        
        payment_id = payment_data.get("id", "")
        amount = payment_data.get("amount", 0) / 100  # Convert from paise
        email = payment_data.get("email", "")
        contact = payment_data.get("contact", "")
        notes = payment_data.get("notes", {})
        username = notes.get("username", "")
        description = payment_data.get("description", "")
        
        # Determine tier from amount
        if amount >= 1999:
            tier = "enterprise"
        elif amount >= 499:
            tier = "pro"
        else:
            tier = "free"
        
        # Also check payment link if available
        payment_link = payment_data.get("payment_link_id", "")
        
        result = {
            "success": True,
            "payment_id": payment_id,
            "amount": amount,
            "email": email,
            "username": username,
            "tier": tier,
            "action": "upgraded" if username else "no_user_specified"
        }
        
        # Auto-upgrade user if username provided
        if username:
            set_user_tier(username, tier, payment_id)
            result["message"] = f"User {username} upgraded to {tier} tier"
        else:
            result["message"] = "Payment received but no username in notes"
        
        return result
    
    elif event == "payment.failed":
        return {
            "success": False,
            "message": "Payment failed",
            "event": event
        }
    
    return {
        "success": False,
        "message": f"Unhandled event: {event}"
    }


def manual_verify_payment(payment_id: str, username: str, tier: str) -> Dict:
    """
    Manually verify a payment and upgrade user.
    Used when webhook fails or for manual verification.
    
    Args:
        payment_id: Razorpay payment ID
        username: Username to upgrade
        tier: Tier to set (pro/enterprise)
        
    Returns:
        Result dictionary
    """
    set_user_tier(username, tier, payment_id)
    
    return {
        "success": True,
        "payment_id": payment_id,
        "username": username,
        "tier": tier,
        "message": f"Manual upgrade: {username} -> {tier}"
    }


def generate_ngrok_webhook_url(ngrok_url: str) -> str:
    """
    Generate webhook URL for ngrok.
    
    Args:
        ngrok_url: Ngrok public URL
        
    Returns:
        Full webhook URL
    """
    return f"{ngrok_url}/webhook/razorpay"


def get_upgrade_history(username: str) -> list:
    """
    Get payment/upgrade history for a user.
    
    Args:
        username: Username
        
    Returns:
        List of upgrade records
    """
    import sqlite3
    from database import get_db_path
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT tier, payment_id, start_date, is_active
        FROM subscriptions
        WHERE username = ?
        ORDER BY start_date DESC
    ''', (username,))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            "tier": row[0],
            "payment_id": row[1],
            "start_date": row[2],
            "is_active": row[3]
        })
    
    conn.close()
    return results
