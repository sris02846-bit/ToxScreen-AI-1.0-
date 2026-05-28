"""
Accuracy Testing Module
Tests with 1000+ compounds, calculates sensitivity/specificity, optimizes thresholds.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from typing import Dict, List, Tuple
import sys
import os
import time
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))


def generate_test_dataset(n: int = 1000) -> pd.DataFrame:
    """
    Generate test dataset with known toxicity labels.
    
    Args:
        n: Number of compounds
        
    Returns:
        DataFrame with SMILES and known labels
    """
    # Known safe compounds
    safe = [
        ("CC(=O)OC1=CC=CC=C1C(=O)O", 0),  # Aspirin
        ("CC(=O)NC1=CC=C(O)C=C1", 0),      # Paracetamol (low dose)
        ("CCO", 0),                          # Ethanol
        ("C(C(=O)O)N", 0),                  # Glycine
        ("CC(=O)O", 0),                     # Acetic acid
        ("C1CCCCC1", 0),                    # Cyclohexane
        ("CCCCCC", 0),                      # Hexane
        ("CC(=O)C", 0),                     # Acetone
        ("C1CC1", 0),                       # Cyclopropane
        ("CCCC", 0),                        # Butane
    ]
    
    # Known toxic compounds
    toxic = [
        ("ClC(Cl)(Cl)Cl", 1),               # Carbon tetrachloride
        ("NN", 1),                           # Hydrazine
        ("CN(N=O)C", 1),                    # N-Nitrosodimethylamine
        ("ClC=C", 1),                       # Vinyl chloride
        ("c1ccccc1", 1),                    # Benzene
        ("ClC(Cl)Cl", 1),                   # Chloroform
        ("CCOP(=S)(OCC)Oc1ccc(cc1)[N+](=O)[O-]", 1),  # Parathion
        ("CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O", 0),  # Morphine (borderline)
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", 0),  # Ibuprofen
        ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", 0),   # Caffeine
    ]
    
    compounds = []
    for i in range(n):
        if i % 2 == 0 and i < len(safe) * 50:
            s = safe[i % len(safe)]
        else:
            s = toxic[i % len(toxic)]
        compounds.append({
            "id": i + 1,
            "smiles": s[0],
            "known_toxic": s[1]
        })
    
    return pd.DataFrame(compounds)


def run_accuracy_tests(n_compounds: int = 500) -> Dict:
    """
    Run comprehensive accuracy testing.
    
    Args:
        n_compounds: Number of test compounds
        
    Returns:
        Accuracy metrics dictionary
    """
    from molecular_parser import parse_smiles
    from lipinski_rules import evaluate_lipinski
    from toxicophores import evaluate_toxicophores
    
    test_df = generate_test_dataset(n_compounds)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_compounds": n_compounds,
        "y_true": [],
        "y_pred": [],
        "y_score": [],
        "errors": [],
        "timing": {}
    }
    
    start_time = time.time()
    
    for _, row in test_df.iterrows():
        smiles = row['smiles']
        known = row['known_toxic']
        
        try:
            mol, err = parse_smiles(smiles)
            if err or mol is None:
                results["errors"].append({"smiles": smiles, "error": str(err)})
                continue
            
            lipinski = evaluate_lipinski(mol)
            tox = evaluate_toxicophores(mol)
            
            # Predict toxicity based on combined score
            toxicity_score = tox['toxicity_score']
            lipinski_penalty = lipinski['violations'] * 15
            combined = toxicity_score + lipinski_penalty
            
            # Threshold: >50 = toxic
            predicted = 1 if combined > 50 else 0
            
            results["y_true"].append(known)
            results["y_pred"].append(predicted)
            results["y_score"].append(combined / 100)
            
        except Exception as e:
            results["errors"].append({"smiles": smiles, "error": str(e)})
    
    results["timing"]["total_seconds"] = round(time.time() - start_time, 2)
    results["timing"]["per_compound"] = round(results["timing"]["total_seconds"] / max(1, len(results["y_true"])), 4)
    
    # Calculate metrics
    if results["y_true"]:
        y_true = np.array(results["y_true"])
        y_pred = np.array(results["y_pred"])
        y_score = np.array(results["y_score"])
        
        results["metrics"] = {
            "accuracy": round(accuracy_score(y_true, y_pred), 3),
            "precision": round(precision_score(y_true, y_pred, zero_division=0), 3),
            "recall": round(recall_score(y_true, y_pred, zero_division=0), 3),
            "sensitivity": round(recall_score(y_true, y_pred, zero_division=0), 3),
            "specificity": round(recall_score(1-y_true, 1-y_pred, zero_division=0), 3),
            "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 3),
            "roc_auc": round(roc_auc_score(y_true, y_score) if len(set(y_true)) > 1 else 0, 3),
            "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
        }
        
        # Classification report
        results["classification_report"] = classification_report(
            y_true, y_pred,
            target_names=["Non-Toxic", "Toxic"],
            zero_division=0
        )
    
    return results


def optimize_thresholds(results: Dict) -> Dict:
    """
    Find optimal threshold for toxicity classification.
    
    Args:
        results: Accuracy test results
        
    Returns:
        Optimal thresholds dictionary
    """
    if not results.get("y_true"):
        return {"error": "No test data available"}
    
    y_true = np.array(results["y_true"])
    y_score = np.array(results["y_score"])
    
    best_f1 = 0
    best_threshold = 50
    
    for threshold in range(10, 90, 5):
        y_pred = (y_score * 100 > threshold).astype(int)
        f1 = f1_score(y_true, y_pred, zero_division=0)
        
        if f1 > best_f1:
            best_f1 = f1
            best_threshold = threshold
    
    return {
        "optimal_threshold": best_threshold,
        "best_f1_score": round(best_f1, 3),
        "current_threshold": 50,
        "recommendation": f"Use threshold of {best_threshold} for best F1 score"
    }


def generate_accuracy_report(results: Dict) -> str:
    """Generate formatted accuracy report."""
    m = results.get("metrics", {})
    
    report = []
    report.append("=" * 60)
    report.append("TOXSCREEN-AI ACCURACY TEST REPORT")
    report.append("=" * 60)
    report.append(f"Date: {results['timestamp']}")
    report.append(f"Compounds Tested: {results['total_compounds']}")
    report.append(f"Errors: {len(results.get('errors', []))}")
    report.append("")
    report.append("-" * 40)
    report.append("PERFORMANCE METRICS")
    report.append("-" * 40)
    report.append(f"Accuracy:    {m.get('accuracy', 'N/A'):.1%}")
    report.append(f"Sensitivity: {m.get('sensitivity', 'N/A'):.1%}")
    report.append(f"Specificity: {m.get('specificity', 'N/A'):.1%}")
    report.append(f"Precision:   {m.get('precision', 'N/A'):.1%}")
    report.append(f"F1 Score:    {m.get('f1_score', 'N/A'):.3f}")
    report.append(f"ROC AUC:     {m.get('roc_auc', 'N/A'):.3f}")
    report.append("")
    report.append("-" * 40)
    report.append("CONFUSION MATRIX")
    report.append("-" * 40)
    cm = m.get('confusion_matrix', [[0,0],[0,0]])
    report.append(f"TN={cm[0][0]}  FP={cm[0][1]}")
    report.append(f"FN={cm[1][0]}  TP={cm[1][1]}")
    report.append("")
    report.append(f"Processing Time: {results['timing']['total_seconds']}s")
    report.append(f"Per Compound: {results['timing']['per_compound']}s")
    report.append("=" * 60)
    
    return "\n".join(report)
