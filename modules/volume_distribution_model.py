"""
Volume of Distribution (Vd) Prediction Module
Predicts Vd (L/kg) using molecular descriptors.
Trained with RandomForest regression.
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


def compute_vd_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for Vd prediction.
    
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
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=32)
    for i in range(32):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_vd_data() -> tuple:
    """Create Vd training data. Values in L/kg."""
    compounds = [
        ("CC(=O)OC1=CC=CC=C1C(=O)O", 0.15),  # Aspirin - low Vd
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", 0.12),  # Ibuprofen
        ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", 0.60),  # Caffeine - moderate
        ("CCO", 0.55),  # Ethanol
        ("CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O", 3.50),  # Morphine - high Vd
        ("CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O", 1.10),  # Diazepam
        ("CCN(CC)CC(=O)Nc1c(C)cccc1C", 1.30),  # Lidocaine
        ("CC(C)NCC(O)COc1cccc2ccccc12", 4.00),  # Propranolol - high Vd
        ("CC(=O)NC1=CC=C(O)C=C1", 0.90),  # Paracetamol
        ("C(C(=O)O)N", 0.60),  # Glycine
    ]
    
    X_data, y_data = [], []
    
    for smiles, vd in compounds:
        desc = compute_vd_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(vd)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_vd_model() -> RandomForestRegressor:
    """Train Vd regression model."""
    X_train, X_test, y_train, y_test = create_vd_data()
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    r2 = model.score(X_test, y_test)
    print(f"Volume of Distribution Model R2: {r2:.3f}")
    
    return model


def predict_volume_distribution(smiles: str) -> dict:
    """
    Predict Volume of Distribution (Vd).
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary with interpretation
    """
    desc = compute_vd_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A"}
    
    model = load_model("volume_distribution_model")
    if model is None:
        model = train_vd_model()
        save_model(model, "volume_distribution_model")
    
    features = np.array([list(desc.values())])
    vd = model.predict(features)[0]
    vd = max(0.01, vd)  # Ensure positive
    
    # Interpretation
    if vd < 0.3:
        vd_class = "Low"
        interpretation = "Confined to plasma. Limited tissue distribution."
    elif vd < 1.0:
        vd_class = "Moderate"
        interpretation = "Distributed in extracellular fluid."
    elif vd < 3.0:
        vd_class = "High"
        interpretation = "Wide tissue distribution."
    else:
        vd_class = "Very High"
        interpretation = "Extensive tissue binding. May accumulate in tissues."
    
    return {
        "vd": round(vd, 2),
        "unit": "L/kg",
        "vd_class": vd_class,
        "interpretation": interpretation,
        "total_body_water": f"{round(vd * 70, 1)} L (for 70 kg person)"
    }


except ImportError:
    print("RDKit not available - some features disabled")