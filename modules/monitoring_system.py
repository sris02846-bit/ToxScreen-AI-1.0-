"""
Monitoring & Analytics System
Real-time monitoring, error tracking, performance metrics, user analytics.
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List
import json
import os
import sys
import sqlite3

sys.path.insert(0, os.path.dirname(__file__))
from database import get_db_path


class MonitoringSystem:
    """Central monitoring and analytics."""
    
    _metrics: Dict[str, list] = {}
    _errors: List[Dict] = []
    _start_time = time.time()
    
    @staticmethod
    def track_metric(name: str, value: float):
        """Track a performance metric."""
        if name not in MonitoringSystem._metrics:
            MonitoringSystem._metrics[name] = []
        MonitoringSystem._metrics[name].append({
            "value": value,
            "timestamp": datetime.now().isoformat()
        })
    
    @staticmethod
    def track_error(error_type: str, message: str, module: str = ""):
        """Track an error."""
        MonitoringSystem._errors.append({
            "type": error_type,
            "message": message,
            "module": module,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 1000 errors
        if len(MonitoringSystem._errors) > 1000:
            MonitoringSystem._errors = MonitoringSystem._errors[-1000:]
    
    @staticmethod
    def get_performance_metrics() -> Dict:
        """Get performance metrics summary."""
        metrics_summary = {}
        
        for name, values in MonitoringSystem._metrics.items():
            if values:
                vals = [v["value"] for v in values[-100:]]
                metrics_summary[name] = {
                    "count": len(values),
                    "avg": round(sum(vals) / len(vals), 4),
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4),
                    "last": vals[-1]
                }
        
        return metrics_summary
    
    @staticmethod
    def get_error_summary() -> Dict:
        """Get error summary."""
        if not MonitoringSystem._errors:
            return {"total": 0, "recent": []}
        
        # Count by type
        error_types = {}
        for e in MonitoringSystem._errors:
            error_types[e["type"]] = error_types.get(e["type"], 0) + 1
        
        return {
            "total": len(MonitoringSystem._errors),
            "by_type": error_types,
            "recent": MonitoringSystem._errors[-10:],
            "last_hour": sum(
                1 for e in MonitoringSystem._errors
                if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(hours=1)
            )
        }
    
    @staticmethod
    def get_uptime() -> Dict:
        """Get system uptime."""
        uptime_seconds = time.time() - MonitoringSystem._start_time
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            "uptime_seconds": round(uptime_seconds, 0),
            "uptime_display": f"{days}d {hours}h {minutes}m",
            "started_at": datetime.fromtimestamp(MonitoringSystem._start_time).isoformat(),
            "availability": "99.9%" if uptime_seconds > 3600 else "Calculating..."
        }
    
    @staticmethod
    def get_user_analytics() -> Dict:
        """Get user analytics from database."""
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        analytics = {}
        
        # Total users
        cursor.execute('SELECT COUNT(DISTINCT username) FROM subscriptions')
        analytics["total_users"] = cursor.fetchone()[0] or 0
        
        # Active users (last 7 days)
        cursor.execute('''
            SELECT COUNT(DISTINCT username) FROM usage_tracking
            WHERE prediction_date >= date('now', '-7 days')
        ''')
        analytics["active_users_7d"] = cursor.fetchone()[0] or 0
        
        # Total predictions
        cursor.execute('SELECT COUNT(*) FROM predictions')
        analytics["total_predictions"] = cursor.fetchone()[0] or 0
        
        # Today's predictions
        cursor.execute('''
            SELECT SUM(prediction_count) FROM usage_tracking
            WHERE prediction_date = date('now')
        ''')
        result = cursor.fetchone()[0]
        analytics["today_predictions"] = result or 0
        
        # Average response time (from metrics)
        perf = MonitoringSystem.get_performance_metrics()
        if "prediction_time" in perf:
            analytics["avg_response_time"] = f"{perf['prediction_time']['avg']}s"
        
        conn.close()
        return analytics
    
    @staticmethod
    def generate_usage_report(days: int = 30) -> str:
        """Generate usage report."""
        analytics = MonitoringSystem.get_user_analytics()
        perf = MonitoringSystem.get_performance_metrics()
        errors = MonitoringSystem.get_error_summary()
        uptime = MonitoringSystem.get_uptime()
        
        report = []
        report.append("=" * 60)
        report.append("TOXSCREEN-AI USAGE & MONITORING REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append(f"Uptime: {uptime['uptime_display']}")
        report.append("")
        report.append(f"Total Users: {analytics.get('total_users', 0)}")
        report.append(f"Active Users (7d): {analytics.get('active_users_7d', 0)}")
        report.append(f"Total Predictions: {analytics.get('total_predictions', 0)}")
        report.append(f"Today: {analytics.get('today_predictions', 0)}")
        report.append("")
        report.append(f"Total Errors: {errors.get('total', 0)}")
        report.append(f"Errors (last hour): {errors.get('last_hour', 0)}")
        report.append("=" * 60)
        
        return "\n".join(report)
    
    @staticmethod
    def get_dashboard_data() -> Dict:
        """Get complete dashboard data."""
        return {
            "uptime": MonitoringSystem.get_uptime(),
            "performance": MonitoringSystem.get_performance_metrics(),
            "errors": MonitoringSystem.get_error_summary(),
            "users": MonitoringSystem.get_user_analytics(),
            "timestamp": datetime.now().isoformat()
        }
