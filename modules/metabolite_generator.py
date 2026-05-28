"""
RDKit Rule-Based Metabolite Generator
Applies common metabolic transformations and screens for reactive metabolites.
Flags "Metabolic Activation Risk" if reactive metabolites detected.
"""

import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, Descriptors
    from rdkit.Chem import rdMolDescriptors
import os
import sys
from typing import List, Dict, Tuple

sys.path.insert(0, os.path.dirname(__file__))


# Common metabolic transformation rules
METABOLIC_RULES = [
    {
        "name": "Aromatic Hydroxylation",
        "smarts": "[c:1]1[cH][cH][cH][cH][cH]1>>[c:1]1[cH][cH][cH][cH][c:1](O)1",
        "description": "CYP450-mediated aromatic hydroxylation"
    },
    {
        "name": "N-Dealkylation",
        "smarts": "[N:1]([C:2])[C:3]>>[N:1][C:3]",
        "description": "Removal of alkyl group from nitrogen"
    },
    {
        "name": "O-Dealkylation",
        "smarts": "[O:1][C:2]>>[O:1]",
        "description": "Removal of alkyl group from oxygen"
    },
    {
        "name": "Alcohol Oxidation",
        "smarts": "[C:1][OH:2]>>[C:1]=O",
        "description": "Oxidation of alcohol to carbonyl"
    },
    {
        "name": "Epoxidation",
        "smarts": "[C:1]=[C:2]>>[C:1]1O[C:2]1",
        "description": "Formation of epoxide from alkene"
    },
    {
        "name": "Glucuronidation",
        "smarts": "[OH:1]>>[O:1]C1OC(CO)C(O)C(O)C1O",
        "description": "Phase II glucuronide conjugation"
    },
]


# Reactive metabolite structural alerts (toxicophores)
REACTIVE_METABOLITE_ALERTS = [
    {"name": "Epoxide", "smarts": "C1OC1", "risk": "High - DNA alkylation"},
    {"name": "Quinone", "smarts": "O=C1C=CC(=O)C=C1", "risk": "High - Redox cycling"},
    {"name": "Quinone Imine", "smarts": "O=C1C=CC(=N)C=C1", "risk": "High - Protein adducts"},
    {"name": "Michael Acceptor", "smarts": "C=CC(=O)", "risk": "High - GSH depletion"},
    {"name": "Acyl Glucuronide", "smarts": "C(=O)OC1OC(CO)C(O)C(O)C1O", "risk": "Medium - Protein binding"},
    {"name": "N-Hydroxylamine", "smarts": "N(O)", "risk": "High - Methemoglobinemia"},
    {"name": "Aldehyde", "smarts": "[CH]=O", "risk": "Medium - Protein crosslinking"},
    {"name": "Nitroso", "smarts": "N=O", "risk": "High - Carcinogenicity"},
    {"name": "Imine", "smarts": "C=N", "risk": "Medium - Schiff base formation"},
    {"name": "Isocyanate", "smarts": "N=C=O", "risk": "High - Respiratory sensitizer"},
]


def generate_metabolites(smiles: str) -> List[Dict]:
    """
    Generate potential metabolites using rule-based transformations.
    
    Args:
        smiles: Parent compound SMILES
        
    Returns:
        List of metabolite dictionaries with SMILES and transformation info
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return []
    
    metabolites = []
    
    for rule in METABOLIC_RULES:
        try:
            rxn = AllChem.ReactionFromSmarts(rule["smarts"])
            products = rxn.RunReactants((mol,))
            
            for product_set in products:
                for product in product_set:
                    try:
                        Chem.SanitizeMol(product)
                        product_smiles = Chem.MolToSmiles(product)
                        
                        if product_smiles != smiles:
                            metabolites.append({
                                "transformation": rule["name"],
                                "description": rule["description"],
                                "smiles": product_smiles,
                                "parent_smiles": smiles
                            })
                    except:
                        pass
        except:
            pass
    
    # Remove duplicates
    seen = set()
    unique_metabolites = []
    for m in metabolites:
        if m["smiles"] not in seen:
            seen.add(m["smiles"])
            unique_metabolites.append(m)
    
    return unique_metabolites[:20]  # Limit to top 20


def screen_metabolites_for_toxicity(metabolites: List[Dict]) -> List[Dict]:
    """
    Screen generated metabolites for reactive structural alerts.
    
    Args:
        metabolites: List of metabolite dictionaries
        
    Returns:
        List of metabolites with toxicity flags
    """
    flagged = []
    
    for metabolite in metabolites:
        mol = Chem.MolFromSmiles(metabolite["smiles"])
        if mol is None:
            continue
        
        alerts = []
        for alert in REACTIVE_METABOLITE_ALERTS:
            pattern = Chem.MolFromSmarts(alert["smarts"])
            if pattern and mol.HasSubstructMatch(pattern):
                alerts.append({
                    "alert": alert["name"],
                    "risk": alert["risk"]
                })
        
        if alerts:
            metabolite["reactive_alerts"] = alerts
            metabolite["is_reactive"] = True
            flagged.append(metabolite)
    
    return flagged


def assess_metabolic_activation_risk(smiles: str) -> Dict:
    """
    Full metabolic activation risk assessment.
    
    Args:
        smiles: Parent compound SMILES
        
    Returns:
        Risk assessment dictionary
    """
    result = {
        "smiles": smiles,
        "metabolites_generated": 0,
        "reactive_metabolites": 0,
        "metabolic_activation_risk": "Low",
        "reactive_species": [],
        "warning": ""
    }
    
    # Generate metabolites
    metabolites = generate_metabolites(smiles)
    result["metabolites_generated"] = len(metabolites)
    
    # Screen for reactive metabolites
    reactive = screen_metabolites_for_toxicity(metabolites)
    result["reactive_metabolites"] = len(reactive)
    
    # Collect reactive species
    for r in reactive:
        for alert in r.get("reactive_alerts", []):
            result["reactive_species"].append({
                "transformation": r["transformation"],
                "metabolite_smiles": r["smiles"][:50],
                "alert": alert["alert"],
                "risk": alert["risk"]
            })
    
    # Determine risk level
    if result["reactive_metabolites"] >= 3:
        result["metabolic_activation_risk"] = "High"
        result["warning"] = "CRITICAL: Multiple reactive metabolites detected. High risk of metabolic activation and toxicity."
    elif result["reactive_metabolites"] >= 1:
        result["metabolic_activation_risk"] = "Medium"
        result["warning"] = "WARNING: Reactive metabolite(s) detected. Potential metabolic activation risk."
    else:
        result["metabolic_activation_risk"] = "Low"
        result["warning"] = "No reactive metabolites detected. Low metabolic activation risk."
    
    return result


except ImportError:
    print("RDKit not available - some features disabled")