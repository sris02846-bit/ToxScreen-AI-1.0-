"""
Drug-Drug Interaction Prediction Module
Predicts interactions, combined toxicity, and synergistic effects.
"""

import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
from rdkit import DataStructs
from typing import Dict, List, Tuple
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


# Known interaction mechanisms
INTERACTION_MECHANISMS = [
    {"name": "CYP3A4 Competition", "risk": "High", "effect": "Altered metabolism of both drugs"},
    {"name": "CYP2D6 Competition", "risk": "Medium", "effect": "Reduced clearance"},
    {"name": "Protein Binding Displacement", "risk": "High", "effect": "Increased free drug concentration"},
    {"name": "Renal Clearance Competition", "risk": "Medium", "effect": "Reduced excretion"},
    {"name": "P-glycoprotein Competition", "risk": "Medium", "effect": "Altered absorption/distribution"},
    {"name": "QT Prolongation Additive", "risk": "High", "effect": "Increased cardiac risk"},
    {"name": "Hepatotoxicity Additive", "risk": "High", "effect": "Combined liver toxicity"},
    {"name": "Nephrotoxicity Additive", "risk": "High", "effect": "Combined kidney damage"},
    {"name": "CNS Depression Additive", "risk": "High", "effect": "Enhanced sedation"},
    {"name": "Serotonin Syndrome Risk", "risk": "Critical", "effect": "Life-threatening serotonin toxicity"},
]


def compute_similarity(smiles1: str, smiles2: str) -> float:
    """Compute Tanimoto similarity between two compounds."""
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    
    if mol1 is None or mol2 is None:
        return 0.0
    
    fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, 2048)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, 2048)
    
    return DataStructs.TanimotoSimilarity(fp1, fp2)


def predict_drug_interaction(smiles1: str, smiles2: str, 
                              drug1_name: str = "Drug A",
                              drug2_name: str = "Drug B") -> Dict:
    """
    Predict potential drug-drug interactions.
    
    Args:
        smiles1: SMILES of first drug
        smiles2: SMILES of second drug
        drug1_name: Name of first drug
        drug2_name: Name of second drug
        
    Returns:
        Interaction prediction
    """
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    
    if mol1 is None or mol2 is None:
        return {"error": "Invalid SMILES"}
    
    # Compute properties
    logp1 = Descriptors.MolLogP(mol1)
    logp2 = Descriptors.MolLogP(mol2)
    mw1 = Descriptors.MolWt(mol1)
    mw2 = Descriptors.MolWt(mol2)
    
    # Tanimoto similarity
    similarity = compute_similarity(smiles1, smiles2)
    
    # Detect potential interactions
    detected_interactions = []
    
    # CYP competition (both lipophilic)
    if logp1 > 3 and logp2 > 3:
        detected_interactions.append(INTERACTION_MECHANISMS[0])
    
    # Protein binding (both >300 MW)
    if mw1 > 300 and mw2 > 300:
        detected_interactions.append(INTERACTION_MECHANISMS[2])
    
    # Structural similarity suggests similar targets
    if similarity > 0.5:
        detected_interactions.append(INTERACTION_MECHANISMS[6])
    
    # Both have nitrogen (potential CNS effects)
    if mol1.GetNumAtoms() > 10 and mol2.GetNumAtoms() > 10:
        detected_interactions.append(INTERACTION_MECHANISMS[8])
    
    # Risk assessment
    high_risks = sum(1 for i in detected_interactions if i["risk"] in ["High", "Critical"])
    
    if high_risks >= 2 or any(i["risk"] == "Critical" for i in detected_interactions):
        overall_risk = "Critical"
        recommendation = "CONTRAINDICATED - Do not co-administer"
    elif high_risks >= 1:
        overall_risk = "High"
        recommendation = "Use with extreme caution - Monitor closely"
    elif len(detected_interactions) >= 2:
        overall_risk = "Medium"
        recommendation = "Monitor for adverse effects"
    else:
        overall_risk = "Low"
        recommendation = "No significant interactions expected"
    
    return {
        "drug1": drug1_name,
        "drug2": drug2_name,
        "similarity": round(similarity, 3),
        "overall_risk": overall_risk,
        "recommendation": recommendation,
        "detected_interactions": [
            {"mechanism": i["name"], "risk": i["risk"], "effect": i["effect"]}
            for i in detected_interactions
        ],
        "monitoring": [
            "Monitor liver function tests",
            "Monitor for adverse effects",
            "Consider therapeutic drug monitoring"
        ] if overall_risk in ["High", "Critical"] else ["Routine monitoring"]
    }


def predict_synergistic_toxicity(smiles1: str, smiles2: str) -> Dict:
    """
    Predict synergistic toxicity effects.
    
    Args:
        smiles1: First compound
        smiles2: Second compound
        
    Returns:
        Synergy prediction
    """
    similarity = compute_similarity(smiles1, smiles2)
    
    mol1 = Chem.MolFromSmiles(smiles1)
    mol2 = Chem.MolFromSmiles(smiles2)
    
    logp1 = Descriptors.MolLogP(mol1) if mol1 else 0
    logp2 = Descriptors.MolLogP(mol2) if mol2 else 0
    
    # Synergy factors
    synergy_score = 0
    factors = []
    
    if similarity > 0.6:
        synergy_score += 30
        factors.append("High structural similarity - additive toxicity likely")
    
    if abs(logp1 - logp2) < 1:
        synergy_score += 20
        factors.append("Similar lipophilicity - same tissue distribution")
    
    if similarity > 0.3:
        synergy_score += 15
        factors.append("Moderate similarity - potential overlapping targets")
    
    synergy_score = min(100, synergy_score)
    
    if synergy_score >= 50:
        risk = "High"
        warning = "Significant synergistic toxicity risk"
    elif synergy_score >= 30:
        risk = "Medium"
        warning = "Moderate synergistic potential"
    else:
        risk = "Low"
        warning = "Minimal synergistic effects expected"
    
    return {
        "synergy_score": synergy_score,
        "risk_level": risk,
        "warning": warning,
        "factors": factors
    }
