"""
Advanced Database Queries Module
Complex searches, filtering, sorting, and reporting system.
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path


def search_compounds(
    smiles: str = None,
    min_score: float = None,
    max_score: float = None,
    risk_level: str = None,
    user: str = None,
    date_from: str = None,
    date_to: str = None,
    sort_by: str = "date",
    sort_order: str = "DESC",
    limit: int = 100
) -> pd.DataFrame:
    """
    Advanced compound search with filtering and sorting.
    
    Args:
        smiles: Partial SMILES search
        min_score: Minimum drug-likeness score
        max_score: Maximum drug-likeness score
        risk_level: Filter by risk level
        user: Filter by username
        date_from: Start date (YYYY-MM-DD)
        date_to: End date (YYYY-MM-DD)
        sort_by: Column to sort by
        sort_order: ASC or DESC
        limit: Max results
        
    Returns:
        Filtered DataFrame
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    query = "SELECT * FROM predictions WHERE 1=1"
    params = []
    
    if smiles:
        query += " AND smiles LIKE ?"
        params.append(f"%{smiles}%")
    
    if min_score is not None:
        query += " AND druglikeness_score >= ?"
        params.append(min_score)
    
    if max_score is not None:
        query += " AND druglikeness_score <= ?"
        params.append(max_score)
    
    if risk_level:
        query += " AND risk_level = ?"
        params.append(risk_level)
    
    if user:
        query += " AND user = ?"
        params.append(user)
    
    if date_from:
        query += " AND date >= ?"
        params.append(date_from)
    
    if date_to:
        query += " AND date <= ?"
        params.append(date_to + " 23:59:59")
    
    # Validate sort column
    valid_columns = ["id", "smiles", "druglikeness_score", "risk_level", "date", "user"]
    if sort_by not in valid_columns:
        sort_by = "date"
    
    query += f" ORDER BY {sort_by} {sort_order} LIMIT {limit}"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    return df


def generate_report(
    report_type: str = "daily",
    user: str = None,
    days: int = 7
) -> Dict:
    """
    Generate analytical reports.
    
    Args:
        report_type: 'daily', 'weekly', 'user', 'risk'
        user: Username for user report
        days: Number of days to include
        
    Returns:
        Report dictionary
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    report = {
        "type": report_type,
        "generated": datetime.now().isoformat(),
        "data": {}
    }
    
    if report_type == "daily":
        # Daily prediction counts
        query = """
            SELECT prediction_date, SUM(prediction_count) as count
            FROM usage_tracking
            WHERE prediction_date >= date('now', ?)
            GROUP BY prediction_date
            ORDER BY prediction_date
        """
        df = pd.read_sql_query(query, conn, params=(f"-{days} days",))
        report["data"]["daily_counts"] = df.to_dict('records')
    
    elif report_type == "risk":
        # Risk distribution
        query = """
            SELECT risk_level, COUNT(*) as count,
                   AVG(druglikeness_score) as avg_score
            FROM predictions
            GROUP BY risk_level
        """
        df = pd.read_sql_query(query, conn)
        report["data"]["risk_distribution"] = df.to_dict('records')
    
    elif report_type == "user" and user:
        # User activity report
        query = """
            SELECT date(date) as day, COUNT(*) as predictions,
                   AVG(druglikeness_score) as avg_score
            FROM predictions
            WHERE user = ? AND date >= date('now', ?)
            GROUP BY date(date)
            ORDER BY day
        """
        df = pd.read_sql_query(query, conn, params=(user, f"-{days} days"))
        report["data"]["user_activity"] = df.to_dict('records')
    
    conn.close()
    return report


def get_statistics_summary() -> Dict:
    """Get comprehensive statistics summary."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total stats
    cursor.execute('SELECT COUNT(*) FROM predictions')
    stats["total_predictions"] = cursor.fetchone()[0]
    
    # Average score
    cursor.execute('SELECT AVG(druglikeness_score) FROM predictions')
    result = cursor.fetchone()[0]
    stats["avg_score"] = round(result, 1) if result else 0
    
    # Score distribution
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN druglikeness_score >= 80 THEN 1 END) as excellent,
            COUNT(CASE WHEN druglikeness_score >= 60 AND druglikeness_score < 80 THEN 1 END) as good,
            COUNT(CASE WHEN druglikeness_score >= 40 AND druglikeness_score < 60 THEN 1 END) as moderate,
            COUNT(CASE WHEN druglikeness_score < 40 THEN 1 END) as poor
        FROM predictions
    ''')
    row = cursor.fetchone()
    stats["score_distribution"] = {
        "excellent": row[0], "good": row[1],
        "moderate": row[2], "poor": row[3]
    }
    
    # Most common toxicophores
    cursor.execute('''
        SELECT most_similar_toxin, COUNT(*) as cnt
        FROM predictions
        WHERE most_similar_toxin IS NOT NULL AND most_similar_toxin != ''
        GROUP BY most_similar_toxin
        ORDER BY cnt DESC
        LIMIT 10
    ''')
    stats["top_toxins"] = [{"name": row[0], "count": row[1]} for row in cursor.fetchall()]
    
    conn.close()
    return stats
