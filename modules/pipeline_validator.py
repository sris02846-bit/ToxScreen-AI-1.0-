"""
Pipeline Validation Module
Runs full pipeline on 5000 compounds, measures metrics, logs errors.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple
import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

def generate_test_compounds(n: int = 5000) -> pd.DataFrame:
    """
    Generate test compound dataset for pipeline validation.
    
    Args:
        n: Number of compounds
        
    Returns:
        DataFrame with SMILES
    """
    known_smiles = [
        "CC(=O)OC1=CC=CC=C1C(=O)O",  # Aspirin
        "CC(=O)NC1=CC=C(O)C=C1",      # Paracetamol
        "CC(C)CC1=CC=C(C=C1)C(C)C(=O)O",  # Ibuprofen
        "CN1C=NC2=C1C(=O)N(C(=O)N2C)C",   # Caffeine
        "CCO",                              # Ethanol
        "c1ccccc1",                         # Benzene
        "CN1CCC23C4C1CC5=C2C(=C(C=C5)O)OC3C(C=C4)O",  # Morphine
        "CN1C(=O)CN=C(C2=CC=CC=C2)C3=CC=CC=C3C1=O",    # Diazepam
        "CCN(CC)CC(=O)Nc1c(C)cccc1C",      # Lidocaine
        "CC(C)NCC(O)COc1cccc2ccccc12",     # Propranolol
        "C(C(=O)O)N",                       # Glycine
        "CC(=O)O",                          # Acetic acid
        "C1CCCCC1",                         # Cyclohexane
        "CC(=O)C",                          # Acetone
        "ClC(Cl)(Cl)Cl",                    # Carbon tetrachloride
    ]
    
    # Repeat to reach n compounds
    compounds = []
    for i in range(n):
        compounds.append({
            "id": i + 1,
            "smiles": known_smiles[i % len(known_smiles)]
        })
    
    return pd.DataFrame(compounds)

def validate_smiles(smiles: str) -> Tuple[bool, str]:
    """
    Validate SMILES string with robust error handling.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    from rdkit import Chem
    
    if not smiles or not isinstance(smiles, str):
        return False, "Empty or invalid input"
    
    smiles = smiles.strip()
    
    if len(smiles) == 0:
        return False, "Empty SMILES"
    
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return False, "RDKit could not parse SMILES"
        
        # Try to compute basic properties
        from rdkit.Chem import Descriptors
        mw = Descriptors.MolWt(mol)
        
        if mw <= 0 or mw > 10000:
            return False, f"Unreasonable molecular weight: {mw}"
        
        return True, ""
    except Exception as e:
        return False, f"Validation error: {str(e)}"

def run_pipeline_validation(n_compounds: int = 100) -> Dict:
    """
    Run full pipeline validation.
    
    Args:
        n_compounds: Number of compounds to test
        
    Returns:
        Validation results dictionary
    """
    from molecular_parser import parse_smiles
    from lipinski_rules import evaluate_lipinski
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_compounds": n_compounds,
        "valid_smiles": 0,
        "invalid_smiles": 0,
        "errors": [],
        "timing": {},
        "metrics": {}
    }
    
    test_df = generate_test_compounds(n_compounds)
    
    # Validate all SMILES
    start_time = time.time()
    for _, row in test_df.iterrows():
        smiles = row['smiles']
        is_valid, error = validate_smiles(smiles)
        
        if is_valid:
            results["valid_smiles"] += 1
        else:
            results["invalid_smiles"] += 1
            results["errors"].append({"smiles": smiles, "error": error})
    
    results["timing"]["validation"] = round(time.time() - start_time, 2)
    
    # Test molecular parsing
    start_time = time.time()
    parse_count = 0
    for _, row in test_df.head(100).iterrows():
        mol, err = parse_smiles(row['smiles'])
        if mol:
            parse_count += 1
    
    results["timing"]["parsing_100"] = round(time.time() - start_time, 2)
    results["metrics"]["parse_success_rate"] = parse_count / min(100, n_compounds)
    
    # Test Lipinski evaluation
    start_time = time.time()
    lipinski_count = 0
    for _, row in test_df.head(100).iterrows():
        mol, _ = parse_smiles(row['smiles'])
        if mol:
            evaluate_lipinski(mol)
            lipinski_count += 1
    
    results["timing"]["lipinski_100"] = round(time.time() - start_time, 2)
    
    results["metrics"]["valid_rate"] = results["valid_smiles"] / n_compounds if n_compounds > 0 else 0
    results["metrics"]["avg_parse_time"] = results["timing"]["parsing_100"] / 100 if parse_count > 0 else 0
    
    return results

def generate_test_summary(results: Dict) -> str:
    """
    Generate test summary report.
    
    Args:
        results: Pipeline validation results
        
    Returns:
        Formatted summary string
    """
    lines = []
    lines.append("=" * 60)
    lines.append("TOXSCREEN-AI PIPELINE VALIDATION REPORT")
    lines.append("=" * 60)
    lines.append(f"Timestamp: {results['timestamp']}")
    lines.append(f"Compounds Tested: {results['total_compounds']}")
    lines.append("")
    lines.append("-" * 40)
    lines.append("SMILES VALIDATION")
    lines.append("-" * 40)
    lines.append(f"Valid: {results['valid_smiles']}")
    lines.append(f"Invalid: {results['invalid_smiles']}")
    lines.append(f"Valid Rate: {results['metrics'].get('valid_rate', 0):.1%}")
    lines.append("")
    lines.append("-" * 40)
    lines.append("PERFORMANCE TIMING")
    lines.append("-" * 40)
    for key, val in results.get('timing', {}).items():
        lines.append(f"  {key}: {val}s")
    lines.append("")
    lines.append("-" * 40)
    lines.append("ERRORS")
    lines.append("-" * 40)
    for err in results.get('errors', [])[:10]:
        lines.append(f"  {err['smiles'][:30]}: {err['error']}")
    if len(results.get('errors', [])) > 10:
        lines.append(f"  ... and {len(results['errors']) - 10} more errors")
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)

def save_validation_report(results: Dict):
    """Save validation report to file."""
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    report_path = os.path.join(base_dir, 'test_summary_report.txt')
    
    report = generate_test_summary(results)
    with open(report_path, 'w') as f:
        f.write(report)
    
    return report_path
