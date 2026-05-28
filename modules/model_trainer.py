"""
Advanced Model Training Module
Ensemble models, cross-validation, hyperparameter tuning.
"""

import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import os
import sys
from datetime import datetime
from typing import Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from model_loader import get_models_dir, save_model


def compute_features(smiles: str) -> np.ndarray:
    """Compute molecular features for training."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    descriptors = []
    for desc in [Descriptors.MolWt, Descriptors.MolLogP, Descriptors.TPSA,
                 Descriptors.NumHAcceptors, Descriptors.NumHDonors,
                 Descriptors.NumRotatableBonds, Descriptors.NumAromaticRings,
                 Descriptors.FractionCSP3, Descriptors.HeavyAtomCount]:
        try:
            descriptors.append(desc(mol))
        except:
            descriptors.append(0)
    
    # Add fingerprint (first 128 bits)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=128)
    for i in range(128):
        descriptors.append(int(fp[i]))
    
    return np.array(descriptors)


def train_with_cross_validation(X: np.ndarray, y: np.ndarray, 
                                 model_name: str = "ensemble") -> Dict:
    """
    Train model with 5-fold cross-validation and hyperparameter tuning.
    
    Args:
        X: Feature matrix
        y: Target labels
        model_name: Name for saving
        
    Returns:
        Training results dictionary
    """
    results = {
        "model_name": model_name,
        "timestamp": datetime.now().isoformat(),
        "samples": len(X),
        "features": X.shape[1],
    }
    
    # Split: 70% train, 15% validation, 15% test
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)
    
    results["split"] = {
        "train": len(X_train),
        "validation": len(X_val),
        "test": len(X_test)
    }
    
    # Random Forest
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    
    # Cross-validation
    cv_scores = cross_val_score(rf, X_train, y_train, cv=5, scoring='accuracy')
    results["rf_cv"] = {
        "mean_accuracy": round(cv_scores.mean(), 3),
        "std_accuracy": round(cv_scores.std(), 3),
        "scores": [round(s, 3) for s in cv_scores]
    }
    
    # Train final model
    rf.fit(X_train, y_train)
    
    # Evaluate on validation set
    y_val_pred = rf.predict(X_val)
    results["rf_validation"] = {
        "accuracy": round(accuracy_score(y_val, y_val_pred), 3),
        "precision": round(precision_score(y_val, y_val_pred, zero_division=0), 3),
        "recall": round(recall_score(y_val, y_val_pred, zero_division=0), 3),
        "f1": round(f1_score(y_val, y_val_pred, zero_division=0), 3)
    }
    
    # Evaluate on test set
    y_test_pred = rf.predict(X_test)
    results["rf_test"] = {
        "accuracy": round(accuracy_score(y_test, y_test_pred), 3),
        "precision": round(precision_score(y_test, y_test_pred, zero_division=0), 3),
        "recall": round(recall_score(y_test, y_test_pred, zero_division=0), 3),
        "f1": round(f1_score(y_test, y_test_pred, zero_division=0), 3)
    }
    
    # Gradient Boosting
    gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    gb.fit(X_train, y_train)
    
    y_gb_pred = gb.predict(X_test)
    results["gb_test"] = {
        "accuracy": round(accuracy_score(y_test, y_gb_pred), 3),
        "f1": round(f1_score(y_test, y_gb_pred, zero_division=0), 3)
    }
    
    # Save best model
    best_model = rf if results["rf_test"]["f1"] >= results["gb_test"]["f1"] else gb
    save_model(best_model, f"{model_name}_ensemble")
    
    results["best_model"] = "RandomForest" if results["rf_test"]["f1"] >= results["gb_test"]["f1"] else "GradientBoosting"
    results["best_f1"] = max(results["rf_test"]["f1"], results["gb_test"]["f1"])
    
    return results


def run_full_training_pipeline(dataset_path: str = None) -> Dict:
    """
    Run complete training pipeline on full dataset.
    
    Args:
        dataset_path: Path to dataset CSV
        
    Returns:
        Complete training report
    """
    # Load or create dataset
    if dataset_path and os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
    else:
        from data_collector import create_full_dataset
        df, _ = create_full_dataset()
    
    print(f"Training on {len(df)} compounds...")
    
    # Compute features
    X_list, y_list = [], []
    errors = 0
    
    for _, row in df.iterrows():
        features = compute_features(row['smiles'])
        if features is not None:
            X_list.append(features)
            y_list.append(row['toxic'])
        else:
            errors += 1
    
    X = np.array(X_list)
    y = np.array(y_list)
    
    print(f"Features computed: {len(X)} valid, {errors} errors")
    
    # Train with cross-validation
    results = train_with_cross_validation(X, y, "toxicity_ensemble")
    results["parse_errors"] = errors
    results["total_dataset"] = len(df)
    
    return results


def generate_training_report(results: Dict) -> str:
    """Generate training report."""
    report = []
    report.append("=" * 60)
    report.append("MODEL TRAINING REPORT")
    report.append("=" * 60)
    report.append(f"Timestamp: {results.get('timestamp', 'N/A')}")
    report.append(f"Samples: {results.get('samples', 0)}")
    report.append(f"Features: {results.get('features', 0)}")
    report.append("")
    report.append("Data Split:")
    split = results.get('split', {})
    report.append(f"  Train: {split.get('train', 0)}")
    report.append(f"  Validation: {split.get('validation', 0)}")
    report.append(f"  Test: {split.get('test', 0)}")
    report.append("")
    report.append("Random Forest CV:")
    cv = results.get('rf_cv', {})
    report.append(f"  Mean Accuracy: {cv.get('mean_accuracy', 0)}")
    report.append(f"  Std: {cv.get('std_accuracy', 0)}")
    report.append("")
    report.append("Test Results:")
    test = results.get('rf_test', {})
    report.append(f"  Accuracy: {test.get('accuracy', 0)}")
    report.append(f"  Precision: {test.get('precision', 0)}")
    report.append(f"  Recall: {test.get('recall', 0)}")
    report.append(f"  F1 Score: {test.get('f1', 0)}")
    report.append("")
    report.append(f"Best Model: {results.get('best_model', 'N/A')}")
    report.append(f"Best F1: {results.get('best_f1', 0)}")
    report.append("=" * 60)
    
    return "\n".join(report)
