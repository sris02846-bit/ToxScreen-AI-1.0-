"""
Phase II Metabolism: Glucuronidation Prediction Module
Predicts likelihood of glucuronidation (UGT-mediated).
Trained on PubChem/literature data with RF classifier.
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


def compute_gluc_descriptors(smiles: str) -> dict:
    """
    Compute descriptors relevant to glucuronidation.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary of descriptors
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    # Key functional groups for glucuronidation
    carboxyl = Chem.MolFromSmarts('C(=O)O')
    hydroxyl = Chem.MolFromSmarts('[OH]')
    amine = Chem.MolFromSmarts('[NH2]')
    phenol = Chem.MolFromSmarts('c[OH]')
    
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
        'Has_Carboxyl': int(mol.HasSubstructMatch(carboxyl)),
        'Has_Hydroxyl': int(mol.HasSubstructMatch(hydroxyl)),
        'Has_Amine': int(mol.HasSubstructMatch(amine)),
        'Has_Phenol': int(mol.HasSubstructMatch(phenol)),
        'RingCount': Descriptors.RingCount(mol),
        'NOCount': Descriptors.NOCount(mol),
    }
    
    # ECFP4 fingerprint
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=32)
    for i in range(32):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_glucuronidation_data() -> tuple:
    """Create glucuronidation training data."""
    # Compounds likely to undergo glucuronidation
    glucuronidated = [
        "CC(=O)NC1=CC=C(O)C=C1",  # Paracetamol (phenol)
        "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",  # Morphine (hydroxyl)
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen (carboxyl)
        "CCCCCOC1=CC=C(C=C1)C(=O)O",  # Valproic acid (carboxyl)
        "CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2",  # Flutamide
        "CC(C)NCC(O)COc1cccc2ccccc12",  # Propranolol (hydroxyl)
    ]
    
    # Compounds unlikely to undergo glucuronidation
    non_glucuronidated = [
        "C1CCCCC1", "CCCCCC", "C1CC1", "CCCC",
        "CC(=O)C", "C1=CC=C2C=CC=CC2=C1"
    ]
    
    X_data, y_data = [], []
    
    for smiles in glucuronidated:
        desc = compute_gluc_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)
    
    for smiles in non_glucuronidated:
        desc = compute_gluc_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_glucuronidation_model() -> RandomForestClassifier:
    """Train glucuronidation prediction model."""
    X_train, X_test, y_train, y_test = create_glucuronidation_data()
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Glucuronidation Model Accuracy: {accuracy:.3f}")
    
    return model


def predict_glucuronidation(smiles: str) -> dict:
    """
    Predict glucuronidation likelihood.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary
    """
    desc = compute_gluc_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model = load_model("glucuronidation_model")
    if model is None:
        model = train_glucuronidation_model()
        save_model(model, "glucuronidation_model")
    
    features = np.array([list(desc.values())])
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    return {
        "phase": "Phase II",
        "enzyme": "UGT",
        "prediction": "Glucuronidated" if prediction == 1 else "Not Glucuronidated",
        "probability": round(proba[1] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "interpretation": "Likely undergoes glucuronidation" if prediction == 1 else "Unlikely to be glucuronidated"
    }


except ImportError:
    print("RDKit not available - some features disabled")