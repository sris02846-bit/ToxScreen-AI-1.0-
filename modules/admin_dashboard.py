"""
Admin Dashboard Module
Complete analytics panel with user management and platform statistics.
"""

import sys
import os
import pandas as pd
from datetime import datetime, date, timedelta
from typing import Dict, List

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path
import sqlite3


def get_dashboard_stats() -> Dict:
    """Get comprehensive dashboard statistics."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {
        "timestamp": datetime.now().isoformat(),
        "users": {},
        "predictions": {},
        "api": {},
        "revenue": {}
    }
    
    # Total users
    cursor.execute('SELECT COUNT(*) FROM subscriptions WHERE is_active = 1')
    stats["users"]["total_active"] = cursor.fetchone()[0]
    
    # Users by tier
    cursor.execute('SELECT tier, COUNT(*) FROM subscriptions WHERE is_active = 1 GROUP BY tier')
    stats["users"]["by_tier"] = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Total predictions
    cursor.execute('SELECT COUNT(*) FROM predictions')
    stats["predictions"]["total"] = cursor.fetchone()[0]
    
    # Today's predictions
    today = date.today().isoformat()
    cursor.execute('SELECT SUM(prediction_count) FROM usage_tracking WHERE prediction_date = ?', (today,))
    result = cursor.fetchone()[0]
    stats["predictions"]["today"] = result if result else 0
    
    # Last 7 days predictions
    predictions_7d = {}
    for i in range(7):
        d = (date.today() - timedelta(days=i)).isoformat()
        cursor.execute('SELECT SUM(prediction_count) FROM usage_tracking WHERE prediction_date = ?', (d,))
        result = cursor.fetchone()[0]
        predictions_7d[d] = result if result else 0
    stats["predictions"]["last_7_days"] = predictions_7d
    
    # Average drug-likeness score
    cursor.execute('SELECT AVG(druglikeness_score) FROM predictions')
    result = cursor.fetchone()[0]
    stats["predictions"]["avg_score"] = round(result, 1) if result else 0
    
    # Risk distribution
    cursor.execute('SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level')
    stats["predictions"]["risk_distribution"] = {row[0]: row[1] for row in cursor.fetchall()}
    
    # API usage
    cursor.execute('SELECT SUM(api_calls) FROM usage_tracking')
    result = cursor.fetchone()[0]
    stats["api"]["total_calls"] = result if result else 0
    
    # Revenue (simulated)
    stats["revenue"] = {
        "pro_users": stats["users"]["by_tier"].get("pro", 0),
        "enterprise_users": stats["users"]["by_tier"].get("enterprise", 0),
        "estimated_revenue": (stats["users"]["by_tier"].get("pro", 0) * 499) + 
                            (stats["users"]["by_tier"].get("enterprise", 0) * 1999)
    }
    
    conn.close()
    return stats


def get_user_activity_feed(limit: int = 20) -> List[Dict]:
    """Get recent user activity feed."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user, smiles, druglikeness_score, risk_level, date 
        FROM predictions 
        ORDER BY date DESC 
        LIMIT ?
    ''', (limit,))
    
    activities = []
    for row in cursor.fetchall():
        activities.append({
            "user": row[0],
            "smiles": row[1][:30],
            "score": row[2],
            "risk": row[3],
            "date": row[4]
        })
    
    conn.close()
    return activities


def get_top_compounds(limit: int = 10) -> List[Dict]:
    """Get most analyzed compounds."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT smiles, COUNT(*) as count, AVG(druglikeness_score) as avg_score
        FROM predictions 
        GROUP BY smiles 
        ORDER BY count DESC 
        LIMIT ?
    ''', (limit,))
    
    compounds = []
    for row in cursor.fetchall():
        compounds.append({
            "smiles": row[0][:40],
            "analyses": row[1],
            "avg_score": round(row[2], 1) if row[2] else 0
        })
    
    conn.close()
    return compounds
