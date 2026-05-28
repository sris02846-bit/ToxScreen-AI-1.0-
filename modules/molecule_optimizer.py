"""
Molecule Optimization Module
Suggests structural modifications to reduce toxicity.
"""

from rdkit import Chem
from rdkit.Chem import Descriptors
from typing import Dict, List
import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))

from toxicophores import detect_toxicophores
from lipinski_rules import evaluate_lipinski


def identify_toxic_substructures(smiles: str) -> List[Dict]:
    """Identify toxic substructures."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []
    return detect_toxicophores(mol)


def suggest_modifications(smiles: str) -> List[Dict]:
    """Suggest modifications to reduce toxicity."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return [{"error": "Invalid SMILES"}]
    
    toxic = identify_toxic_substructures(smiles)
    suggestions = []
    
    for t in toxic:
        if t["Risk Level"] == "High":
            suggestions.append({
                "toxicophore": t["Toxicophore"],
                "risk": t["Risk Level"],
                "suggestion": f"Replace or modify {t['Toxicophore']} group",
                "impact": "High"
            })
    
    lipinski = evaluate_lipinski(mol)
    if lipinski['violations'] > 0:
        suggestions.append({
            "toxicophore": "Drug-likeness",
            "risk": "Medium",
            "suggestion": f"Fix {lipinski['violations']} Lipinski violations",
            "impact": "Medium"
        })
    
    return suggestions


def get_optimization_score(smiles: str) -> Dict:
    """Calculate optimization potential."""
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"error": "Invalid SMILES"}
    
    toxic = identify_toxic_substructures(smiles)
    lipinski = evaluate_lipinski(mol)
    
    potential = 0
    for t in toxic:
        potential += 30 if t["Risk Level"] == "High" else 15 if t["Risk Level"] == "Medium" else 5
    potential += lipinski['violations'] * 20
    potential = min(100, potential)
    
    return {
        "optimization_potential": potential,
        "toxic_substructures": len(toxic),
        "lipinski_violations": lipinski['violations'],
        "suggestions": suggest_modifications(smiles)
    }


def generate_modified_molecules(smiles: str) -> List[Dict]:
    """Generate modified molecules."""
    suggestions = suggest_modifications(smiles)
    return [{"original": smiles, "modification": s["suggestion"], "impact": s["impact"]} for s in suggestions]
