"""
Molecular Parser Module
Handles SMILES parsing and basic molecular property calculations.
"""

import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors
from typing import Dict, Tuple, Optional
import sys


def parse_smiles(smiles: str) -> Tuple[Optional[Chem.Mol], Optional[str]]:
    """
    Parse SMILES string and return RDKit molecule object.
    
    Args:
        smiles: SMILES notation string
        
    Returns:
        Tuple of (RDKit Mol object or None, error message or None)
    """
    if not smiles or not smiles.strip():
        return None, "Please enter a valid SMILES string."
    
    try:
        mol = Chem.MolFromSmiles(smiles.strip())
        if mol is None:
            return None, "Invalid SMILES string. Check syntax and try again."
        return mol, None
    except Exception as e:
        return None, f"Error parsing SMILES: {str(e)}"


def calculate_basic_properties(mol: Chem.Mol) -> Dict:
    """
    Calculate fundamental molecular properties.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Dictionary containing molecular properties
    """
    properties = {
        "Molecular Formula": rdMolDescriptors.CalcMolFormula(mol),
        "Molecular Weight (g/mol)": round(Descriptors.MolWt(mol), 2),
        "Heavy Atom Count": mol.GetNumHeavyAtoms(),
        "Total Atom Count": mol.GetNumAtoms(),
        "Ring Count": rdMolDescriptors.CalcNumRings(mol),
        "Rotatable Bonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
    }
    return properties


def calculate_molecular_weight(mol: Chem.Mol) -> float:
    """
    Calculate exact molecular weight.
    
    Args:
        mol: RDKit molecule object
        
    Returns:
        Molecular weight in g/mol
    """
    return Descriptors.MolWt(mol)
