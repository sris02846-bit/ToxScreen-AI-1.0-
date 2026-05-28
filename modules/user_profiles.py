"""
User Profiles Module
User profile management, saved compounds, and history tracking.
"""

import sys
import os
import pandas as pd
from datetime import datetime, date
from typing import Dict, List, Optional
import hashlib

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path
import sqlite3


def create_user_profile(username: str, email: str, organization: str = "") -> Dict:
    """
    Create or update user profile.
    
    Args:
        username: Username
        email: Email address
        organization: Organization name
        
    Returns:
        Profile data
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create profiles table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profiles (
            username TEXT PRIMARY KEY,
            email TEXT,
            organization TEXT,
            joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            avatar_hash TEXT,
            preferences TEXT
        )
    ''')
    
    # Insert or update profile
    cursor.execute('''
        INSERT INTO user_profiles (username, email, organization, last_login)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(username) DO UPDATE SET
            email = ?,
            organization = ?,
            last_login = ?
    ''', (username, email, organization, datetime.now().isoformat(),
          email, organization, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    return get_user_profile(username)


def get_user_profile(username: str) -> Dict:
    """Get user profile data."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM user_profiles WHERE username = ?', (username,))
    row = cursor.fetchone()
    
    if row:
        profile = {
            "username": row[0],
            "email": row[1],
            "organization": row[2] or "Not set",
            "joined_date": row[3],
            "last_login": row[4],
            "preferences": row[6] or "{}"
        }
    else:
        profile = {
            "username": username,
            "email": "Not set",
            "organization": "Not set",
            "joined_date": datetime.now().isoformat(),
            "last_login": datetime.now().isoformat(),
            "preferences": "{}"
        }
    
    conn.close()
    return profile


def get_user_stats(username: str) -> Dict:
    """Get comprehensive user statistics."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total predictions
    cursor.execute('SELECT COUNT(*) FROM predictions WHERE user = ?', (username,))
    stats["total_predictions"] = cursor.fetchone()[0]
    
    # Today's predictions
    today = date.today().isoformat()
    cursor.execute(
        'SELECT prediction_count FROM usage_tracking WHERE username = ? AND prediction_date = ?',
        (username, today)
    )
    result = cursor.fetchone()
    stats["today_predictions"] = result[0] if result else 0
    
    # Average score
    cursor.execute(
        'SELECT AVG(druglikeness_score) FROM predictions WHERE user = ?',
        (username,)
    )
    result = cursor.fetchone()[0]
    stats["avg_score"] = round(result, 1) if result else 0
    
    # Risk distribution
    cursor.execute(
        'SELECT risk_level, COUNT(*) FROM predictions WHERE user = ? GROUP BY risk_level',
        (username,)
    )
    stats["risk_distribution"] = {row[0]: row[1] for row in cursor.fetchall()}
    
    # Most analyzed SMILES
    cursor.execute('''
        SELECT smiles, COUNT(*) as cnt 
        FROM predictions 
        WHERE user = ? 
        GROUP BY smiles 
        ORDER BY cnt DESC 
        LIMIT 5
    ''', (username,))
    stats["top_compounds"] = [{"smiles": row[0][:30], "count": row[1]} for row in cursor.fetchall()]
    
    # Subscription info
    cursor.execute(
        'SELECT tier, start_date FROM subscriptions WHERE username = ? AND is_active = 1',
        (username,)
    )
    sub = cursor.fetchone()
    stats["subscription"] = {
        "tier": sub[0] if sub else "free",
        "since": sub[1] if sub else "N/A"
    }
    
    conn.close()
    return stats


def get_user_history(username: str, limit: int = 50) -> pd.DataFrame:
    """
    Get user prediction history.
    
    Args:
        username: Username
        limit: Max records
        
    Returns:
        DataFrame of history
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    query = f'''
        SELECT id, smiles, druglikeness_score, lipinski_violations,
               veber_violations, toxicity_score, risk_level, result,
               ml_prediction, most_similar_toxin, date
        FROM predictions
        WHERE user = ?
        ORDER BY date DESC
        LIMIT {limit}
    '''
    
    df = pd.read_sql_query(query, conn, params=(username,))
    conn.close()
    
    return df


def save_compound(username: str, smiles: str, name: str = "") -> Dict:
    """Save a compound to user's favorites."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create saved_compounds table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            smiles TEXT NOT NULL,
            name TEXT,
            saved_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            UNIQUE(username, smiles)
        )
    ''')
    
    try:
        cursor.execute('''
            INSERT INTO saved_compounds (username, smiles, name)
            VALUES (?, ?, ?)
        ''', (username, smiles, name))
        conn.commit()
        result = {"success": True, "message": "Compound saved"}
    except sqlite3.IntegrityError:
        result = {"success": False, "message": "Compound already saved"}
    
    conn.close()
    return result


def get_saved_compounds(username: str) -> pd.DataFrame:
    """Get user's saved compounds."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT smiles, name, saved_date, notes 
        FROM saved_compounds 
        WHERE username = ? 
        ORDER BY saved_date DESC
    ''', (username,))
    
    rows = cursor.fetchall()
    df = pd.DataFrame(rows, columns=['SMILES', 'Name', 'Saved Date', 'Notes']) if rows else pd.DataFrame()
    
    conn.close()
    return df


def get_user_badges(username: str) -> List[Dict]:
    """Get achievement badges for user."""
    stats = get_user_stats(username)
    badges = []
    
    if stats["total_predictions"] >= 1:
        badges.append({"name": "First Analysis", "icon": "🔬", "description": "Completed first compound analysis"})
    if stats["total_predictions"] >= 10:
        badges.append({"name": "Power User", "icon": "⚡", "description": "Analyzed 10+ compounds"})
    if stats["total_predictions"] >= 100:
        badges.append({"name": "Centurion", "icon": "💯", "description": "Analyzed 100+ compounds"})
    if stats["subscription"]["tier"] == "pro":
        badges.append({"name": "Pro Member", "icon": "⭐", "description": "Upgraded to Pro"})
    if stats["subscription"]["tier"] == "enterprise":
        badges.append({"name": "Enterprise", "icon": "👑", "description": "Enterprise member"})
    
    return badges
