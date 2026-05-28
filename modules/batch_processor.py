"""
Batch Processing Module
Handles CSV upload and bulk compound analysis.
"""

import pandas as pd
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from typing import Dict, List, Tuple
import io
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from molecular_parser import parse_smiles, calculate_basic_properties
from lipinski_rules import evaluate_lipinski
from veber_rules import evaluate_veber
from toxicophores import evaluate_toxicophores
from fingerprint import compare_toxin_similarity


def process_single_smiles(smiles: str) -> Dict:
    """Process a single SMILES and return all results."""
    mol, error = parse_smiles(smiles)
    
    if error:
        return {
            'SMILES': smiles,
            'Valid': False,
            'Error': error
        }
    
    basic = calculate_basic_properties(mol)
    lipinski = evaluate_lipinski(mol)
    veber = evaluate_veber(mol)
    toxicophores = evaluate_toxicophores(mol)
    similarity = compare_toxin_similarity(smiles)
    
    score = 100 - (lipinski['violations'] * 15) - (veber['violations'] * 10) - (toxicophores['toxicity_score'] * 0.5)
    score = max(0, min(100, score))
    
    if score >= 80:
        result = "Excellent"
    elif score >= 60:
        result = "Good"
    elif score >= 40:
        result = "Moderate"
    else:
        result = "Poor"
    
    return {
        'SMILES': smiles,
        'Valid': True,
        'Molecular_Weight': basic.get('Molecular Weight (g/mol)', 'N/A'),
        'Molecular_Formula': basic.get('Molecular Formula', 'N/A'),
        'Lipinski_Violations': lipinski['violations'],
        'Veber_Violations': veber['violations'],
        'Toxicity_Score': round(toxicophores['toxicity_score'], 1),
        'Risk_Level': toxicophores['risk_level'],
        'DrugLikeness_Score': round(score, 1),
        'Result': result,
        'Most_Similar_Toxin': similarity.get('most_similar', 'None'),
        'Toxin_Similarity': similarity.get('similarity', 0),
        'Toxicophore_Count': toxicophores['total_alerts']
    }


def process_csv_file(csv_content: str) -> Tuple[pd.DataFrame, int, int]:
    """
    Process a CSV file containing SMILES strings.
    
    Args:
        csv_content: String content of CSV file
        
    Returns:
        Tuple of (results DataFrame, valid_count, invalid_count)
    """
    try:
        df = pd.read_csv(io.StringIO(csv_content))
    except Exception as e:
        raise ValueError(f"Error reading CSV: {str(e)}")
    
    # Find SMILES column
    smiles_col = None
    for col in df.columns:
        if 'smiles' in col.lower():
            smiles_col = col
            break
    
    if smiles_col is None:
        smiles_col = df.columns[0]
    
    results = []
    valid_count = 0
    invalid_count = 0
    
    for _, row in df.iterrows():
        smiles = str(row[smiles_col]).strip()
        result = process_single_smiles(smiles)
        
        if result['Valid']:
            valid_count += 1
        else:
            invalid_count += 1
        
        # Add any additional columns from original CSV
        for col in df.columns:
            if col != smiles_col:
                result[f'Original_{col}'] = row[col]
        
        results.append(result)
    
    results_df = pd.DataFrame(results)
    return results_df, valid_count, invalid_count


def generate_batch_summary(results_df: pd.DataFrame) -> Dict:
    """Generate summary statistics for batch processing."""
    valid_df = results_df[results_df['Valid'] == True]
    
    if len(valid_df) == 0:
        return {
            'total': len(results_df),
            'valid': 0,
            'invalid': len(results_df),
            'avg_score': 0,
            'excellent': 0,
            'good': 0,
            'moderate': 0,
            'poor': 0
        }
    
    return {
        'total': len(results_df),
        'valid': len(valid_df),
        'invalid': len(results_df) - len(valid_df),
        'avg_score': round(valid_df['DrugLikeness_Score'].mean(), 1),
        'excellent': len(valid_df[valid_df['Result'] == 'Excellent']),
        'good': len(valid_df[valid_df['Result'] == 'Good']),
        'moderate': len(valid_df[valid_df['Result'] == 'Moderate']),
        'poor': len(valid_df[valid_df['Result'] == 'Poor'])
    }
