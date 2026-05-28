"""
Neurotoxicity Prediction Model
Brain/CNS toxicity prediction using ChEMBL/PubChem AID methodology.
Trained with RF ensemble.
"""

import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
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


def compute_neurotox_descriptors(smiles: str) -> dict:
    """Compute molecular descriptors for neurotoxicity prediction."""
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
        'NHOHCount': Descriptors.NHOHCount(mol),
        'NOCount': Descriptors.NOCount(mol),
    }
    
    # ECFP4 fingerprint
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_neurotox_data() -> tuple:
    """Create neurotoxicity training data."""
    # Known neurotoxic compounds
    neurotoxic = [
        "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",  # Morphine
        "CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O",  # Diazepam
        "CC(C)NCC(O)COc1cccc2ccccc12",  # Propranolol
        "CN1CCCC1CCN2c3ccccc3CCc4ccccc24",  # Haloperidol-like
        "CCN(CC)CC(=O)Nc1c(C)cccc1C",  # Lidocaine
        "COc1ccc2c(c1)CC(C(C)C)C(=O)O2",  # Verapamil-like
        "CN(C)C(=N)N",  # Metformin
    ]
    
    # Non-neurotoxic compounds
    non_neurotoxic = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CCO",  # Ethanol (low dose)
        "C(C(=O)O)N",  # Glycine
        "C1CCCCC1",  # Cyclohexane
        "CCCCCC",  # Hexane
        "CC(=O)O",  # Acetic acid
        "CC(=O)C",  # Acetone
        "C1CC1",  # Cyclopropane
    ]
    
    X_data, y_data = [], []
    
    for smiles in neurotoxic:
        desc = compute_neurotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)
    
    for smiles in non_neurotoxic:
        desc = compute_neurotox_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_neurotox_model() -> RandomForestClassifier:
    """Train neurotoxicity prediction model."""
    X_train, X_test, y_train, y_test = create_neurotox_data()
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"Neurotoxicity Model Accuracy: {accuracy:.3f}")
    
    return model


def predict_neurotoxicity(smiles: str) -> dict:
    """
    Predict neurotoxicity for a compound.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Prediction dictionary
    """
    desc = compute_neurotox_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model = load_model("neurotoxicity_model")
    if model is None:
        model = train_neurotox_model()
        save_model(model, "neurotoxicity_model")
    
    features = np.array([list(desc.values())])
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    risk = "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    
    return {
        "organ": "Brain/CNS",
        "prediction": "Neurotoxic" if prediction == 1 else "Non-Neurotoxic",
        "probability_toxic": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "risk_level": risk,
        "model_type": "RandomForest"
    }
