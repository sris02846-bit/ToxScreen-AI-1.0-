"""
Lipinski's Rule of Five Module
Evaluates drug-likeness based on Lipinski's criteria.
"""

import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, Lipinski
from typing import Dict, List, Tuple


def calculate_lipinski_properties(mol: Chem.Mol) -> Dict:
    """
    Calculate all Lipinski Rule of Five properties.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Dictionary with property names and values
    """
    properties = {
        "Molecular Weight (MW)": round(Descriptors.MolWt(mol), 2),
        "LogP (Octanol-Water)": round(Crippen.MolLogP(mol), 2),
        "Hydrogen Bond Donors (HBD)": Lipinski.NumHDonors(mol),
        "Hydrogen Bond Acceptors (HBA)": Lipinski.NumHAcceptors(mol),
    }
    return properties


def check_lipinski_violations(properties: Dict) -> Tuple[List[Dict], int]:
    """
    Evaluate Lipinski violations and return detailed results.
    
    Lipinski Rule of Five:
    1. Molecular Weight ≤ 500 g/mol
    2. LogP ≤ 5
    3. H-Bond Donors ≤ 5
    4. H-Bond Acceptors ≤ 10
    
    Args:
        properties: Dictionary of calculated properties
        
    Returns:
        Tuple of (violations list, violation count)
    """
    rules = [
        {
            "Rule": "Molecular Weight ≤ 500",
            "Value": f"{properties['Molecular Weight (MW)']:.2f}",
            "Threshold": "≤ 500",
            "Status": "PASS" if properties["Molecular Weight (MW)"] <= 500 else "FAIL"
        },
        {
            "Rule": "LogP ≤ 5",
            "Value": f"{properties['LogP (Octanol-Water)']:.2f}",
            "Threshold": "≤ 5",
            "Status": "PASS" if properties["LogP (Octanol-Water)"] <= 5 else "FAIL"
        },
        {
            "Rule": "H-Bond Donors ≤ 5",
            "Value": str(properties["Hydrogen Bond Donors (HBD)"]),
            "Threshold": "≤ 5",
            "Status": "PASS" if properties["Hydrogen Bond Donors (HBD)"] <= 5 else "FAIL"
        },
        {
            "Rule": "H-Bond Acceptors ≤ 10",
            "Value": str(properties["Hydrogen Bond Acceptors (HBA)"]),
            "Threshold": "≤ 10",
            "Status": "PASS" if properties["Hydrogen Bond Acceptors (HBA)"] <= 10 else "FAIL"
        }
    ]
    
    violations = sum(1 for rule in rules if rule["Status"] == "FAIL")
    
    return rules, violations


def evaluate_lipinski(mol: Chem.Mol) -> Dict:
    """
    Complete Lipinski evaluation for a molecule.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Dictionary with full evaluation results
    """
    properties = calculate_lipinski_properties(mol)
    rules, violations = check_lipinski_violations(properties)
    
    return {
        "properties": properties,
        "rules": rules,
        "violations": violations,
        "pass": violations == 0
    }


except ImportError:
    print("RDKit not available - some features disabled")