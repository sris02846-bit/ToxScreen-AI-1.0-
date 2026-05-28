"""
Genetic Factors Module
Polymorphism prediction, ethnicity-based variations, personalized toxicity.
"""

import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors
from typing import Dict, List, Optional
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


# CYP450 polymorphism data by ethnicity
CYP_POLYMORPHISM_DATA = {
    "CYP2D6": {
        "Caucasian": {"poor_metabolizer": 0.07, "intermediate": 0.12, "extensive": 0.71, "ultrarapid": 0.10},
        "Asian": {"poor_metabolizer": 0.01, "intermediate": 0.20, "extensive": 0.60, "ultrarapid": 0.19},
        "African": {"poor_metabolizer": 0.02, "intermediate": 0.15, "extensive": 0.55, "ultrarapid": 0.28},
        "Hispanic": {"poor_metabolizer": 0.04, "intermediate": 0.14, "extensive": 0.68, "ultrarapid": 0.14},
    },
    "CYP2C9": {
        "Caucasian": {"poor_metabolizer": 0.03, "intermediate": 0.14, "extensive": 0.83},
        "Asian": {"poor_metabolizer": 0.01, "intermediate": 0.08, "extensive": 0.91},
        "African": {"poor_metabolizer": 0.01, "intermediate": 0.12, "extensive": 0.87},
        "Hispanic": {"poor_metabolizer": 0.02, "intermediate": 0.11, "extensive": 0.87},
    },
    "CYP2C19": {
        "Caucasian": {"poor_metabolizer": 0.03, "intermediate": 0.25, "extensive": 0.42, "ultrarapid": 0.30},
        "Asian": {"poor_metabolizer": 0.15, "intermediate": 0.45, "extensive": 0.35, "ultrarapid": 0.05},
        "African": {"poor_metabolizer": 0.04, "intermediate": 0.30, "extensive": 0.40, "ultrarapid": 0.26},
        "Hispanic": {"poor_metabolizer": 0.04, "intermediate": 0.22, "extensive": 0.50, "ultrarapid": 0.24},
    },
}


def predict_polymorphism_risk(smiles: str, ethnicity: str = "Caucasian") -> Dict:
    """
    Predict pharmacogenetic risk based on CYP polymorphism.
    
    Args:
        smiles: SMILES string
        ethnicity: Patient ethnicity
        
    Returns:
        Polymorphism risk assessment
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    
    # Check which CYP enzymes likely metabolize this compound
    cyp_risks = {}
    
    for cyp, ethnic_data in CYP_POLYMORPHISM_DATA.items():
        if ethnicity in ethnic_data:
            probs = ethnic_data[ethnicity]
            
            # Simplified prediction based on molecular properties
            if logp > 4 and mw > 400:
                risk = "High"
            elif logp > 2:
                risk = "Medium"
            else:
                risk = "Low"
            
            cyp_risks[cyp] = {
                "risk_level": risk,
                "ethnicity": ethnicity,
                "polymorphism_distribution": probs,
                "recommendation": "Genetic testing recommended" if risk == "High" else "Standard dosing"
            }
    
    overall_risk = "High" if any(r["risk_level"] == "High" for r in cyp_risks.values()) else \
                   "Medium" if any(r["risk_level"] == "Medium" for r in cyp_risks.values()) else "Low"
    
    return {
        "smiles": smiles,
        "ethnicity": ethnicity,
        "overall_genetic_risk": overall_risk,
        "cyp_risks": cyp_risks,
        "pharmacogenetic_recommendation": (
            "Pharmacogenetic testing strongly recommended before administration"
            if overall_risk == "High" else
            "Consider genetic testing for optimal dosing"
            if overall_risk == "Medium" else
            "Standard dosing likely appropriate"
        )
    }


def get_personalized_dosing(smiles: str, ethnicity: str, age: int, 
                             weight_kg: float, liver_function: str = "normal",
                             kidney_function: str = "normal") -> Dict:
    """
    Calculate personalized dosing recommendations.
    
    Args:
        smiles: SMILES string
        ethnicity: Patient ethnicity
        age: Patient age
        weight_kg: Patient weight in kg
        liver_function: 'normal', 'mild', 'moderate', 'severe'
        kidney_function: 'normal', 'mild', 'moderate', 'severe'
        
    Returns:
        Personalized dosing recommendations
    """
    genetic = predict_polymorphism_risk(smiles, ethnicity)
    
    # Base adjustment factors
    adjustments = []
    dose_factor = 1.0
    
    # Age adjustment
    if age > 65:
        dose_factor *= 0.7
        adjustments.append("Elderly: 30% dose reduction")
    elif age < 12:
        dose_factor *= 0.5
        adjustments.append("Pediatric: 50% dose reduction")
    
    # Weight adjustment
    if weight_kg < 50:
        dose_factor *= 0.8
        adjustments.append("Low weight: 20% dose reduction")
    elif weight_kg > 100:
        dose_factor *= 0.9
        adjustments.append("High weight: 10% dose adjustment")
    
    # Liver impairment
    liver_factors = {"normal": 1.0, "mild": 0.75, "moderate": 0.5, "severe": 0.25}
    if liver_function in liver_factors:
        lf = liver_factors[liver_function]
        dose_factor *= lf
        if lf < 1.0:
            adjustments.append(f"Liver impairment ({liver_function}): {int((1-lf)*100)}% reduction")
    
    # Kidney impairment
    kidney_factors = {"normal": 1.0, "mild": 0.8, "moderate": 0.5, "severe": 0.2}
    if kidney_function in kidney_factors:
        kf = kidney_factors[kidney_function]
        dose_factor *= kf
        if kf < 1.0:
            adjustments.append(f"Kidney impairment ({kidney_function}): {int((1-kf)*100)}% reduction")
    
    # Genetic adjustment
    if genetic["overall_genetic_risk"] == "High":
        dose_factor *= 0.5
        adjustments.append("Genetic risk: 50% dose reduction")
    
    return {
        "smiles": smiles,
        "patient": {"ethnicity": ethnicity, "age": age, "weight": weight_kg},
        "dose_factor": round(dose_factor, 2),
        "recommended_percent": round(dose_factor * 100),
        "adjustments": adjustments,
        "genetic_risk": genetic["overall_genetic_risk"],
        "monitoring": "Close monitoring required" if dose_factor < 0.5 else 
                      "Standard monitoring" if dose_factor > 0.8 else
                      "Enhanced monitoring recommended"
    }
