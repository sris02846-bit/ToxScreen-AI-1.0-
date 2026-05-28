"""
Real-time Features Module
Live updates, notifications, collaboration, and sharing.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path


def create_notification(user: str, message: str, notif_type: str = "info") -> Dict:
    """
    Create a notification for a user.
    
    Args:
        user: Username
        message: Notification message
        notif_type: 'info', 'warning', 'success', 'error'
        
    Returns:
        Notification record
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create notifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO notifications (username, message, type)
        VALUES (?, ?, ?)
    ''', (user, message, notif_type))
    
    conn.commit()
    notif_id = cursor.lastrowid
    conn.close()
    
    return {"id": notif_id, "user": user, "message": message}


def get_notifications(user: str, unread_only: bool = False, limit: int = 20) -> List[Dict]:
    """Get user notifications."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    query = "SELECT * FROM notifications WHERE username = ?"
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC LIMIT ?"
    
    cursor.execute(query, (user, limit))
    notifications = []
    for row in cursor.fetchall():
        notifications.append({
            "id": row[0], "user": row[1], "message": row[2],
            "type": row[3], "read": bool(row[4]), "date": row[5]
        })
    
    conn.close()
    return notifications


def mark_notification_read(notif_id: int):
    """Mark a notification as read."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE notifications SET is_read = 1 WHERE id = ?', (notif_id,))
    conn.commit()
    conn.close()


def share_compound(owner: str, recipient: str, smiles: str, note: str = "") -> Dict:
    """
    Share a compound with another user.
    
    Args:
        owner: Owner username
        recipient: Recipient username
        smiles: SMILES string
        note: Optional note
        
    Returns:
        Share record
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create shares table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shared_compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            recipient TEXT NOT NULL,
            smiles TEXT NOT NULL,
            note TEXT,
            shared_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO shared_compounds (owner, recipient, smiles, note)
        VALUES (?, ?, ?, ?)
    ''', (owner, recipient, smiles, note))
    
    conn.commit()
    
    # Notify recipient
    create_notification(recipient, f"{owner} shared a compound with you", "info")
    
    conn.close()
    return {"success": True, "shared_with": recipient}


def get_shared_compounds(user: str) -> List[Dict]:
    """Get compounds shared with user."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM shared_compounds
        WHERE recipient = ?
        ORDER BY shared_date DESC
    ''', (user,))
    
    shares = []
    for row in cursor.fetchall():
        shares.append({
            "id": row[0], "owner": row[1], "smiles": row[3],
            "note": row[4], "date": row[5]
        })
    
    conn.close()
    return shares


def add_comment(user: str, smiles: str, comment: str) -> Dict:
    """
    Add a comment on a compound.
    
    Args:
        user: Username
        smiles: SMILES string
        comment: Comment text
        
    Returns:
        Comment record
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create comments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compound_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            smiles TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO compound_comments (username, smiles, comment)
        VALUES (?, ?, ?)
    ''', (user, smiles, comment))
    
    conn.commit()
    conn.close()
    
    return {"success": True, "user": user}


def get_comments(smiles: str) -> List[Dict]:
    """Get comments for a compound."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM compound_comments
        WHERE smiles = ?
        ORDER BY created_at DESC
    ''', (smiles,))
    
    comments = []
    for row in cursor.fetchall():
        comments.append({
            "id": row[0], "user": row[1], "comment": row[3], "date": row[4]
        })
    
    conn.close()
    return comments


def get_team_activity(team_users: List[str], limit: int = 20) -> List[Dict]:
    """Get recent activity for a team."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    placeholders = ','.join(['?' for _ in team_users])
    query = f'''
        SELECT * FROM predictions
        WHERE user IN ({placeholders})
        ORDER BY date DESC
        LIMIT ?
    '''
    
    df = pd.read_sql_query(query, conn, params=team_users + [limit])
    conn.close()
    
    return df.to_dict('records')


# Initialize database tables on import
def init_realtime_tables():
    """Initialize all real-time feature tables."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = [
        '''CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            message TEXT NOT NULL,
            type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS shared_compounds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner TEXT NOT NULL,
            recipient TEXT NOT NULL,
            smiles TEXT NOT NULL,
            note TEXT,
            shared_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
        '''CREATE TABLE IF NOT EXISTS compound_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            smiles TEXT NOT NULL,
            comment TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''',
    ]
    
    for table_sql in tables:
        cursor.execute(table_sql)
    
    conn.commit()
    conn.close()

# Auto-initialize
init_realtime_tables()
