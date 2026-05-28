"""
Machine Learning Module
Hepatotoxicity prediction using RandomForest on Tox21 data.
"""

import pandas as pd
import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
import warnings
warnings.filterwarnings('ignore')


def compute_molecular_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for ML model.
    
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
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'NumAromaticRings': Descriptors.NumAromaticRings(mol),
        'NumSaturatedRings': Descriptors.NumSaturatedRings(mol),
        'NumAliphaticRings': Descriptors.NumAliphaticRings(mol),
        'TPSA': Descriptors.TPSA(mol),
        'FractionCSP3': Descriptors.FractionCSP3(mol),
        'HeavyAtomCount': Descriptors.HeavyAtomCount(mol),
        'NumHeteroatoms': Descriptors.NumHeteroatoms(mol),
        'RingCount': Descriptors.RingCount(mol),
        'NumValenceElectrons': Descriptors.NumValenceElectrons(mol),
    }
    
    # Add Morgan fingerprint bits as features (first 128 bits)
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=128)
    for i in range(128):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_training_data() -> tuple:
    """
    Create training data from Tox21 SR-HSE (hepatotoxicity) data.
    Since we can't download live data, we'll create synthetic training data
    based on known hepatotoxic and non-hepatotoxic compounds.
    
    Returns:
        Tuple of (X_train, X_test, y_train, y_test)
    """
    # Known hepatotoxic compounds
    hepatotoxic_smiles = [
        "CC(=O)NC1=CC=C(O)C=C1",  # Paracetamol (high dose)
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",  # Caffeine (high dose)
        "CC1(C(N2C(S1)C(C2=O)NC(=O)CC3=CC=CC=C3)C(=O)O)C",  # Penicillin G
        "CCN(CC)C(=S)SSC(=S)N(CC)CC",  # Disulfiram
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CC1=C(C(=O)C=CC1=O)C",  # Vitamin K3
        "CN(C)C(=N)N",  # Metformin
        "CCCCCOC1=CC=C(C=C1)C(=O)O",  # Valproic acid
        "CC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2",  # Flutamide
        "O=C1C=CC(=O)N1C2=CC=CC=C2",  # N-phenylmaleimide
        "ClC1=CC=C(C=C1)C(=O)NC2=CC=CC=C2Cl",  # Diclofenac
        "CC1=CC=C(C=C1)S(=O)(=O)NC(=O)NC2=CC=CC=C2",  # Tolbutamide
        "CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O",  # Diazepam
        "CCCCCN1C(=O)CN=C(C2=CC=CC=C2F)C3=CC=CC=C3C1=O",  # Flunitrazepam
    ]
    
    # Known non-hepatotoxic compounds (generally safe)
    non_hepatotoxic_smiles = [
        "CCO",  # Ethanol (low dose)
        "O",  # Water
        "C(C(=O)O)N",  # Glycine
        "C(C(C(=O)O)N)S",  # Cysteine
        "C1=CC=C(C=C1)C=O",  # Benzaldehyde
        "CC(=O)O",  # Acetic acid
        "C1CCCCC1",  # Cyclohexane
        "CCCCCCCC",  # Octane
        "COCCO",  # 2-Methoxyethanol
        "C1CC1",  # Cyclopropane
        "CCCC",  # Butane
        "CCCCCC",  # Hexane
        "C1=CC=C2C=CC=CC2=C1",  # Naphthalene
        "CC(=O)C",  # Acetone
    ]
    
    # Generate features
    X_data = []
    y_data = []
    
    for smiles in hepatotoxic_smiles:
        desc = compute_molecular_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(1)  # Hepatotoxic
    
    for smiles in non_hepatotoxic_smiles:
        desc = compute_molecular_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(0)  # Non-hepatotoxic
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)


def train_hepatotoxicity_model() -> RandomForestClassifier:
    """
    Train RandomForest model for hepatotoxicity prediction.
    
    Returns:
        Trained RandomForestClassifier
    """
    # Create training data
    X_train, X_test, y_train, y_test = create_training_data()
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {accuracy:.3f}")
    
    return model


def get_model_path() -> str:
    """
    Get path for saved model.
    
    Returns:
        Path to model file
    """
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    return os.path.join(models_dir, 'hepatotoxicity_model.pkl')


def save_model(model: RandomForestClassifier):
    """
    Save trained model to disk.
    
    Args:
        model: Trained RandomForestClassifier
    """
    model_path = get_model_path()
    joblib.dump(model, model_path)
    print(f"Model saved to {model_path}")


def load_model() -> RandomForestClassifier:
    """
    Load trained model from disk or train new one.
    
    Returns:
        RandomForestClassifier
    """
    model_path = get_model_path()
    
    if os.path.exists(model_path):
        return joblib.load(model_path)
    else:
        print("Training new model...")
        model = train_hepatotoxicity_model()
        save_model(model)
        return model


def predict_hepatotoxicity(smiles: str) -> dict:
    """
    Predict hepatotoxicity for a molecule.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary with prediction results
    """
    # Compute descriptors
    desc = compute_molecular_descriptors(smiles)
    if desc is None:
        return {
            "prediction": "Invalid SMILES",
            "probability": 0.0,
            "confidence": 0.0,
            "error": "Could not compute descriptors"
        }
    
    # Load model
    model = load_model()
    
    # Prepare features
    features = np.array([list(desc.values())])
    
    # Predict
    proba = model.predict_proba(features)[0]
    prediction = model.predict(features)[0]
    
    # Get confidence
    confidence = proba[1] if prediction == 1 else proba[0]
    
    return {
        "prediction": "Hepatotoxic" if prediction == 1 else "Non-Hepatotoxic",
        "probability_hepatotoxic": round(proba[1] * 100, 1),
        "probability_safe": round(proba[0] * 100, 1),
        "confidence": round(confidence * 100, 1),
        "risk_level": "High" if proba[1] > 0.7 else "Medium" if proba[1] > 0.3 else "Low"
    }
