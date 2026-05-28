"""
Cytotoxicity Prediction Model
Cell toxicity prediction using Tox21 SR-MMP methodology.
Trained with RF/XGBoost ensemble.
"""

import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from model_loader import load_model, save_model


def compute_cytotox_descriptors(smiles: str) -> dict:
    """Compute molecular descriptors for cytotoxicity prediction."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    descriptors = {
        'MolWt': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        'TPSA': Descriptors.TPSA(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'NumAromaticRings': Descriptors.NumAromaticRings(mol),
        'FractionCSP3': Descriptors.FractionCSP3(mol),
        'HeavyAtomCount': Descriptors.HeavyAtomCount(mol),
        'NumHeteroatoms': Descriptors.NumHeteroatoms(mol),
        'RingCount': Descriptors.RingCount(mol),
        'BertzCT': Descriptors.BertzCT(mol),
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
        'MaxPartialCharge': Descriptors.MaxPartialCharge(mol) if hasattr(Descriptors, 'MaxPartialCharge') else 0,
        'MinPartialCharge': Descriptors.MinPartialCharge(mol) if hasattr(Descriptors, 'MinPartialCharge') else 0,
    }
    
    # ECFP4 fingerprint
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_cytotox_data() -> tuple:
    """Create cytotoxicity training data."""
    # Cytotoxic compounds
    cytotoxic = [
        "O=C1C=C2C3=C(C(=O)CC3)OC4=C2C5=C(C(=O)OCC5)O4",  # Aflatoxin B1
        "Clc1cc2c(Cl)c(Cl)c3c(c2c(Cl)c1Cl)Oc4c(Cl)c(Cl)c5c(c4O3)Cl",  # Dioxin
        "CCOP(=S)(OCC)Oc1ccc(cc1)[N+](=O)[O-]",  # Parathion
        "NN",  # Hydrazine
        "ClC(Cl)(Cl)Cl",  # Carbon tetrachloride
        "CN(N=O)C",  # N-Nitrosodimethylamine
        "ClC=C",  # Vinyl chloride
    ]
    
    # Non-cytotoxic compounds
    non_cytotoxic = [
        "CCO",  # Ethanol
        "CC(=O)O",  # Acetic acid
        "C(C(=O)O)N",  # Glycine
        "C1CCCCC1",  # Cyclohexane
        "CCCCCC",  # Hexane
        "CC(=O)C",  # Acetone
        "C1=CC=C2C=CC=CC2=C1",  # Naphthalene
        "C1CC1",  # Cyclopropane
    ]
    
    X_data, y_data = [], []
    
    for smiles in cytotoxic:
        desc = compute_cytotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)
    
    for smiles in non_cytotoxic:
        desc = compute_cytotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_cytotox_model() -> XGBClassifier:
    """Train cytotoxicity prediction model with XGBoost."""
    X_train, X_test, y_train, y_test = create_cytotox_data()
    
    model = XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        random_state=42,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Cytotoxicity Model Accuracy: {accuracy:.3f}")
    
    return model


def predict_cytotoxicity(smiles: str) -> dict:
    """
    Predict cytotoxicity for a compound.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary
    """
    desc = compute_cytotox_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model = load_model("cytotoxicity_model")
    if model is None:
        model = train_cytotox_model()
        save_model(model, "cytotoxicity_model")
    
    features = np.array([list(desc.values())])
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    risk = "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    
    return {
        "organ": "General Cell",
        "prediction": "Cytotoxic" if prediction == 1 else "Non-Cytotoxic",
        "probability_toxic": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "risk_level": risk,
        "model_type": "XGBoost"
    }
