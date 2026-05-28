"""
SQLite Database Module
Prediction storage, usage tracking, and subscription management.
"""

import sqlite3
import pandas as pd
from datetime import datetime, date
import os
from typing import List, Dict, Optional


def get_db_path() -> str:
    """Get the database file path."""
    return os.path.join(os.path.dirname(__file__), '..', 'toxscreen.db')


def init_database():
    """Initialize SQLite database and create all tables."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Predictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT DEFAULT 'default',
            smiles TEXT NOT NULL,
            druglikeness_score REAL,
            lipinski_violations INTEGER,
            veber_violations INTEGER,
            toxicity_score REAL,
            risk_level TEXT,
            result TEXT,
            ml_prediction TEXT,
            ml_confidence REAL,
            most_similar_toxin TEXT,
            toxin_similarity REAL,
            blockchain_tx TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Usage tracking table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usage_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            prediction_date DATE NOT NULL,
            prediction_count INTEGER DEFAULT 0,
            api_calls INTEGER DEFAULT 0,
            UNIQUE(username, prediction_date)
        )
    ''')
    
    # API keys table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'free',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    # Subscription table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            tier TEXT DEFAULT 'free',
            payment_id TEXT,
            start_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_date TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')
    
    conn.commit()
    conn.close()


def save_prediction(data: Dict) -> int:
    """Save a prediction to the database."""
    db_path = get_db_path()
    init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO predictions (
            user, smiles, druglikeness_score, lipinski_violations,
            veber_violations, toxicity_score, risk_level, result,
            ml_prediction, ml_confidence, most_similar_toxin,
            toxin_similarity, blockchain_tx, date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get('user', 'default'),
        data.get('smiles', ''),
        data.get('druglikeness_score'),
        data.get('lipinski_violations'),
        data.get('veber_violations'),
        data.get('toxicity_score'),
        data.get('risk_level'),
        data.get('result'),
        data.get('ml_prediction'),
        data.get('ml_confidence'),
        data.get('most_similar_toxin'),
        data.get('toxin_similarity'),
        data.get('blockchain_tx'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    
    conn.commit()
    record_id = cursor.lastrowid
    conn.close()
    return record_id


def get_all_predictions(username: str = None, limit: int = 50) -> pd.DataFrame:
    """Retrieve predictions from database."""
    db_path = get_db_path()
    init_database()
    conn = sqlite3.connect(db_path)
    
    if username:
        query = f'''
            SELECT * FROM predictions
            WHERE user = ?
            ORDER BY date DESC LIMIT {limit}
        '''
        df = pd.read_sql_query(query, conn, params=(username,))
    else:
        query = f'SELECT * FROM predictions ORDER BY date DESC LIMIT {limit}'
        df = pd.read_sql_query(query, conn)
    
    conn.close()
    return df


def get_prediction_count() -> int:
    """Get total number of predictions."""
    db_path = get_db_path()
    init_database()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM predictions')
    count = cursor.fetchone()[0]
    conn.close()
    return count


def update_blockchain_tx(record_id: int, tx_hash: str):
    """Update blockchain transaction hash."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE predictions SET blockchain_tx = ? WHERE id = ?', (tx_hash, record_id))
    conn.commit()
    conn.close()


def track_usage(username: str, count: int = 1) -> int:
    """Track daily prediction usage. Returns total count for today."""
    db_path = get_db_path()
    init_database()
    today = date.today().isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO usage_tracking (username, prediction_date, prediction_count)
        VALUES (?, ?, ?)
        ON CONFLICT(username, prediction_date)
        DO UPDATE SET prediction_count = prediction_count + ?
    ''', (username, today, count, count))
    
    conn.commit()
    
    cursor.execute(
        'SELECT prediction_count FROM usage_tracking WHERE username = ? AND prediction_date = ?',
        (username, today)
    )
    total = cursor.fetchone()[0]
    conn.close()
    return total


def get_daily_usage(username: str) -> int:
    """Get today's prediction count for a user."""
    db_path = get_db_path()
    init_database()
    today = date.today().isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT prediction_count FROM usage_tracking WHERE username = ? AND prediction_date = ?',
        (username, today)
    )
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0


def get_user_tier(username: str) -> str:
    """Get user subscription tier."""
    db_path = get_db_path()
    init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT tier FROM subscriptions WHERE username = ? AND is_active = 1', (username,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 'free'


def set_user_tier(username: str, tier: str, payment_id: str = None):
    """Set user subscription tier."""
    db_path = get_db_path()
    init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO subscriptions (username, tier, payment_id, start_date)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(username)
        DO UPDATE SET tier = ?, payment_id = ?, start_date = ?, is_active = 1
    ''', (username, tier, payment_id, datetime.now().isoformat(), tier, payment_id, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()


def get_tier_limits(tier: str) -> Dict:
    """Get prediction limits for a tier."""
    limits = {
        'free': {'daily_predictions': 5, 'batch_processing': False, 'api_calls': 100},
        'pro': {'daily_predictions': 100, 'batch_processing': True, 'api_calls': 1000},
        'enterprise': {'daily_predictions': 999999, 'batch_processing': True, 'api_calls': 999999}
    }
    return limits.get(tier, limits['free'])


def create_api_key(username: str, tier: str) -> str:
    """Create an API key for a user."""
    import hashlib
    import uuid
    
    db_path = get_db_path()
    init_database()
    
    api_key = hashlib.sha256(f"{username}{uuid.uuid4()}".encode()).hexdigest()[:32]
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO api_keys (username, api_key, tier)
        VALUES (?, ?, ?)
    ''', (username, api_key, tier))
    conn.commit()
    conn.close()
    
    return api_key


def validate_api_key(api_key: str) -> Optional[Dict]:
    """Validate an API key and return user info."""
    db_path = get_db_path()
    init_database()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, tier FROM api_keys
        WHERE api_key = ? AND is_active = 1
    ''', (api_key,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {'username': result[0], 'tier': result[1]}
    return None


def track_api_usage(username: str):
    """Track API usage for rate limiting."""
    db_path = get_db_path()
    init_database()
    today = date.today().isoformat()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO usage_tracking (username, prediction_date, api_calls)
        VALUES (?, ?, 1)
        ON CONFLICT(username, prediction_date)
        DO UPDATE SET api_calls = api_calls + 1
    ''', (username, today))
    
    conn.commit()
    conn.close()

def get_all_smiles_for_sync() -> list:
    """Get all unique SMILES for government DB syncing."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT smiles FROM predictions")
        smiles_list = [row[0] for row in cursor.fetchall()]
    except:
        smiles_list = []
    conn.close()
    return smiles_list

