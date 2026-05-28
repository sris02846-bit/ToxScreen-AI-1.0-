"""
Plasma Protein Binding Prediction Module
Predicts fraction unbound (fu) using molecular descriptors.
Trained with RandomForest regression on literature data.
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


def compute_ppb_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for protein binding prediction.
    
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
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
        'NOCount': Descriptors.NOCount(mol),
        'NumAliphaticRings': Descriptors.NumAliphaticRings(mol),
        'NumSaturatedRings': Descriptors.NumSaturatedRings(mol),
    }
    
    # ECFP4 fingerprint (32 bits for regression)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=32)
    for i in range(32):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_ppb_data() -> tuple:
    """
    Create plasma protein binding training data.
    Values represent fraction unbound (fu) - higher = less binding.
    """
    # (smiles, fraction_unbound)
    compounds = [
        ("CC(=O)OC1=CC=CC=C1C(=O)O", 0.50),  # Aspirin - moderate binding
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", 0.01),  # Ibuprofen - high binding
        ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", 0.64),  # Caffeine - low binding
        ("CCO", 0.95),  # Ethanol - very low binding
        ("c1ccccc1", 0.05),  # Benzene - high binding
        ("CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O", 0.65),  # Morphine
        ("CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O", 0.02),  # Diazepam - high binding
        ("CCN(CC)CC(=O)Nc1c(C)cccc1C", 0.30),  # Lidocaine
        ("CC(C)NCC(O)COc1cccc2ccccc12", 0.10),  # Propranolol - high binding
        ("CC(=O)NC1=CC=C(O)C=C1", 0.80),  # Paracetamol - low binding
        ("C(C(=O)O)N", 0.90),  # Glycine
        ("C1CCCCC1", 0.20),  # Cyclohexane
    ]
    
    X_data, y_data = [], []
    
    for smiles, fu in compounds:
        desc = compute_ppb_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(fu)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_ppb_model() -> RandomForestRegressor:
    """Train plasma protein binding regression model."""
    X_train, X_test, y_train, y_test = create_ppb_data()
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    r2 = model.score(X_test, y_test)
    print(f"Protein Binding Model R2: {r2:.3f}")
    
    return model


def predict_protein_binding(smiles: str) -> dict:
    """
    Predict plasma protein binding (fraction unbound).
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary with interpretation
    """
    desc = compute_ppb_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A"}
    
    model = load_model("protein_binding_model")
    if model is None:
        model = train_ppb_model()
        save_model(model, "protein_binding_model")
    
    features = np.array([list(desc.values())])
    fu = model.predict(features)[0]
    fu = max(0.001, min(0.999, fu))  # Clamp to valid range
    
    # Calculate percent bound
    percent_bound = round((1 - fu) * 100, 1)
    percent_unbound = round(fu * 100, 1)
    
    # Interpretation
    if percent_bound >= 90:
        binding_class = "High"
        interpretation = "Highly protein bound. May affect drug distribution and interactions."
    elif percent_bound >= 50:
        binding_class = "Moderate"
        interpretation = "Moderate protein binding. Standard distribution expected."
    else:
        binding_class = "Low"
        interpretation = "Low protein binding. Higher free fraction available for activity."
    
    return {
        "fraction_unbound": round(fu, 3),
        "percent_bound": percent_bound,
        "percent_unbound": percent_unbound,
        "binding_class": binding_class,
        "interpretation": interpretation,
        "unit": "fraction unbound (fu)"
    }


except ImportError:
    print("RDKit not available - some features disabled")