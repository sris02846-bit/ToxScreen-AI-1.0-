"""
Advanced Accuracy Testing Module
Comprehensive metrics: Sensitivity, Specificity, Precision, Recall, F1, AUC-ROC.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, roc_curve, confusion_matrix, classification_report,
    matthews_corrcoef, balanced_accuracy_score
)
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from typing import Dict, Tuple
import sys
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from model_loader import load_model


def run_comprehensive_testing(smiles_list: list = None, y_true: list = None) -> Dict:
    """
    Run comprehensive accuracy testing with all metrics.
    
    Returns:
        Complete metrics dictionary
    """
    if smiles_list is None:
        # Use test compounds
        smiles_list = [
            "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin - safe
            "CC(=O)NC1=CC=C(O)C=C1",      # Paracetamol - safe (low dose)
            "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen - safe
            "CCO",                          # Ethanol - safe
            "C(C(=O)O)N",                  # Glycine - safe
            "CC(=O)O",                     # Acetic acid - safe
            "ClC(Cl)(Cl)Cl",              # CCl4 - toxic
            "NN",                          # Hydrazine - toxic
            "CN(N=O)C",                   # NDMA - toxic
            "ClC=C",                      # Vinyl chloride - toxic
            "c1ccccc1",                   # Benzene - toxic
            "ClC(Cl)Cl",                  # Chloroform - toxic
            "CCCCCC",                      # Hexane - safe
            "C1CCCCC1",                   # Cyclohexane - safe
            "CC(=O)C",                    # Acetone - safe
            "CCOP(=S)(OCC)Oc1ccc(cc1)[N+](=O)[O-]",  # Parathion - toxic
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine - safe
            "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",  # Morphine - borderline
        ]
        y_true = [0,0,0,0,0,0, 1,1,1,1,1,1, 0,0,0, 1,0,0]
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_samples": len(smiles_list),
        "metrics": {},
        "predictions": []
    }
    
    y_pred = []
    y_scores = []
    
    for smiles in smiles_list:
        try:
            from molecular_parser import parse_smiles
            from toxicophores import evaluate_toxicophores
            from lipinski_rules import evaluate_lipinski
            
            mol, _ = parse_smiles(smiles)
            if mol:
                tox = evaluate_toxicophores(mol)
                lip = evaluate_lipinski(mol)
                
                # Combined score
                score = tox['toxicity_score'] + lip['violations'] * 15
                pred = 1 if score > 40 else 0
                
                y_pred.append(pred)
                y_scores.append(score / 100)
            else:
                y_pred.append(0)
                y_scores.append(0)
        except:
            y_pred.append(0)
            y_scores.append(0)
    
    y_true = np.array(y_true[:len(y_pred)])
    y_pred = np.array(y_pred)
    y_scores = np.array(y_scores)
    
    # Calculate ALL metrics
    metrics = {
        "accuracy": round(accuracy_score(y_true, y_pred), 4),
        "balanced_accuracy": round(balanced_accuracy_score(y_true, y_pred), 4),
        "sensitivity": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "specificity": round(recall_score(1-y_true, 1-y_pred, zero_division=0), 4),
        "precision": round(precision_score(y_true, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_true, y_pred, zero_division=0), 4),
        "f1_score": round(f1_score(y_true, y_pred, zero_division=0), 4),
        "mcc": round(matthews_corrcoef(y_true, y_pred), 4),
    }
    
    # AUC-ROC (only if both classes present)
    if len(set(y_true)) > 1:
        try:
            metrics["auc_roc"] = round(roc_auc_score(y_true, y_scores), 4)
        except:
            metrics["auc_roc"] = 0
    
    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred)
    metrics["confusion_matrix"] = {
        "true_negatives": int(cm[0][0]) if cm.shape[0] > 0 else 0,
        "false_positives": int(cm[0][1]) if cm.shape[1] > 1 else 0,
        "false_negatives": int(cm[1][0]) if cm.shape[0] > 1 else 0,
        "true_positives": int(cm[1][1]) if cm.shape[0] > 1 and cm.shape[1] > 1 else 0,
    }
    
    results["metrics"] = metrics
    
    # Target comparison
    targets = {
        "sensitivity": {"target": 0.95, "achieved": metrics["sensitivity"], "pass": metrics["sensitivity"] >= 0.95},
        "specificity": {"target": 0.85, "achieved": metrics["specificity"], "pass": metrics["specificity"] >= 0.85},
        "precision": {"target": 0.90, "achieved": metrics["precision"], "pass": metrics["precision"] >= 0.90},
        "recall": {"target": 0.95, "achieved": metrics["recall"], "pass": metrics["recall"] >= 0.95},
        "f1_score": {"target": 0.93, "achieved": metrics["f1_score"], "pass": metrics["f1_score"] >= 0.93},
        "auc_roc": {"target": 0.95, "achieved": metrics.get("auc_roc", 0), "pass": metrics.get("auc_roc", 0) >= 0.95},
    }
    
    results["target_comparison"] = targets
    
    # Overall pass/fail
    passed = sum(1 for t in targets.values() if t["pass"])
    results["targets_passed"] = f"{passed}/{len(targets)}"
    results["overall_pass"] = passed >= 4
    
    return results


def generate_accuracy_report(results: Dict) -> str:
    """Generate formatted accuracy report."""
    m = results["metrics"]
    t = results["target_comparison"]
    
    report = []
    report.append("=" * 65)
    report.append("TOXSCREEN-AI COMPREHENSIVE ACCURACY REPORT")
    report.append("=" * 65)
    report.append(f"Date: {results['timestamp']}")
    report.append(f"Samples: {results['total_samples']}")
    report.append("")
    
    report.append("-" * 45)
    report.append("PERFORMANCE METRICS")
    report.append("-" * 45)
    for name, value in m.items():
        if not isinstance(value, dict):
            report.append(f"  {name}: {value}")
    report.append("")
    
    report.append("-" * 45)
    report.append("TARGET COMPARISON")
    report.append("-" * 45)
    for name, data in t.items():
        if isinstance(data, dict):
            status = "PASS" if data["pass"] else "FAIL"
            report.append(f"  [{status}] {name}: {data['achieved']:.3f} (target: {data['target']})")
    report.append("")
    
    report.append(f"Targets Passed: {results['targets_passed']}")
    report.append(f"Overall: {'PASS' if results['overall_pass'] else 'NEEDS IMPROVEMENT'}")
    report.append("=" * 65)
    
    return "\n".join(report)
