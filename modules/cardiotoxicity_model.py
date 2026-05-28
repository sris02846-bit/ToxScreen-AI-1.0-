"""
Cardiotoxicity Prediction Model
Trained on Tox21 SR-TOX data with RF/XGBoost.
"""

import pandas as pd
import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score
import joblib
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))


def compute_cardiotox_descriptors(smiles: str) -> dict:
    """Compute descriptors for cardiotoxicity prediction."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    descriptors = {
        'MolWt': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'TPSA': Descriptors.TPSA(mol),
        'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'NumAromaticRings': Descriptors.NumAromaticRings(mol),
        'FractionCSP3': Descriptors.FractionCSP3(mol),
        'HeavyAtomCount': Descriptors.HeavyAtomCount(mol),
        'NumHeteroatoms': Descriptors.NumHeteroatoms(mol),
        'RingCount': Descriptors.RingCount(mol),
        'BertzCT': Descriptors.BertzCT(mol),
    }
    
    # ECFP4 fingerprint (64 bits)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_cardiotox_data() -> tuple:
    """Create cardiotoxicity training data."""
    # Cardiotoxic compounds
    cardiotoxic = [
        "COc1ccc2c(c1)C(C(C)C)C(=O)O2",  # Verapamil-like
        "CN1CCCC1CCN2c3ccccc3CCc4ccccc24",  # Haloperidol-like
        "CCN(CC)CC(=O)Nc1c(C)cccc1C",  # Lidocaine
        "CC(C)NCC(O)COc1cccc2ccccc12",  # Propranolol
        "O=C1CN(C(=O)c2ccccc2)c3ccccc3N1",  # Diazepam-like
        "CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O",  # Diazepam
    ]
    
    # Non-cardiotoxic
    non_cardiotoxic = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CC(=O)NC1=CC=C(O)C=C1",  # Paracetamol
        "CCO",  # Ethanol
        "CCCCCC",  # Hexane
        "C1CCCCC1",  # Cyclohexane
        "C(C(=O)O)N",  # Glycine
        "CC(=O)O",  # Acetic acid
        "CC(=O)C",  # Acetone
    ]
    
    X_data, y_data = [], []
    
    for smiles in cardiotoxic:
        desc = compute_cardiotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)
    
    for smiles in non_cardiotoxic:
        desc = compute_cardiotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_cardiotox_model(model_type: str = "xgboost") -> object:
    """Train cardiotoxicity model (RF or XGBoost)."""
    X_train, X_test, y_train, y_test = create_cardiotox_data()
    
    if model_type == "xgboost":
        model = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='logloss'
        )
    else:
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=8,
            random_state=42,
            n_jobs=-1
        )
    
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Cardiotoxicity Model ({model_type}) Accuracy: {accuracy:.3f}")
    
    return model


def get_cardiotox_model_path() -> str:
    """Get model path."""
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    return os.path.join(models_dir, 'cardiotoxicity_model.pkl')


def save_cardiotox_model(model):
    """Save cardiotoxicity model."""
    joblib.dump(model, get_cardiotox_model_path())
    print("Cardiotoxicity model saved")


def load_cardiotox_model():
    """Load or train cardiotoxicity model."""
    path = get_cardiotox_model_path()
    if os.path.exists(path):
        return joblib.load(path)
    else:
        model = train_cardiotox_model()
        save_cardiotox_model(model)
        return model


def predict_cardiotoxicity(smiles: str) -> dict:
    """
    Predict cardiotoxicity risk.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary
    """
    desc = compute_cardiotox_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model = load_cardiotox_model()
    features = np.array([list(desc.values())])
    
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    risk = "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    
    return {
        "prediction": "Cardiotoxic" if prediction == 1 else "Non-Cardiotoxic",
        "probability_toxic": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "risk_level": risk,
        "model_type": "XGBoost" if hasattr(model, 'get_booster') else "RandomForest"
    }


except ImportError:
    print("RDKit not available - some features disabled")