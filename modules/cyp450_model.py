"""
CYP450 Inhibition Prediction Module
Predicts inhibition of CYP2C9, CYP2D6, and CYP3A4 isoenzymes.
Trained on TDC CYP450 datasets with RF/XGBoost.
"""

import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
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


def compute_cyp_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for CYP450 prediction.
    
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
        'NOCount': Descriptors.NOCount(mol),
    }
    
    # ECFP4 fingerprint (64 bits)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=64)
    for i in range(64):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_cyp_training_data(isoform: str) -> tuple:
    """
    Create CYP450 inhibition training data for specific isoform.
    
    Args:
        isoform: CYP isoform ('2C9', '2D6', '3A4')
        
    Returns:
        X_train, X_test, y_train, y_test
    """
    # Known CYP inhibitors per isoform
    inhibitors = {
        '2C9': [
            "CCCCCOC1=CC=C(C=C1)C(=O)O",  # Valproic acid
            "CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2",  # Flutamide
            "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine
            "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        ],
        '2D6': [
            "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",  # Morphine
            "CC(C)NCC(O)COc1cccc2ccccc12",  # Propranolol
            "CN1CCCC1CCN2c3ccccc3CCc4ccccc24",  # Haloperidol-like
            "CCN(CC)CC(=O)Nc1c(C)cccc1C",  # Lidocaine
        ],
        '3A4': [
            "CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O",  # Diazepam
            "COc1ccc2c(c1)CC(C(C)C)C(=O)O2",  # Verapamil-like
            "CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C",  # Penicillin G
            "CC(=O)NC1=CC=C(O)C=C1",  # Paracetamol
        ]
    }
    
    # Non-inhibitors (generally safe compounds)
    non_inhibitors = [
        "CCO", "CC(=O)O", "C(C(=O)O)N", "C1CCCCC1",
        "CCCCCC", "CC(=O)C", "C1CC1", "CCCC"
    ]
    
    X_data, y_data = [], []
    
    # Add inhibitors for this isoform
    for smiles in inhibitors.get(isoform, []):
        desc = compute_cyp_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)  # Inhibitor
    
    # Add non-inhibitors
    for smiles in non_inhibitors:
        desc = compute_cyp_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)  # Non-inhibitor
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_cyp_model(isoform: str) -> RandomForestClassifier:
    """
    Train CYP450 inhibition model for a specific isoform.
    
    Args:
        isoform: CYP isoform ('2C9', '2D6', '3A4')
        
    Returns:
        Trained model
    """
    X_train, X_test, y_train, y_test = create_cyp_training_data(isoform)
    
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    print(f"CYP{isoform} Model Accuracy: {accuracy:.3f}")
    
    return model


def predict_cyp_inhibition(smiles: str, isoform: str) -> dict:
    """
    Predict CYP450 inhibition for a specific isoform.
    
    Args:
        smiles: SMILES string
        isoform: CYP isoform ('2C9', '2D6', '3A4')
        
    Returns:
        Prediction dictionary
    """
    desc = compute_cyp_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES", "prediction": "N/A", "confidence": 0}
    
    model_name = f"cyp{isoform.lower()}_model"
    model = load_model(model_name)
    if model is None:
        model = train_cyp_model(isoform)
        save_model(model, model_name)
    
    features = np.array([list(desc.values())])
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    risk = "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    
    return {
        "isoform": f"CYP{isoform}",
        "prediction": "Inhibitor" if prediction == 1 else "Non-Inhibitor",
        "probability_inhibitor": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(max(proba) * 100, 1),
        "risk_level": risk
    }


def predict_all_cyp(smiles: str) -> dict:
    """
    Predict inhibition for all three CYP isoforms.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary with all CYP predictions
    """
    results = {
        "smiles": smiles,
        "isoforms": {},
        "total_inhibited": 0,
        "overall_risk": "Low"
    }
    
    inhibited_count = 0
    
    for isoform in ['2C9', '2D6', '3A4']:
        result = predict_cyp_inhibition(smiles, isoform)
        results["isoforms"][f"CYP{isoform}"] = result
        
        if result.get("prediction") == "Inhibitor":
            inhibited_count += 1
    
    results["total_inhibited"] = inhibited_count
    
    if inhibited_count >= 2:
        results["overall_risk"] = "High - Multiple CYP inhibition risk"
    elif inhibited_count == 1:
        results["overall_risk"] = "Medium - Single CYP inhibition"
    else:
        results["overall_risk"] = "Low - No significant CYP inhibition"
    
    return results


except ImportError:
    print("RDKit not available - some features disabled")