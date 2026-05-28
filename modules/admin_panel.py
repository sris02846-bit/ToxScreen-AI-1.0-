"""
Admin Panel Module
User management, usage stats, manual tier upgrades.
"""

import sys
import os
import pandas as pd
from datetime import datetime, date
from typing import Dict, List

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path, get_all_predictions, get_prediction_count
import sqlite3


def get_all_users() -> List[Dict]:
    """Get all registered users from database."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get users from subscriptions
    cursor.execute('SELECT username, tier, payment_id, start_date, is_active FROM subscriptions')
    users = {}
    for row in cursor.fetchall():
        users[row[0]] = {
            "username": row[0],
            "tier": row[1],
            "payment_id": row[2] or "N/A",
            "start_date": row[3],
            "is_active": row[4]
        }
    
    # Get usage stats for each user
    today = date.today().isoformat()
    for username in users:
        cursor.execute(
            'SELECT prediction_count FROM usage_tracking WHERE username = ? AND prediction_date = ?',
            (username, today)
        )
        result = cursor.fetchone()
        users[username]["daily_usage"] = result[0] if result else 0
        
        # Get total predictions
        cursor.execute('SELECT COUNT(*) FROM predictions WHERE user = ?', (username,))
        users[username]["total_predictions"] = cursor.fetchone()[0]
    
    conn.close()
    return list(users.values())


def get_platform_stats() -> Dict:
    """Get overall platform statistics."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total predictions
    cursor.execute('SELECT COUNT(*) FROM predictions')
    stats["total_predictions"] = cursor.fetchone()[0]
    
    # Today's predictions
    today = date.today().isoformat()
    cursor.execute('SELECT SUM(prediction_count) FROM usage_tracking WHERE prediction_date = ?', (today,))
    result = cursor.fetchone()[0]
    stats["today_predictions"] = result if result else 0
    
    # Active users
    cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE is_active = 1')
    stats["active_users"] = cursor.fetchone()[0]
    
    # Users by tier
    cursor.execute('SELECT tier, COUNT(*) FROM subscriptions WHERE is_active = 1 GROUP BY tier')
    stats["users_by_tier"] = {}
    for row in cursor.fetchall():
        stats["users_by_tier"][row[0]] = row[1]
    
    # Total API calls
    cursor.execute('SELECT SUM(api_calls) FROM usage_tracking')
    result = cursor.fetchone()[0]
    stats["total_api_calls"] = result if result else 0
    
    conn.close()
    return stats


def manual_upgrade_user(username: str, tier: str) -> Dict:
    """Manually upgrade or downgrade a user's tier."""
    valid_tiers = ["free", "pro", "enterprise"]
    
    if tier not in valid_tiers:
        return {"success": False, "message": f"Invalid tier. Must be: {valid_tiers}"}
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO subscriptions (username, tier, payment_id, start_date, is_active)
        VALUES (?, ?, 'manual_upgrade', ?, 1)
        ON CONFLICT(username)
        DO UPDATE SET tier = ?, payment_id = 'manual_upgrade', start_date = ?, is_active = 1
    ''', (username, tier, datetime.now().isoformat(), tier, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "username": username,
        "new_tier": tier,
        "message": f"User {username} manually upgraded to {tier}"
    }


def manual_downgrade_user(username: str) -> Dict:
    """Manually downgrade a user to free tier."""
    return manual_upgrade_user(username, "free")


def get_user_details(username: str) -> Dict:
    """Get detailed info for a specific user."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get subscription
    cursor.execute('SELECT * FROM subscriptions WHERE username = ?', (username,))
    sub = cursor.fetchone()
    
    # Get predictions
    cursor.execute('SELECT COUNT(*) FROM predictions WHERE user = ?', (username,))
    total_preds = cursor.fetchone()[0]
    
    # Get recent predictions
    cursor.execute(
        'SELECT smiles, druglikeness_score, risk_level, date FROM predictions WHERE user = ? ORDER BY date DESC LIMIT 10',
        (username,)
    )
    recent = cursor.fetchall()
    
    conn.close()
    
    return {
        "username": username,
        "subscription": {
            "tier": sub[1] if sub else "free",
            "payment_id": sub[2] if sub else "N/A",
            "start_date": sub[3] if sub else "N/A"
        },
        "total_predictions": total_preds,
        "recent_predictions": [
            {"smiles": r[0], "score": r[1], "risk": r[2], "date": r[3]}
            for r in recent
        ]
    }
