"""
Disease State Adjustments Module
Liver/kidney impairment predictions and age-based dosing.
"""

from rdkit import Chem
from rdkit.Chem import Descriptors
from typing import Dict, List
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


def predict_liver_impairment_risk(smiles: str) -> Dict:
    """
    Predict risk in liver impairment.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Liver impairment risk assessment
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    
    # Risk factors for liver impairment
    risk_score = 0
    factors = []
    
    if mw > 500:
        risk_score += 20
        factors.append("High MW - accumulation risk in hepatic impairment")
    
    if logp > 4:
        risk_score += 25
        factors.append("High lipophilicity - extensive hepatic metabolism")
    
    if logp > 2:
        risk_score += 10
        factors.append("Moderate hepatic metabolism expected")
    
    if tpsa > 140:
        risk_score += 10
        factors.append("High polarity - potential biliary excretion")
    
    # Liver impairment categories
    categories = {
        "mild": {"factor": 0.8, "adjustment": "20% dose reduction"},
        "moderate": {"factor": 0.5, "adjustment": "50% dose reduction"},
        "severe": {"factor": 0.25, "adjustment": "75% dose reduction, consider alternative"},
    }
    
    if risk_score >= 40:
        risk = "High"
        recommendation = "Significant dose adjustment needed in hepatic impairment"
    elif risk_score >= 20:
        risk = "Medium"
        recommendation = "Moderate dose adjustment in hepatic impairment"
    else:
        risk = "Low"
        recommendation = "Standard dosing with monitoring"
    
    return {
        "hepatic_risk": risk,
        "risk_score": risk_score,
        "factors": factors,
        "dose_adjustments": categories,
        "recommendation": recommendation,
        "monitoring": ["LFTs at baseline", "LFTs weekly", "Monitor for jaundice"] if risk_score > 20 else ["Routine LFTs"]
    }


def predict_kidney_impairment_risk(smiles: str) -> Dict:
    """
    Predict risk in kidney impairment.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Kidney impairment risk assessment
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    tpsa = Descriptors.TPSA(mol)
    
    risk_score = 0
    factors = []
    
    if mw < 300:
        risk_score += 20
        factors.append("Low MW - likely renal clearance")
    
    if tpsa < 90:
        risk_score += 15
        factors.append("Low TPSA - potential renal tubular reabsorption")
    
    if logp < 0:
        risk_score += 10
        factors.append("High hydrophilicity - primarily renal excretion")
    
    if mw > 500:
        risk_score += 5
        factors.append("High MW - less renal dependent")
    
    categories = {
        "mild": {"factor": 0.8, "adjustment": "20% dose reduction"},
        "moderate": {"factor": 0.5, "adjustment": "50% dose reduction"},
        "severe": {"factor": 0.2, "adjustment": "80% dose reduction, monitor closely"},
    }
    
    if risk_score >= 30:
        risk = "High"
        recommendation = "Major dose adjustment needed in renal impairment"
    elif risk_score >= 15:
        risk = "Medium"
        recommendation = "Moderate dose adjustment in renal impairment"
    else:
        risk = "Low"
        recommendation = "Standard dosing with monitoring"
    
    return {
        "renal_risk": risk,
        "risk_score": risk_score,
        "factors": factors,
        "dose_adjustments": categories,
        "recommendation": recommendation,
        "monitoring": ["Renal function at baseline", "CrCl monitoring", "BUN/Creatinine weekly"] if risk_score > 15 else ["Routine renal function"]
    }


def get_age_based_recommendations(smiles: str, age: int) -> Dict:
    """
    Get age-based dosing recommendations.
    
    Args:
        smiles: SMILES string
        age: Patient age
        
    Returns:
        Age-based recommendations
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    
    if age < 2:
        group = "Neonate/Infant"
        factor = 0.3
        note = "Very limited data - extreme caution"
    elif age < 12:
        group = "Pediatric"
        factor = 0.5
        note = "Weight-based dosing recommended"
    elif age < 18:
        group = "Adolescent"
        factor = 0.8
        note = "May approach adult dosing"
    elif age < 65:
        group = "Adult"
        factor = 1.0
        note = "Standard adult dosing"
    elif age < 75:
        group = "Elderly"
        factor = 0.7
        note = "Start low, go slow"
    else:
        group = "Geriatric"
        factor = 0.5
        note = "Significant dose reduction - monitor closely"
    
    # Additional adjustments
    if age > 65 and logp > 4:
        factor *= 0.8
        note += " - Lipophilic drugs accumulate in elderly"
    
    return {
        "age_group": group,
        "dose_factor": round(factor, 2),
        "recommended_percent": round(factor * 100),
        "note": note,
        "monitoring": "Enhanced monitoring" if age < 12 or age > 65 else "Standard monitoring"
    }
