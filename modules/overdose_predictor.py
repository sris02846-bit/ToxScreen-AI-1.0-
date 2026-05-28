"""
Overdose Effect & Advanced Toxicity Prediction Module
Predicts overdose effects and organ-specific toxicity severity.
"""

import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors
import os
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))

OVERDOSE_EFFECTS = {
    "Liver": {
        "mild": ["Elevated liver enzymes", "Mild hepatomegaly"],
        "moderate": ["Jaundice", "Hepatitis", "Fatty liver"],
        "severe": ["Acute liver failure", "Hepatic necrosis"],
        "antidotes": ["N-acetylcysteine", "Silymarin"]
    },
    "Heart": {
        "mild": ["Tachycardia", "Palpitations"],
        "moderate": ["Arrhythmia", "QT prolongation"],
        "severe": ["Cardiac arrest", "Ventricular fibrillation"],
        "antidotes": ["Beta-blockers", "Calcium channel blockers"]
    },
    "Kidney": {
        "mild": ["Mild proteinuria", "Increased creatinine"],
        "moderate": ["Acute kidney injury", "Tubular necrosis"],
        "severe": ["Renal failure", "Dialysis required"],
        "antidotes": ["Hemodialysis", "Fluid resuscitation"]
    },
    "Brain": {
        "mild": ["Dizziness", "Headache", "Confusion"],
        "moderate": ["Seizures", "Hallucinations", "Ataxia"],
        "severe": ["Coma", "Respiratory depression"],
        "antidotes": ["Naloxone", "Flumazenil"]
    },
    "Lungs": {
        "mild": ["Cough", "Shortness of breath"],
        "moderate": ["Pneumonitis", "Pulmonary edema"],
        "severe": ["Respiratory failure", "ARDS"],
        "antidotes": ["Oxygen therapy", "Mechanical ventilation"]
    },
}


def predict_overdose_risk(smiles: str, therapeutic_index: float = None) -> dict:
    """Predict overdose risk and organ-specific effects."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    
    mw = Descriptors.MolWt(mol)
    logp = Descriptors.MolLogP(mol)
    
    risk_factors = []
    if mw > 500:
        risk_factors.append("High molecular weight - accumulation risk")
    if logp > 5:
        risk_factors.append("High lipophilicity - tissue accumulation")
    if logp < 0:
        risk_factors.append("Very hydrophilic - rapid clearance")
    
    organ_risks = {}
    for organ, effects in OVERDOSE_EFFECTS.items():
        if organ == "Liver":
            risk = "High" if logp > 4 else "Medium" if logp > 2 else "Low"
        elif organ == "Heart":
            risk = "High" if mw > 400 else "Medium" if mw > 300 else "Low"
        elif organ == "Kidney":
            risk = "High" if mw < 200 else "Medium" if mw < 400 else "Low"
        elif organ == "Brain":
            risk = "High" if logp > 3 else "Medium" if logp > 1 else "Low"
        else:
            risk = "Low"
        
        organ_risks[organ] = {
            "risk_level": risk,
            "mild_effects": effects["mild"],
            "moderate_effects": effects["moderate"],
            "severe_effects": effects["severe"],
            "antidotes": effects["antidotes"]
        }
    
    high_organs = sum(1 for o in organ_risks.values() if o["risk_level"] == "High")
    overall_risk = "Critical" if high_organs >= 3 else "High" if high_organs >= 1 else "Moderate"
    
    return {
        "smiles": smiles,
        "overall_overdose_risk": overall_risk,
        "risk_factors": risk_factors,
        "organ_risks": organ_risks,
        "recommendation": "Careful dose titration recommended" if overall_risk in ["Critical", "High"] else "Standard dosing"
    }


def calculate_enhanced_therapeutic_window(smiles: str) -> dict:
    """Calculate enhanced therapeutic window."""
    from therapeutic_index_model import predict_therapeutic_index
    
    ti_result = predict_therapeutic_index(smiles)
    ti = ti_result.get("therapeutic_index", 10)
    
    if ti >= 100:
        safety_ratio = ">100:1"
        flexibility = "High"
    elif ti >= 10:
        safety_ratio = f"{ti}:1"
        flexibility = "Moderate"
    elif ti >= 3:
        safety_ratio = f"{ti}:1"
        flexibility = "Low"
    else:
        safety_ratio = f"{ti}:1"
        flexibility = "Critical"
    
    overdose = predict_overdose_risk(smiles, ti)
    
    return {
        "therapeutic_index": ti,
        "safety_ratio": safety_ratio,
        "dosing_flexibility": flexibility,
        "overdose_risk": overdose["overall_overdose_risk"],
        "organ_risks": overdose["organ_risks"],
        "monitoring_required": ti < 10
    }
