"""
Toxicophore Detection Module
Identifies toxic structural alerts using SMARTS patterns.
"""

import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from typing import Dict, List, Tuple
import json
import os


def load_toxicophore_patterns() -> List[Dict]:
    """
    Load toxicophore SMARTS patterns from JSON database.
    
    Returns:
        List of toxicophore pattern dictionaries
    """
    # Get the path to the patterns file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    patterns_file = os.path.join(current_dir, '..', 'data', 'toxicophore_patterns.json')
    
    try:
        with open(patterns_file, 'r') as f:
            data = json.load(f)
        return data.get('toxicophores', [])
    except FileNotFoundError:
        print(f"Warning: Toxicophore patterns file not found at {patterns_file}")
        return []
    except json.JSONDecodeError:
        print("Warning: Invalid JSON in toxicophore patterns file")
        return []


def detect_toxicophores(mol: Chem.Mol) -> List[Dict]:
    """
    Detect toxicophore patterns in a molecule.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        List of detected toxicophores with details
    """
    patterns = load_toxicophore_patterns()
    detected = []
    
    for pattern in patterns:
        try:
            # Create SMARTS pattern
            substructure = Chem.MolFromSmarts(pattern['smarts'])
            
            if substructure is None:
                continue
            
            # Find matches
            matches = mol.GetSubstructMatches(substructure)
            
            if matches:
                detected.append({
                    "Toxicophore": pattern['name'],
                    "Description": pattern['description'],
                    "Risk Level": pattern['risk_level'],
                    "Match Count": len(matches),
                    "SMARTS Pattern": pattern['smarts']
                })
        except Exception as e:
            print(f"Error processing pattern {pattern['name']}: {str(e)}")
            continue
    
    # Sort by risk level (High > Medium > Low)
    risk_order = {"High": 0, "Medium": 1, "Low": 2}
    detected.sort(key=lambda x: risk_order.get(x['Risk Level'], 3))
    
    return detected


def calculate_toxicity_score(detected_patterns: List[Dict]) -> Tuple[float, str]:
    """
    Calculate toxicity risk score based on detected patterns.
    
    Args:
        detected_patterns: List of detected toxicophore dictionaries
        
    Returns:
        Tuple of (risk_score, risk_level_string)
    """
    if not detected_patterns:
        return 0.0, "Low Risk"
    
    # Weight by risk level
    risk_weights = {"High": 25, "Medium": 15, "Low": 5}
    
    total_score = 0
    for pattern in detected_patterns:
        weight = risk_weights.get(pattern['Risk Level'], 10)
        total_score += weight * pattern['Match Count']
    
    # Cap at 100
    total_score = min(total_score, 100)
    
    # Determine risk level
    if total_score >= 50:
        risk_level = "High Risk"
    elif total_score >= 20:
        risk_level = "Moderate Risk"
    else:
        risk_level = "Low Risk"
    
    return total_score, risk_level


def evaluate_toxicophores(mol: Chem.Mol) -> Dict:
    """
    Complete toxicophore evaluation for a molecule.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Dictionary with full evaluation results
    """
    detected = detect_toxicophores(mol)
    score, risk_level = calculate_toxicity_score(detected)
    
    return {
        "detected": detected,
        "toxicity_score": score,
        "risk_level": risk_level,
        "total_alerts": len(detected)
    }
