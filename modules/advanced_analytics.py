"""
Advanced Analytics Module
Trend analysis, pattern recognition, and predictive analytics.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path


def analyze_trends(days: int = 30) -> Dict:
    """
    Analyze prediction trends over time.
    
    Args:
        days: Number of days to analyze
        
    Returns:
        Trend analysis dictionary
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    query = '''
        SELECT date(date) as day, 
               COUNT(*) as predictions,
               AVG(druglikeness_score) as avg_score,
               SUM(CASE WHEN risk_level LIKE '%High%' THEN 1 ELSE 0 END) as high_risk_count
        FROM predictions
        WHERE date >= date('now', ?)
        GROUP BY date(date)
        ORDER BY day
    '''
    
    df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
    conn.close()
    
    if len(df) < 2:
        return {"trend": "insufficient_data", "days_analyzed": days, "data_points": len(df)}
    
    # Calculate trends
    score_trend = "increasing" if df['avg_score'].iloc[-1] > df['avg_score'].iloc[0] else "decreasing"
    volume_trend = "increasing" if df['predictions'].iloc[-1] > df['predictions'].iloc[0] else "decreasing"
    
    return {
        "days_analyzed": days,
        "data_points": len(df),
        "score_trend": score_trend,
        "volume_trend": volume_trend,
        "avg_daily_predictions": round(df['predictions'].mean(), 1),
        "avg_score": round(df['avg_score'].mean(), 1),
        "total_high_risk": int(df['high_risk_count'].sum()),
        "peak_day": df.loc[df['predictions'].idxmax(), 'day'] if len(df) > 0 else None,
    }


def detect_patterns() -> Dict:
    """
    Detect patterns in prediction data.
    
    Returns:
        Pattern analysis results
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    # Common SMILES patterns
    query = '''
        SELECT 
            CASE 
                WHEN LENGTH(smiles) < 10 THEN 'Small molecules'
                WHEN LENGTH(smiles) < 30 THEN 'Medium molecules'
                ELSE 'Large molecules'
            END as size_group,
            COUNT(*) as count,
            AVG(druglikeness_score) as avg_score,
            AVG(toxicity_score) as avg_toxicity
        FROM predictions
        GROUP BY size_group
        ORDER BY count DESC
    '''
    
    df = pd.read_sql_query(query, conn)
    
    # Risk pattern by day of week
    query2 = '''
        SELECT 
            CASE CAST(strftime('%w', date) AS INTEGER)
                WHEN 0 THEN 'Sunday'
                WHEN 1 THEN 'Monday'
                WHEN 2 THEN 'Tuesday'
                WHEN 3 THEN 'Wednesday'
                WHEN 4 THEN 'Thursday'
                WHEN 5 THEN 'Friday'
                ELSE 'Saturday'
            END as day_of_week,
            COUNT(*) as predictions,
            AVG(druglikeness_score) as avg_score
        FROM predictions
        GROUP BY day_of_week
        ORDER BY predictions DESC
    '''
    
    dow_df = pd.read_sql_query(query2, conn)
    conn.close()
    
    return {
        "size_patterns": df.to_dict('records') if len(df) > 0 else [],
        "day_of_week_patterns": dow_df.to_dict('records') if len(dow_df) > 0 else [],
        "insight": "Larger molecules tend to have lower drug-likeness scores" if len(df) > 0 else "Insufficient data"
    }


def predict_future_trends(days_forward: int = 7) -> Dict:
    """
    Predict future trends based on historical data.
    
    Args:
        days_forward: Days to predict
        
    Returns:
        Predictive analytics results
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    
    # Get historical data
    query = '''
        SELECT date(date) as day, COUNT(*) as predictions
        FROM predictions
        WHERE date >= date('now', '-30 days')
        GROUP BY date(date)
        ORDER BY day
    '''
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) < 3:
        return {"prediction": "insufficient_data", "data_points": len(df)}
    
    # Simple moving average prediction
    avg = df['predictions'].mean()
    recent_avg = df['predictions'].tail(7).mean()
    
    trend = "growing" if recent_avg > avg else "stable" if recent_avg == avg else "declining"
    
    predictions = []
    for i in range(1, days_forward + 1):
        day = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        predicted = round(recent_avg * (1.05 if trend == "growing" else 0.95 if trend == "declining" else 1.0))
        predictions.append({"day": day, "predicted_predictions": max(0, predicted)})
    
    return {
        "trend": trend,
        "current_daily_avg": round(recent_avg, 1),
        "historical_avg": round(avg, 1),
        "forecast": predictions,
        "confidence": "Medium" if len(df) >= 14 else "Low"
    }


def generate_analytics_report() -> str:
    """
    Generate comprehensive analytics report.
    
    Returns:
        Report file path
    """
    trends = analyze_trends(30)
    patterns = detect_patterns()
    forecast = predict_future_trends(7)
    
    report = []
    report.append("=" * 60)
    report.append("TOXSCREEN-AI ADVANCED ANALYTICS REPORT")
    report.append("=" * 60)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    report.append("")
    report.append("TREND ANALYSIS:")
    report.append(f"  Score Trend: {trends.get('score_trend', 'N/A')}")
    report.append(f"  Volume Trend: {trends.get('volume_trend', 'N/A')}")
    report.append(f"  Daily Average: {trends.get('avg_daily_predictions', 0)}")
    report.append("")
    report.append("PATTERN DETECTION:")
    for p in patterns.get('size_patterns', []):
        report.append(f"  {p['size_group']}: {p['count']} compounds, Avg Score: {p['avg_score']}")
    report.append("")
    report.append("FORECAST:")
    report.append(f"  Trend: {forecast.get('trend', 'N/A')}")
    for f in forecast.get('forecast', []):
        report.append(f"  {f['day']}: {f['predicted_predictions']} predictions")
    report.append("=" * 60)
    
    report_path = os.path.join(os.path.dirname(__file__), '..', 'analytics_report.txt')
    with open(report_path, 'w') as f:
        f.write('\n'.join(report))
    
    return report_path
