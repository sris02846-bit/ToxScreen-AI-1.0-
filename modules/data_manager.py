"""
Data Management Module
Backup, validation, and data cleaning system.
"""

import sqlite3
import pandas as pd
import json
import os
import shutil
from datetime import datetime
from typing import Dict, List
import sys

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path


def backup_database() -> Dict:
    """
    Create a backup of the database.
    
    Returns:
        Backup result dictionary
    """
    db_path = get_db_path()
    backup_dir = os.path.join(os.path.dirname(__file__), '..', 'backups')
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f'toxscreen_backup_{timestamp}.db')
    
    try:
        shutil.copy2(db_path, backup_path)
        
        # Also export to CSV
        conn = sqlite3.connect(db_path)
        df = pd.read_sql_query('SELECT * FROM predictions', conn)
        csv_path = os.path.join(backup_dir, f'toxscreen_export_{timestamp}.csv')
        df.to_csv(csv_path, index=False)
        conn.close()
        
        return {
            "success": True,
            "backup_path": backup_path,
            "csv_path": csv_path,
            "records": len(df),
            "timestamp": timestamp
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def validate_data() -> Dict:
    """
    Validate database integrity and clean invalid records.
    
    Returns:
        Validation results
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {
        "total_records": 0,
        "valid_records": 0,
        "invalid_records": 0,
        "issues": []
    }
    
    # Check predictions table
    cursor.execute('SELECT COUNT(*) FROM predictions')
    results["total_records"] = cursor.fetchone()[0]
    
    # Check for NULL SMILES
    cursor.execute('SELECT COUNT(*) FROM predictions WHERE smiles IS NULL OR smiles = ""')
    null_smiles = cursor.fetchone()[0]
    if null_smiles > 0:
        results["issues"].append(f"{null_smiles} records with NULL/empty SMILES")
        results["invalid_records"] += null_smiles
    
    # Check for invalid scores
    cursor.execute('SELECT COUNT(*) FROM predictions WHERE druglikeness_score < 0 OR druglikeness_score > 100')
    invalid_scores = cursor.fetchone()[0]
    if invalid_scores > 0:
        results["issues"].append(f"{invalid_scores} records with invalid scores")
        results["invalid_records"] += invalid_scores
    
    results["valid_records"] = results["total_records"] - results["invalid_records"]
    results["health"] = "Good" if results["invalid_records"] == 0 else "Needs cleaning"
    
    conn.close()
    return results


def clean_database() -> Dict:
    """
    Clean invalid records from database.
    
    Returns:
        Cleaning results
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    results = {"cleaned": 0}
    
    # Remove NULL SMILES
    cursor.execute('DELETE FROM predictions WHERE smiles IS NULL OR smiles = ""')
    results["null_smiles_removed"] = cursor.rowcount
    
    # Remove invalid scores
    cursor.execute('DELETE FROM predictions WHERE druglikeness_score < 0 OR druglikeness_score > 100')
    results["invalid_scores_removed"] = cursor.rowcount
    
    results["total_cleaned"] = results["null_smiles_removed"] + results["invalid_scores_removed"]
    
    conn.commit()
    conn.close()
    
    return results


def export_data(format: str = "csv") -> str:
    """
    Export database to various formats.
    
    Args:
        format: 'csv' or 'json'
        
    Returns:
        File path
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM predictions', conn)
    conn.close()
    
    export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == "json":
        path = os.path.join(export_dir, f'toxscreen_export_{timestamp}.json')
        df.to_json(path, orient='records', indent=2)
    else:
        path = os.path.join(export_dir, f'toxscreen_export_{timestamp}.csv')
        df.to_csv(path, index=False)
    
    return path
