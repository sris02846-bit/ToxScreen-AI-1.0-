"""
Database Optimization Module
Indexing, query optimization, and caching system.
"""

import sqlite3
import time
from functools import lru_cache
from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path

# Query cache
_QUERY_CACHE: Dict[str, tuple] = {}
CACHE_TTL = 300  # 5 minutes


def create_indexes():
    """Create database indexes for faster queries."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_date ON predictions(date)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_score ON predictions(druglikeness_score)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_risk ON predictions(risk_level)",
        "CREATE INDEX IF NOT EXISTS idx_predictions_smiles ON predictions(smiles)",
        "CREATE INDEX IF NOT EXISTS idx_usage_user_date ON usage_tracking(username, prediction_date)",
        "CREATE INDEX IF NOT EXISTS idx_subscriptions_tier ON subscriptions(tier)",
    ]
    
    for idx_sql in indexes:
        try:
            cursor.execute(idx_sql)
        except:
            pass
    
    conn.commit()
    conn.close()
    return {"indexed": len(indexes)}


def cached_query(query: str, params: tuple = (), ttl: int = None) -> List:
    """
    Execute cached database query.
    
    Args:
        query: SQL query
        params: Query parameters
        ttl: Cache time-to-live in seconds
        
    Returns:
        Query results
    """
    if ttl is None:
        ttl = CACHE_TTL
    
    cache_key = f"{query}_{str(params)}"
    
    # Check cache
    if cache_key in _QUERY_CACHE:
        result, timestamp = _QUERY_CACHE[cache_key]
        if time.time() - timestamp < ttl:
            return result
    
    # Execute query
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.close()
    
    # Store in cache
    _QUERY_CACHE[cache_key] = (result, time.time())
    
    return result


def clear_query_cache():
    """Clear the query cache."""
    _QUERY_CACHE.clear()
    return {"cleared": True}


def get_cache_stats() -> Dict:
    """Get cache statistics."""
    return {
        "cached_queries": len(_QUERY_CACHE),
        "cache_ttl": CACHE_TTL,
        "indexes_created": True
    }


def analyze_query_performance() -> Dict:
    """Analyze database query performance."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {}
    
    # Test queries
    test_queries = {
        "count_all": "SELECT COUNT(*) FROM predictions",
        "avg_score": "SELECT AVG(druglikeness_score) FROM predictions",
        "group_by_risk": "SELECT risk_level, COUNT(*) FROM predictions GROUP BY risk_level",
        "recent_100": "SELECT * FROM predictions ORDER BY date DESC LIMIT 100",
    }
    
    for name, query in test_queries.items():
        start = time.time()
        cursor.execute(query)
        cursor.fetchall()
        elapsed = round((time.time() - start) * 1000, 2)
        results[name] = f"{elapsed}ms"
    
    conn.close()
    return results
