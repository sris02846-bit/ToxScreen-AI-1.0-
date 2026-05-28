"""
Continuous Learning Module
Feedback collection, model retraining, and automated updates.
"""

import pandas as pd
import numpy as np
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
import joblib

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path
from model_loader import get_models_dir


def collect_feedback(
    smiles: str,
    predicted_toxic: bool,
    actual_toxic: bool,
    user: str = "system",
    notes: str = ""
) -> Dict:
    """
    Collect user feedback for model improvement.
    
    Args:
        smiles: SMILES string
        predicted_toxic: Model prediction
        actual_toxic: Actual toxicity (from user/expert)
        user: Username
        notes: Additional notes
        
    Returns:
        Feedback record
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS model_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            smiles TEXT NOT NULL,
            predicted_toxic INTEGER,
            actual_toxic INTEGER,
            user TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        INSERT INTO model_feedback (smiles, predicted_toxic, actual_toxic, user, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (smiles, int(predicted_toxic), int(actual_toxic), user, notes))
    
    conn.commit()
    
    # Check if retraining is needed
    cursor.execute('SELECT COUNT(*) FROM model_feedback')
    count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "success": True,
        "total_feedback": count,
        "retrain_recommended": count >= 10
    }


def get_feedback_stats() -> Dict:
    """Get feedback statistics for model evaluation."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    try:
        df = pd.read_sql_query('SELECT * FROM model_feedback', conn)
        
        if len(df) == 0:
            return {"total": 0, "accuracy": 0, "needs_data": True}
        
        correct = (df['predicted_toxic'] == df['actual_toxic']).sum()
        accuracy = round(correct / len(df) * 100, 1)
        
        return {
            "total": len(df),
            "correct": int(correct),
            "incorrect": len(df) - int(correct),
            "accuracy": accuracy,
            "last_updated": df['created_at'].max() if 'created_at' in df.columns else None
        }
    except:
        return {"total": 0, "accuracy": 0}
    finally:
        conn.close()


def retrain_models_if_needed() -> Dict:
    """
    Check if retraining is needed and retrain models.
    
    Returns:
        Retraining status
    """
    stats = get_feedback_stats()
    
    if stats["total"] < 10:
        return {"retrained": False, "reason": f"Need 10+ feedback samples (have {stats['total']})"}
    
    if stats["accuracy"] > 80:
        return {"retrained": False, "reason": f"Accuracy already {stats['accuracy']}%"}
    
    # Retrain hepatotoxicity model
    try:
        from ml_model import train_hepatotoxicity_model
        model = train_hepatotoxicity_model()
        from model_loader import save_model
        save_model(model, "hepatotoxicity_model")
        
        return {
            "retrained": True,
            "model": "hepatotoxicity_model",
            "previous_accuracy": stats["accuracy"],
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"retrained": False, "error": str(e)}


def get_model_versions() -> Dict:
    """Get all model versions and timestamps."""
    models_dir = get_models_dir()
    versions = {}
    
    for model_file in os.listdir(models_dir):
        if model_file.endswith('.pkl'):
            path = os.path.join(models_dir, model_file)
            mtime = datetime.fromtimestamp(os.path.getmtime(path))
            size_kb = round(os.path.getsize(path) / 1024, 1)
            
            versions[model_file] = {
                "last_modified": mtime.isoformat(),
                "size_kb": size_kb,
                "days_since_update": (datetime.now() - mtime).days
            }
    
    return versions


def schedule_daily_updates() -> Dict:
    """
    Perform daily automated updates.
    - Clean old data
    - Backup database
    - Check model performance
    """
    results = {}
    
    # Backup
    try:
        from data_manager import backup_database
        backup = backup_database()
        results["backup"] = backup["success"]
    except:
        results["backup"] = False
    
    # Validate data
    try:
        from data_manager import validate_data
        validation = validate_data()
        results["data_health"] = validation["health"]
    except:
        results["data_health"] = "unknown"
    
    # Check feedback
    try:
        stats = get_feedback_stats()
        results["feedback_count"] = stats["total"]
        results["model_accuracy"] = stats["accuracy"]
    except:
        results["feedback_count"] = 0
    
    # Check for retraining
    retrain = retrain_models_if_needed()
    results["retrained"] = retrain.get("retrained", False)
    
    results["timestamp"] = datetime.now().isoformat()
    
    return results
