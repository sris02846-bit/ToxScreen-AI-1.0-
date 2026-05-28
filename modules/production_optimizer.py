"""
Production Performance Optimizer
Caching, profiling, and optimization for <2s response time.
"""

import time
import functools
from typing import Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# Performance metrics
_PERFORMANCE_STATS: Dict[str, list] = {}


def timer(func):
    """Decorator to measure function execution time."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        
        name = func.__name__
        if name not in _PERFORMANCE_STATS:
            _PERFORMANCE_STATS[name] = []
        _PERFORMANCE_STATS[name].append(elapsed)
        
        return result
    return wrapper


def get_performance_report() -> Dict:
    """Get performance statistics."""
    report = {}
    for name, times in _PERFORMANCE_STATS.items():
        if times:
            report[name] = {
                "calls": len(times),
                "avg_time": round(sum(times) / len(times), 4),
                "min_time": round(min(times), 4),
                "max_time": round(max(times), 4),
                "total_time": round(sum(times), 2)
            }
    return report


# Caching layer for frequent predictions
_PREDICTION_CACHE: Dict[str, Any] = {}
_CACHE_MAX_SIZE = 10000


def cache_result(key: str, result: Any):
    """Cache a prediction result."""
    if len(_PREDICTION_CACHE) >= _CACHE_MAX_SIZE:
        # Remove oldest entry
        oldest = next(iter(_PREDICTION_CACHE))
        del _PREDICTION_CACHE[oldest]
    _PREDICTION_CACHE[key] = result


def get_cached_result(key: str) -> Any:
    """Get cached prediction result."""
    return _PREDICTION_CACHE.get(key)


def clear_cache():
    """Clear prediction cache."""
    _PREDICTION_CACHE.clear()
    return {"cleared": True}


def get_cache_stats() -> Dict:
    """Get cache statistics."""
    return {
        "cache_size": len(_PREDICTION_CACHE),
        "max_size": _CACHE_MAX_SIZE,
        "utilization": f"{len(_PREDICTION_CACHE)/_CACHE_MAX_SIZE:.1%}"
    }


# Health check
def system_health_check() -> Dict:
    """Comprehensive system health check."""
    import psutil
    
    return {
        "status": "healthy",
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "memory_used_gb": round(psutil.virtual_memory().used / 1024**3, 2),
        "memory_total_gb": round(psutil.virtual_memory().total / 1024**3, 2),
        "disk_percent": psutil.disk_usage('/').percent,
        "cache_entries": len(_PREDICTION_CACHE),
        "uptime_seconds": time.time() - psutil.boot_time()
    }


# Response time checker
def check_response_time(func, *args) -> Dict:
    """Check if function meets response time target."""
    start = time.time()
    result = func(*args)
    elapsed = time.time() - start
    
    return {
        "result": result,
        "response_time": round(elapsed, 3),
        "meets_target": elapsed < 2.0,
        "target": "< 2 seconds"
    }
