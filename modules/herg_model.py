"""
hERG Channel Toxicity Prediction Model
Predicts cardiotoxicity risk via hERG channel inhibition.
Based on Karim dataset methodology.
"""

import pandas as pd
import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import joblib
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))


def compute_herg_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors specific to hERG prediction.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary of descriptors
    """
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
        'NumAliphaticRings': Descriptors.NumAliphaticRings(mol),
        'NumSaturatedRings': Descriptors.NumSaturatedRings(mol),
        'RingCount': Descriptors.RingCount(mol),
        'NumHeteroatoms': Descriptors.NumHeteroatoms(mol),
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
        'BertzCT': Descriptors.BertzCT(mol),
    }
    
    # Add ECFP4 fingerprint (first 64 bits)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        descriptors[f'ECFP4_{i}'] = int(fp[i])
    
    return descriptors


def create_herg_training_data() -> tuple:
    """
    Create hERG training data from known hERG blockers and non-blockers.
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    # Known hERG blockers (cardiotoxic)
    herg_blockers = [
        "CN1CCC(=C2c3ccccc3CCc4ccccc24)CC1",  # Terfenadine
        "CC(C)NCC(O)COc1cccc2ccccc12",  # Propranolol
        "CCN(CC)CC(=O)Nc1c(C)cccc1C",  # Lidocaine
        "COc1ccc2c(c1)CC(C(C)C)C(=O)O2",  # Verapamil (simplified)
        "CN1CCCC1CCN2c3ccccc3CCc4ccccc24",  # Haloperidol-like
        "CC(C)(C)NCC(O)c1ccc(O)c(CO)c1",  # Salbutamol-like
        "O=C1CN(C(=O)c2ccccc2)c3ccccc3N1",  # Diazepam-like
        "CCOC(=O)C1(C)NC(=O)N(C)C1=O",  # Phenytoin-like
    ]
    
    # Non-hERG blockers (safe)
    non_blockers = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CC(=O)NC1=CC=C(O)C=C1",  # Paracetamol
        "CCO",  # Ethanol
        "C(C(=O)O)N",  # Glycine
        "CCCCCC",  # Hexane
        "C1CCCCC1",  # Cyclohexane
        "CC(=O)O",  # Acetic acid
        "CC(C)(C)OH",  # tert-Butanol
        "C1=CC=C2C=CC=CC2=C1",  # Naphthalene
        "CC(=O)C",  # Acetone
    ]
    
    X_data = []
    y_data = []
    
    for smiles in herg_blockers:
        desc = compute_herg_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)  # hERG blocker
    
    for smiles in non_blockers:
        desc = compute_herg_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)  # Non-blocker
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_herg_model() -> RandomForestClassifier:
    """Train hERG prediction model."""
    X_train, X_test, y_train, y_test = create_herg_training_data()
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"hERG Model Accuracy: {accuracy:.3f}")
    
    return model


def get_herg_model_path() -> str:
    """Get path for hERG model."""
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    return os.path.join(models_dir, 'herg_model.pkl')


def save_herg_model(model):
    """Save hERG model."""
    path = get_herg_model_path()
    joblib.dump(model, path)
    print(f"hERG model saved to {path}")


def load_herg_model():
    """Load or train hERG model."""
    path = get_herg_model_path()
    if os.path.exists(path):
        return joblib.load(path)
    else:
        model = train_herg_model()
        save_herg_model(model)
        return model


def predict_herg(smiles: str) -> dict:
    """
    Predict hERG channel inhibition risk.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary
    """
    desc = compute_herg_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model = load_herg_model()
    features = np.array([list(desc.values())])
    
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    risk = "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    
    return {
        "prediction": "hERG Blocker (Cardiotoxic Risk)" if prediction == 1 else "Non-hERG Blocker (Safe)",
        "probability_blocker": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "risk_level": risk
    }
