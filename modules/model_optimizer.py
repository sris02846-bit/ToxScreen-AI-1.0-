"""
Model Optimization Module
Feature engineering, ensemble methods, model stacking.
"""

import numpy as np
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import (
    RandomForestClassifier, GradientBoostingClassifier,
    ExtraTreesClassifier, VotingClassifier, StackingClassifier
)
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import f1_score
import joblib
import os
import sys
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from model_loader import get_models_dir, save_model


def engineer_features(smiles: str) -> np.ndarray:
    """
    Advanced feature engineering for better predictions.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Feature array
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    features = []
    
    # Basic descriptors
    basic_descriptors = [
        Descriptors.MolWt, Descriptors.MolLogP, Descriptors.TPSA,
        Descriptors.NumHAcceptors, Descriptors.NumHDonors,
        Descriptors.NumRotatableBonds, Descriptors.NumAromaticRings,
        Descriptors.FractionCSP3, Descriptors.HeavyAtomCount,
        Descriptors.RingCount, Descriptors.NumHeteroatoms,
        Descriptors.BertzCT, Descriptors.NumValenceElectrons,
        Descriptors.MaxPartialCharge, Descriptors.MinPartialCharge,
        Descriptors.NumAliphaticRings, Descriptors.NumSaturatedRings,
        Descriptors.NHOHCount, Descriptors.NOCount,
    ]
    
    for desc in basic_descriptors:
        try:
            features.append(desc(mol))
        except:
            features.append(0)
    
    # Morgan fingerprint (reduced to 64 bits for speed)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        features.append(int(fp[i]))
    
    # MACCS keys (166 bits)
    try:
        maccs = AllChem.GetMACCSKeysFingerprint(mol)
        for i in range(166):
            features.append(int(maccs[i]))
    except:
        features.extend([0] * 166)
    
    return np.array(features)


def create_stacked_ensemble() -> StackingClassifier:
    """
    Create stacked ensemble model.
    
    Returns:
        StackingClassifier
    """
    # Base estimators
    base_estimators = [
        ('rf', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)),
        ('et', ExtraTreesClassifier(n_estimators=100, max_depth=10, random_state=42)),
    ]
    
    # Meta classifier
    meta_classifier = LogisticRegression(max_iter=1000, random_state=42)
    
    # Stacking ensemble
    ensemble = StackingClassifier(
        estimators=base_estimators,
        final_estimator=meta_classifier,
        cv=5
    )
    
    return ensemble


def create_voting_ensemble() -> VotingClassifier:
    """
    Create voting ensemble model.
    
    Returns:
        VotingClassifier
    """
    estimators = [
        ('rf', RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)),
        ('gb', GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)),
        ('et', ExtraTreesClassifier(n_estimators=100, max_depth=10, random_state=42)),
        ('svm', SVC(kernel='rbf', probability=True, random_state=42)),
    ]
    
    ensemble = VotingClassifier(
        estimators=estimators,
        voting='soft'
    )
    
    return ensemble


def hyperparameter_tuning(X: np.ndarray, y: np.ndarray) -> Dict:
    """
    Perform hyperparameter tuning with GridSearchCV.
    
    Args:
        X: Feature matrix
        y: Labels
        
    Returns:
        Best parameters and scores
    """
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4],
    }
    
    rf = RandomForestClassifier(random_state=42, n_jobs=-1)
    
    grid = GridSearchCV(
        rf, param_grid,
        cv=5, scoring='f1',
        n_jobs=-1, verbose=0
    )
    
    grid.fit(X, y)
    
    return {
        "best_params": grid.best_params_,
        "best_score": round(grid.best_score_, 4),
        "cv_results_mean": round(grid.cv_results_['mean_test_score'].mean(), 4)
    }


def train_optimized_models(dataset_path: str = None) -> Dict:
    """
    Train optimized models with feature engineering.
    
    Args:
        dataset_path: Path to dataset
        
    Returns:
        Training results
    """
    # Load data
    if dataset_path and os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
    else:
        from data_collector import create_full_dataset
        df, _ = create_full_dataset()
    
    # Take a subset for speed
    df = df.head(2000)
    
    # Engineer features
    X_list, y_list = [], []
    errors = 0
    
    for _, row in df.iterrows():
        features = engineer_features(row['smiles'])
        if features is not None:
            X_list.append(features)
            y_list.append(row['toxic'])
        else:
            errors += 1
    
    X = np.array(X_list)
    y = np.array(y_list)
    
    results = {
        "samples": len(X),
        "features": X.shape[1],
        "errors": errors,
        "models": {}
    }
    
    # 1. Random Forest (baseline)
    rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    rf_scores = cross_val_score(rf, X, y, cv=5, scoring='f1')
    results["models"]["RandomForest"] = {
        "cv_f1_mean": round(rf_scores.mean(), 4),
        "cv_f1_std": round(rf_scores.std(), 4)
    }
    
    # 2. Gradient Boosting
    gb = GradientBoostingClassifier(n_estimators=100, max_depth=5, random_state=42)
    gb_scores = cross_val_score(gb, X, y, cv=5, scoring='f1')
    results["models"]["GradientBoosting"] = {
        "cv_f1_mean": round(gb_scores.mean(), 4),
        "cv_f1_std": round(gb_scores.std(), 4)
    }
    
    # 3. Extra Trees
    et = ExtraTreesClassifier(n_estimators=100, max_depth=10, random_state=42)
    et_scores = cross_val_score(et, X, y, cv=5, scoring='f1')
    results["models"]["ExtraTrees"] = {
        "cv_f1_mean": round(et_scores.mean(), 4),
        "cv_f1_std": round(et_scores.std(), 4)
    }
    
    # 4. Voting Ensemble
    voting = create_voting_ensemble()
    voting_scores = cross_val_score(voting, X, y, cv=5, scoring='f1')
    results["models"]["VotingEnsemble"] = {
        "cv_f1_mean": round(voting_scores.mean(), 4),
        "cv_f1_std": round(voting_scores.std(), 4)
    }
    
    # 5. Stacking Ensemble
    stacking = create_stacked_ensemble()
    stacking_scores = cross_val_score(stacking, X, y, cv=5, scoring='f1')
    results["models"]["StackingEnsemble"] = {
        "cv_f1_mean": round(stacking_scores.mean(), 4),
        "cv_f1_std": round(stacking_scores.std(), 4)
    }
    
    # Find best model
    best_model = max(results["models"].items(), key=lambda x: x[1]["cv_f1_mean"])
    results["best_model"] = best_model[0]
    results["best_f1"] = best_model[1]["cv_f1_mean"]
    
    # Save best model
    if best_model[0] == "StackingEnsemble":
        stacking.fit(X, y)
        save_model(stacking, "optimized_stacking")
    elif best_model[0] == "VotingEnsemble":
        voting.fit(X, y)
        save_model(voting, "optimized_voting")
    
    return results
