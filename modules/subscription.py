"""
Subscription Management Module
Handles user tiers, limits, and payment integration.
"""

from typing import Dict, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database import get_user_tier, set_user_tier, get_daily_usage, get_tier_limits


# Razorpay payment links
PAYMENT_LINKS = {
    'pro': 'https://rzp.io/rzp/WxjqLwMo',
    'enterprise': 'https://rzp.io/rzp/JafzcGNI'
}

# Pricing
PRICING = {
    'free': {'price': 0, 'daily_limit': 5, 'batch': False, 'api_calls': 100},
    'pro': {'price': 499, 'daily_limit': 100, 'batch': True, 'api_calls': 1000},
    'enterprise': {'price': 1999, 'daily_limit': 999999, 'batch': True, 'api_calls': 999999}
}

# Demo credentials
DEMO_USERS = {
    'devil': {'password': 'devil@123ch', 'tier': 'pro'},
    'monkey': {'password': 'monkey@123ch', 'tier': 'enterprise'},
    'demo': {'password': 'demo123', 'tier': 'free'}
}


def check_usage_limit(username: str) -> Dict:
    """
    Check if user has remaining predictions for today.
    
    Args:
        username: Username to check
        
    Returns:
        Dictionary with usage info
    """
    tier = get_user_tier(username)
    limits = get_tier_limits(tier)
    daily_usage = get_daily_usage(username)
    
    remaining = limits['daily_predictions'] - daily_usage
    can_predict = remaining > 0
    
    return {
        'username': username,
        'tier': tier,
        'daily_limit': limits['daily_predictions'],
        'used_today': daily_usage,
        'remaining': max(0, remaining),
        'can_predict': can_predict,
        'can_batch': limits['batch_processing']
    }


def get_payment_link(tier: str) -> str:
    """Get Razorpay payment link for a tier."""
    return PAYMENT_LINKS.get(tier, '')


def upgrade_user(username: str, tier: str, payment_id: str = 'manual'):
    """Upgrade a user's subscription tier."""
    set_user_tier(username, tier, payment_id)


def get_subscription_info(username: str) -> Dict:
    """Get full subscription info for a user."""
    tier = get_user_tier(username)
    usage = check_usage_limit(username)
    pricing = PRICING.get(tier, PRICING['free'])
    
    return {
        'username': username,
        'current_tier': tier,
        'price': pricing['price'],
        'daily_limit': pricing['daily_limit'],
        'used_today': usage['used_today'],
        'remaining': usage['remaining'],
        'can_batch': pricing['batch'],
        'api_calls': pricing['api_calls'],
        'upgrade_link_pro': PAYMENT_LINKS['pro'] if tier == 'free' else None,
        'upgrade_link_enterprise': PAYMENT_LINKS['enterprise'] if tier in ['free', 'pro'] else None
    }
