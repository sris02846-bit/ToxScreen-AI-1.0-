"""
Tox21 Validation Module
Runs held-out validation and generates reports.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
import joblib
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from ml_model import compute_molecular_descriptors, load_model


def create_validation_dataset() -> tuple:
    """
    Create held-out validation set from known compounds.
    Returns X_val, y_val, smiles_list
    """
    # Known hepatotoxic compounds (held-out, not in training)
    hepatotoxic_val = [
        ("CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2", "Flutamide"),
        ("CCN(CC)C(=S)SSC(=S)N(CC)CC", "Disulfiram"),
        ("CC1=C(C(=O)C=CC1=O)C", "Vitamin K3"),
        ("CCCCCOC1=CC=C(C=C1)C(=O)O", "Valproic acid"),
        ("CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O", "Diazepam"),
        ("ClC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2Cl", "Diclofenac"),
    ]
    
    # Known non-hepatotoxic (held-out)
    non_hepatotoxic_val = [
        ("C1CCCCC1", "Cyclohexane"),
        ("CCCCCCCC", "Octane"),
        ("C1CC1", "Cyclopropane"),
        ("CCCC", "Butane"),
        ("CCCCCC", "Hexane"),
        ("CC(=O)C", "Acetone"),
        ("C1=CC=C2C=CC=CC2=C1", "Naphthalene"),
    ]
    
    X_data = []
    y_data = []
    smiles_list = []
    names = []
    
    for smiles, name in hepatotoxic_val:
        desc = compute_molecular_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)
            smiles_list.append(smiles)
            names.append(name)
    
    for smiles, name in non_hepatotoxic_val:
        desc = compute_molecular_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)
            smiles_list.append(smiles)
            names.append(name)
    
    return np.array(X_data), np.array(y_data), smiles_list, names


def run_validation() -> dict:
    """
    Run validation on held-out dataset.
    
    Returns:
        Dictionary with validation metrics
    """
    # Load model
    model = load_model()
    
    # Get validation data
    X_val, y_val, smiles_list, names = create_validation_dataset()
    
    # Predict
    y_pred = model.predict(X_val)
    y_proba = model.predict_proba(X_val)[:, 1]
    
    # Calculate metrics
    accuracy = accuracy_score(y_val, y_pred)
    precision = precision_score(y_val, y_pred, zero_division=0)
    recall = recall_score(y_val, y_pred, zero_division=0)
    f1 = f1_score(y_val, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_val, y_proba)
    cm = confusion_matrix(y_val, y_pred)
    
    results = {
        "validation_date": datetime.now().isoformat(),
        "model_type": "RandomForest",
        "task": "Hepatotoxicity Prediction",
        "validation_samples": len(X_val),
        "metrics": {
            "accuracy": round(accuracy, 3),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "roc_auc": round(roc_auc, 3),
            "confusion_matrix": cm.tolist(),
            "true_negatives": int(cm[0][0]),
            "false_positives": int(cm[0][1]),
            "false_negatives": int(cm[1][0]),
            "true_positives": int(cm[1][1])
        },
        "predictions": []
    }
    
    for i, (smiles, name) in enumerate(zip(smiles_list, names)):
        results["predictions"].append({
            "name": name,
            "smiles": smiles,
            "actual": "Hepatotoxic" if y_val[i] == 1 else "Non-Hepatotoxic",
            "predicted": "Hepatotoxic" if y_pred[i] == 1 else "Non-Hepatotoxic",
            "probability": round(y_proba[i], 3),
            "correct": bool(y_val[i] == y_pred[i])
        })
    
    return results


def save_validation_results(results: dict):
    """Save validation results to CSV and report files."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    # Save CSV
    csv_data = []
    for pred in results["predictions"]:
        csv_data.append({
            "Name": pred["name"],
            "SMILES": pred["smiles"],
            "Actual": pred["actual"],
            "Predicted": pred["predicted"],
            "Probability": pred["probability"],
            "Correct": pred["correct"]
        })
    
    df = pd.DataFrame(csv_data)
    csv_path = os.path.join(base_dir, "validation_results.csv")
    df.to_csv(csv_path, index=False)
    
    # Save report
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append("ToxScreen-AI Validation Report")
    report_lines.append("=" * 60)
    report_lines.append(f"Date: {results['validation_date']}")
    report_lines.append(f"Model: {results['model_type']}")
    report_lines.append(f"Task: {results['task']}")
    report_lines.append(f"Validation Samples: {results['validation_samples']}")
    report_lines.append("")
    report_lines.append("-" * 60)
    report_lines.append("METRICS")
    report_lines.append("-" * 60)
    
    m = results["metrics"]
    report_lines.append(f"Accuracy:  {m['accuracy']:.3f}")
    report_lines.append(f"Precision: {m['precision']:.3f}")
    report_lines.append(f"Recall:    {m['recall']:.3f}")
    report_lines.append(f"F1 Score:  {m['f1_score']:.3f}")
    report_lines.append(f"ROC AUC:   {m['roc_auc']:.3f}")
    report_lines.append("")
    report_lines.append("Confusion Matrix:")
    report_lines.append(f"  TN={m['true_negatives']}  FP={m['false_positives']}")
    report_lines.append(f"  FN={m['false_negatives']}  TP={m['true_positives']}")
    report_lines.append("")
    report_lines.append("-" * 60)
    report_lines.append("PREDICTIONS")
    report_lines.append("-" * 60)
    
    for pred in results["predictions"]:
        status = "CORRECT" if pred["correct"] else "WRONG"
        report_lines.append(f"[{status}] {pred['name']}: {pred['actual']} -> {pred['predicted']} ({pred['probability']:.3f})")
    
    report_lines.append("")
    report_lines.append("=" * 60)
    
    report_path = os.path.join(base_dir, "validation_report.txt")
    with open(report_path, 'w') as f:
        f.write("\n".join(report_lines))
    
    return csv_path, report_path


def generate_validation_summary() -> str:
    """Generate a quick validation summary for display."""
    results = run_validation()
    save_validation_results(results)
    
    m = results["metrics"]
    correct = sum(1 for p in results["predictions"] if p["correct"])
    total = len(results["predictions"])
    
    summary = f"""
Validation Summary:
- Samples: {total}
- Correct: {correct}/{total}
- Accuracy: {m['accuracy']:.1%}
- ROC AUC: {m['roc_auc']:.3f}
- F1 Score: {m['f1_score']:.3f}
    """
    return summary
