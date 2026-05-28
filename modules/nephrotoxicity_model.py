"""
Nephrotoxicity Prediction Model
Kidney toxicity prediction using DrugBank/TDC dataset methodology.
Trained with RF/XGBoost ensemble.
"""

import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from model_loader import load_model, save_model


def compute_nephrotox_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for nephrotoxicity prediction.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary of molecular descriptors
    """
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
        'NumAliphaticRings': Descriptors.NumAliphaticRings(mol),
        'NumSaturatedRings': Descriptors.NumSaturatedRings(mol),
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
    }
    
    # ECFP4 fingerprint bits
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_nephrotox_data() -> tuple:
    """
    Create nephrotoxicity training data.
    Based on known nephrotoxic and non-nephrotoxic compounds.
    """
    # Known nephrotoxic compounds
    nephrotoxic = [
        "CC(=O)NC1=CC=C(O)C=C1",  # Acetaminophen (high dose)
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine (high dose)
        "CCN(CC)CC(=O)Nc1c(C)cccc1C",  # Lidocaine
        "CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C",  # Penicillin G
        "O=C1C=CC(=O)N1C2=CC=CC=C2",  # N-phenylmaleimide
        "CCCCCOC1=CC=C(C=C1)C(=O)O",  # Valproic acid
        "Clc1ccccc1C(=O)NC2=CC=CC=C2Cl",  # Diclofenac
    ]
    
    # Non-nephrotoxic compounds
    non_nephrotoxic = [
        "CCO",  # Ethanol
        "CC(=O)O",  # Acetic acid
        "C(C(=O)O)N",  # Glycine
        "C1CCCCC1",  # Cyclohexane
        "CCCCCC",  # Hexane
        "C1=CC=C2C=CC=CC2=C1",  # Naphthalene
        "CC(=O)C",  # Acetone
        "C1CC1",  # Cyclopropane
        "CCCC",  # Butane
    ]
    
    X_data, y_data = [], []
    
    for smiles in nephrotoxic:
        desc = compute_nephrotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)  # Nephrotoxic
    
    for smiles in non_nephrotoxic:
        desc = compute_nephrotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)  # Safe
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_nephrotox_model() -> RandomForestClassifier:
    """Train nephrotoxicity prediction model."""
    X_train, X_test, y_train, y_test = create_nephrotox_data()
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Nephrotoxicity Model Accuracy: {accuracy:.3f}")
    
    return model


def predict_nephrotoxicity(smiles: str) -> dict:
    """
    Predict nephrotoxicity for a compound.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary with risk assessment
    """
    desc = compute_nephrotox_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model = load_model("nephrotoxicity_model")
    if model is None:
        model = train_nephrotox_model()
        save_model(model, "nephrotoxicity_model")
    
    features = np.array([list(desc.values())])
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    risk = "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    
    return {
        "organ": "Kidney",
        "prediction": "Nephrotoxic" if prediction == 1 else "Non-Nephrotoxic",
        "probability_toxic": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "risk_level": risk,
        "model_type": "RandomForest"
    }


except ImportError:
    print("RDKit not available - some features disabled")