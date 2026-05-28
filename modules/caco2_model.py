"""
Caco-2 Permeability Prediction Module
Predicts intestinal absorption using Caco-2 cell permeability.
Trained with regression model (logPapp prediction).
"""

import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))
from model_loader import load_model, save_model


def compute_caco2_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for Caco-2 permeability prediction.
    
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
        'NOCount': Descriptors.NOCount(mol),
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
    }
    
    # ECFP4 fingerprint
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=32)
    for i in range(32):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_caco2_data() -> tuple:
    """Create Caco-2 permeability training data."""
    # High permeability compounds (logPapp > -5)
    high_perm = [
        ("CC(=O)OC1=CC=CC=C1C(=O)O", -4.5),  # Aspirin
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", -4.2),  # Ibuprofen
        ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", -4.8),  # Caffeine
        ("CCO", -5.0),  # Ethanol
        ("c1ccccc1", -4.0),  # Benzene
    ]
    
    # Low permeability compounds (logPapp < -6)
    low_perm = [
        ("C(C1C(C(C(C(O1)O)O)O)O)O", -6.5),  # Glucose
        ("C(C(=O)O)N", -6.8),  # Glycine
        ("CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O", -6.2),  # Morphine
        ("CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C", -6.0),  # Penicillin G
    ]
    
    X_data, y_data = [], []
    
    for smiles, logpapp in high_perm + low_perm:
        desc = compute_caco2_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(logpapp)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_caco2_model() -> RandomForestRegressor:
    """Train Caco-2 permeability regression model."""
    X_train, X_test, y_train, y_test = create_caco2_data()
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    r2 = model.score(X_test, y_test)
    print(f"Caco-2 Model R2 Score: {r2:.3f}")
    
    return model


def predict_caco2(smiles: str) -> dict:
    """
    Predict Caco-2 permeability (logPapp).
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary with absorption interpretation
    """
    desc = compute_caco2_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A"}
    
    model = load_model("caco2_model")
    if model is None:
        model = train_caco2_model()
        save_model(model, "caco2_model")
    
    features = np.array([list(desc.values())])
    logpapp = model.predict(features)[0]
    
    # Interpret permeability
    if logpapp > -5:
        absorption = "High"
        interpretation = "Excellent intestinal absorption expected"
    elif logpapp > -6:
        absorption = "Moderate"
        interpretation = "Moderate intestinal absorption"
    else:
        absorption = "Low"
        interpretation = "Poor intestinal absorption - may require formulation"
    
    return {
        "model": "Caco-2 Permeability",
        "logPapp": round(logpapp, 2),
        "unit": "log cm/s",
        "absorption": absorption,
        "interpretation": interpretation,
        "threshold_high": "> -5",
        "threshold_low": "< -6"
    }


except ImportError:
    print("RDKit not available - some features disabled")