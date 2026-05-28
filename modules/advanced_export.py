"""
Advanced Export Module
PDF reports, Excel exports, and API data dumps.
"""

import pandas as pd
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path


def export_to_excel(data: pd.DataFrame = None, filename: str = None) -> str:
    """
    Export data to Excel with formatting.
    
    Args:
        data: DataFrame to export
        filename: Output filename
        
    Returns:
        Path to Excel file
    """
    export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    if data is None:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        data = pd.read_sql_query('SELECT * FROM predictions ORDER BY date DESC', conn)
        conn.close()
    
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'toxscreen_export_{timestamp}.xlsx'
    
    filepath = os.path.join(export_dir, filename)
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        data.to_excel(writer, sheet_name='Predictions', index=False)
        
        # Summary sheet
        summary = pd.DataFrame({
            'Metric': ['Total Compounds', 'Average Score', 'High Risk', 'Low Risk'],
            'Value': [
                len(data),
                round(data['druglikeness_score'].mean(), 1) if 'druglikeness_score' in data.columns else 0,
                len(data[data['risk_level'].str.contains('High', na=False)]) if 'risk_level' in data.columns else 0,
                len(data[data['risk_level'].str.contains('Low', na=False)]) if 'risk_level' in data.columns else 0,
            ]
        })
        summary.to_excel(writer, sheet_name='Summary', index=False)
    
    return filepath


def export_to_json(data: pd.DataFrame = None) -> str:
    """Export data to JSON format."""
    export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    if data is None:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        data = pd.read_sql_query('SELECT * FROM predictions ORDER BY date DESC', conn)
        conn.close()
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = os.path.join(export_dir, f'toxscreen_export_{timestamp}.json')
    
    data.to_json(filepath, orient='records', indent=2)
    return filepath


def export_api_dump(format: str = 'json') -> str:
    """Create API-compatible data dump."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    query = '''
        SELECT smiles, druglikeness_score, risk_level, result,
               lipinski_violations, veber_violations, toxicity_score,
               ml_prediction, most_similar_toxin, date
        FROM predictions
        ORDER BY date DESC
        LIMIT 1000
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if format == 'json':
        filepath = os.path.join(export_dir, f'api_dump_{timestamp}.json')
        df.to_json(filepath, orient='records', indent=2)
    else:
        filepath = os.path.join(export_dir, f'api_dump_{timestamp}.csv')
        df.to_csv(filepath, index=False)
    
    return filepath


def export_summary_pdf() -> str:
    """Generate summary PDF report."""
    from fpdf import FPDF
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    # Get stats
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM predictions')
    total = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(druglikeness_score) FROM predictions')
    avg = cursor.fetchone()[0] or 0
    
    conn.close()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'ToxScreen-AI Summary Report', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8, f'Total Predictions: {total}', 0, 1)
    pdf.cell(0, 8, f'Average Score: {round(avg, 1)}', 0, 1)
    pdf.cell(0, 8, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1)
    
    export_dir = os.path.join(os.path.dirname(__file__), '..', 'exports')
    os.makedirs(export_dir, exist_ok=True)
    
    filepath = os.path.join(export_dir, f'summary_{datetime.now().strftime("%Y%m%d")}.pdf')
    pdf.output(filepath)
    return filepath
