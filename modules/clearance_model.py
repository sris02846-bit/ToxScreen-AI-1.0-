"""
Clearance (CL) and Half-Life Prediction Module
Predicts clearance rate and calculates half-life using Vd.
"""

import numpy as np
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
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


def compute_cl_descriptors(smiles: str) -> dict:
    """
    Compute molecular descriptors for clearance prediction.
    
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
        'NOCount': Descriptors.NOCount(mol),
    }
    
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=32)
    for i in range(32):
        descriptors[f'FP_{i}'] = int(fp[i])
    
    return descriptors


def create_clearance_data() -> tuple:
    """Create clearance training data. Values in mL/min/kg."""
    compounds = [
        ("CC(=O)OC1=CC=CC=C1C(=O)O", 9.0),   # Aspirin
        ("CC(C)CC1=CC=C(C=C1)C(C)C(=O)O", 0.75),  # Ibuprofen - low CL
        ("CN1C=NC2=C1C(=O)N(C(=O)N2C)C", 1.5),   # Caffeine
        ("CCO", 6.0),   # Ethanol
        ("CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O", 15.0),  # Morphine
        ("CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O", 0.38),  # Diazepam - very low CL
        ("CCN(CC)CC(=O)Nc1c(C)cccc1C", 10.0),  # Lidocaine
        ("CC(C)NCC(O)COc1cccc2ccccc12", 12.0),  # Propranolol
        ("CC(=O)NC1=CC=C(O)C=C1", 5.0),   # Paracetamol
        ("C(C(=O)O)N", 7.0),   # Glycine
    ]
    
    X_data, y_data = [], []
    
    for smiles, cl in compounds:
        desc = compute_cl_descriptors(smiles)
        if desc:
            X_data.append(list(desc.values()))
            y_data.append(cl)
    
    X = np.array(X_data)
    y = np.array(y_data)
    
    return train_test_split(X, y, test_size=0.2, random_state=42)


def train_clearance_model() -> RandomForestRegressor:
    """Train clearance regression model."""
    X_train, X_test, y_train, y_test = create_clearance_data()
    
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=8,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    r2 = model.score(X_test, y_test)
    print(f"Clearance Model R2: {r2:.3f}")
    
    return model


def calculate_half_life(vd: float, cl: float) -> float:
    """
    Calculate elimination half-life.
    
    t1/2 = (0.693 * Vd) / CL
    
    Args:
        vd: Volume of distribution (L/kg)
        cl: Clearance (mL/min/kg)
        
    Returns:
        Half-life in hours
    """
    # Convert CL to L/hr/kg
    cl_l_hr = cl * 0.06  # mL/min/kg to L/hr/kg
    
    if cl_l_hr > 0:
        t_half = (0.693 * vd) / cl_l_hr
        return round(t_half, 1)
    return 0


def predict_clearance_and_halflife(smiles: str, vd: float = None) -> dict:
    """
    Predict clearance and calculate half-life.
    
    Args:
        smiles: SMILES string
        vd: Optional pre-calculated Vd
        
    Returns:
        Prediction dictionary
    """
    desc = compute_cl_descriptors(smiles)
    if desc is None:
        return {"error": "Invalid SMILES"}
    
    model = load_model("clearance_model")
    if model is None:
        model = train_clearance_model()
        save_model(model, "clearance_model")
    
    features = np.array([list(desc.values())])
    cl = model.predict(features)[0]
    cl = max(0.01, cl)
    
    # Calculate half-life if Vd is provided
    t_half = None
    if vd is not None:
        t_half = calculate_half_life(vd, cl)
    
    # Interpretation
    if cl < 2:
        cl_class = "Low"
        cl_interp = "Slow elimination. May require dose adjustment."
    elif cl < 10:
        cl_class = "Moderate"
        cl_interp = "Standard elimination rate."
    else:
        cl_class = "High"
        cl_interp = "Rapid elimination. May require frequent dosing."
    
    result = {
        "clearance": round(cl, 2),
        "cl_unit": "mL/min/kg",
        "cl_class": cl_class,
        "cl_interpretation": cl_interp,
    }
    
    if t_half is not None:
        if t_half < 2:
            half_class = "Short"
            half_interp = "Rapidly eliminated. Frequent dosing needed."
        elif t_half < 8:
            half_class = "Moderate"
            half_interp = "Standard dosing interval (e.g., TID)."
        elif t_half < 24:
            half_class = "Long"
            half_interp = "Once-daily dosing possible."
        else:
            half_class = "Very Long"
            half_interp = "Accumulation risk. Monitor carefully."
        
        result["half_life"] = t_half
        result["half_life_unit"] = "hours"
        result["half_life_class"] = half_class
        result["half_life_interpretation"] = half_interp
    
    return result
