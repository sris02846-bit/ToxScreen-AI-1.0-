"""
Performance Testing Module
Stress tests with 10,000 compounds, measures memory/speed, optimizes.
"""

import psutil
import os
import sys
import time
import tracemalloc
from typing import Dict, List
from datetime import datetime
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))


def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


def stress_test_pipeline(n_compounds: int = 10000) -> Dict:
    """
    Stress test the full pipeline.
    
    Args:
        n_compounds: Number of compounds to test
        
    Returns:
        Performance metrics dictionary
    """
    from molecular_parser import parse_smiles
    from accuracy_tester import generate_test_dataset
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_compounds": n_compounds,
        "memory": {},
        "timing": {},
        "throughput": {},
        "bottlenecks": []
    }
    
    # Generate test data
    start_mem = get_memory_usage()
    test_df = generate_test_dataset(min(n_compounds, 1000))
    test_df = pd.concat([test_df] * (n_compounds // len(test_df) + 1)).head(n_compounds)
    results["memory"]["dataset_mb"] = round(get_memory_usage() - start_mem, 2)
    
    # Test parsing speed
    tracemalloc.start()
    start_time = time.time()
    parse_count = 0
    
    for _, row in test_df.iterrows():
        try:
            mol, _ = parse_smiles(row['smiles'])
            if mol:
                parse_count += 1
        except:
            pass
    
    parse_time = time.time() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    results["timing"]["parsing_total"] = round(parse_time, 2)
    results["timing"]["parsing_per_compound"] = round(parse_time / n_compounds * 1000, 2)
    results["memory"]["parsing_peak_mb"] = round(peak / 1024 / 1024, 2)
    results["throughput"]["compounds_per_second"] = round(n_compounds / parse_time, 1)
    
    # Identify bottlenecks
    if parse_time / n_compounds > 0.01:
        results["bottlenecks"].append("SMILES parsing is slow - consider caching")
    if results["memory"]["parsing_peak_mb"] > 500:
        results["bottlenecks"].append("High memory usage - optimize batch size")
    
    # Recommendations
    results["recommendations"] = []
    if results["throughput"]["compounds_per_second"] < 50:
        results["recommendations"].append("Use parallel processing for large batches")
    if results["memory"]["parsing_peak_mb"] > 200:
        results["recommendations"].append("Process in chunks of 1000 compounds")
    
    return results


def run_benchmark_suite() -> Dict:
    """
    Run complete benchmark suite.
    
    Returns:
        Benchmark results
    """
    print("Running performance benchmarks...")
    
    benchmarks = {}
    
    # Test 100 compounds
    print("  Testing 100 compounds...")
    benchmarks["100"] = stress_test_pipeline(100)
    
    # Test 1000 compounds
    print("  Testing 1,000 compounds...")
    benchmarks["1000"] = stress_test_pipeline(1000)
    
    # Quick estimate for 10000
    print("  Testing 10,000 compounds...")
    benchmarks["10000"] = stress_test_pipeline(10000)
    
    return benchmarks


def generate_performance_report(benchmarks: Dict) -> str:
    """Generate performance report."""
    report = []
    report.append("=" * 60)
    report.append("TOXSCREEN-AI PERFORMANCE TEST REPORT")
    report.append("=" * 60)
    
    for size, data in benchmarks.items():
        report.append(f"\n{size} Compounds:")
        report.append(f"  Time: {data['timing']['parsing_total']}s")
        report.append(f"  Speed: {data['throughput']['compounds_per_second']} compounds/sec")
        report.append(f"  Memory: {data['memory']['parsing_peak_mb']} MB")
    
    report.append("\n" + "=" * 60)
    return "\n".join(report)
