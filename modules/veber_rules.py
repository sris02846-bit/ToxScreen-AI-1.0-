"""
Veber Rules Module
Evaluates oral bioavailability based on Veber's criteria.
"""

import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors
from typing import Dict, List, Tuple


def calculate_veber_properties(mol: Chem.Mol) -> Dict:
    """
    Calculate Veber rule properties.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Dictionary with property names and values
    """
    properties = {
        "Rotatable Bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
        "TPSA": round(rdMolDescriptors.CalcTPSA(mol), 2),
    }
    return properties


def check_veber_violations(properties: Dict) -> Tuple[List[Dict], int]:
    """
    Evaluate Veber violations.
    
    Veber Rules for oral bioavailability:
    1. Rotatable Bonds <= 10
    2. Topological Polar Surface Area (TPSA) <= 140 square Angstrom
    
    Args:
        properties: Dictionary of calculated properties
        
    Returns:
        Tuple of (violations list, violation count)
    """
    rules = [
        {
            "Rule": "Rotatable Bonds <= 10",
            "Value": str(properties["Rotatable Bonds"]),
            "Threshold": "<= 10",
            "Status": "PASS" if properties["Rotatable Bonds"] <= 10 else "FAIL"
        },
        {
            "Rule": "TPSA <= 140 square Angstrom",
            "Value": f"{properties['TPSA']:.2f}",
            "Threshold": "<= 140",
            "Status": "PASS" if properties["TPSA"] <= 140 else "FAIL"
        }
    ]
    
    violations = sum(1 for rule in rules if rule["Status"] == "FAIL")
    
    return rules, violations


def evaluate_veber(mol: Chem.Mol) -> Dict:
    """
    Complete Veber evaluation for a molecule.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Dictionary with full evaluation results
    """
    properties = calculate_veber_properties(mol)
    rules, violations = check_veber_violations(properties)
    
    return {
        "properties": properties,
        "rules": rules,
        "violations": violations,
        "pass": violations == 0
    }


except ImportError:
    print("RDKit not available - some features disabled")