"""
Batch Processor v2 - Parallel Processing
Optimized for large compound libraries.
"""

import pandas as pd
import numpy as np
from rdkit import Chem
from typing import Dict, List, Tuple
import io
import sys
import os
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, os.path.dirname(__file__))

from molecular_parser import parse_smiles, calculate_basic_properties
from lipinski_rules import evaluate_lipinski
from veber_rules import evaluate_veber
from toxicophores import evaluate_toxicophores
from fingerprint import compare_toxin_similarity


def process_single_smiles_parallel(smiles: str, include_ml: bool = False) -> Dict:
    """Process a single SMILES with all analyses."""
    result = {'SMILES': smiles, 'Valid': False, 'Error': None}
    
    try:
        mol, error = parse_smiles(smiles)
        if error or mol is None:
            result['Error'] = error or 'Invalid SMILES'
            return result
        
        basic = calculate_basic_properties(mol)
        lipinski = evaluate_lipinski(mol)
        veber = evaluate_veber(mol)
        tox = evaluate_toxicophores(mol)
        similarity = compare_toxin_similarity(smiles)
        
        score = 100 - (lipinski['violations'] * 15) - (veber['violations'] * 10) - (tox['toxicity_score'] * 0.5)
        score = max(0, min(100, score))
        
        result.update({
            'Valid': True,
            'Molecular_Weight': basic.get('Molecular Weight (g/mol)', 'N/A'),
            'Molecular_Formula': basic.get('Molecular Formula', 'N/A'),
            'Lipinski_Violations': lipinski['violations'],
            'Veber_Violations': veber['violations'],
            'Toxicity_Score': round(tox['toxicity_score'], 1),
            'Risk_Level': tox['risk_level'],
            'DrugLikeness_Score': round(score, 1),
            'Result': "Excellent" if score >= 80 else "Good" if score >= 60 else "Moderate" if score >= 40 else "Poor",
            'Most_Similar_Toxin': similarity.get('most_similar', 'None'),
            'Toxin_Similarity': similarity.get('similarity', 0),
            'Toxicophore_Count': tox['total_alerts']
        })
        
        if include_ml:
            try:
                from ml_model import predict_hepatotoxicity
                ml = predict_hepatotoxicity(smiles)
                result['ML_Prediction'] = ml.get('prediction', 'N/A')
                result['ML_Confidence'] = ml.get('confidence', 0)
            except:
                pass
        
        return result
    except Exception as e:
        result['Error'] = str(e)
        return result


def process_csv_parallel(csv_content: str, include_ml: bool = False, progress_callback=None) -> Tuple[pd.DataFrame, int, int]:
    """Process CSV file with parallel execution."""
    try:
        df = pd.read_csv(io.StringIO(csv_content))
    except Exception as e:
        raise ValueError(f"Error reading CSV: {str(e)}")
    
    smiles_col = None
    for col in df.columns:
        if 'smiles' in col.lower():
            smiles_col = col
            break
    if smiles_col is None:
        smiles_col = df.columns[0]
    
    smiles_list = df[smiles_col].astype(str).str.strip().tolist()
    results = []
    
    for i, smiles in enumerate(smiles_list):
        result = process_single_smiles_parallel(smiles, include_ml)
        results.append(result)
        if progress_callback:
            progress_callback(i + 1, len(smiles_list))
    
    results_df = pd.DataFrame(results)
    valid_count = results_df['Valid'].sum()
    invalid_count = len(results_df) - valid_count
    
    return results_df, valid_count, invalid_count


def generate_batch_summary_v2(results_df: pd.DataFrame) -> Dict:
    """Generate batch summary statistics."""
    valid_df = results_df[results_df['Valid'] == True]
    
    if len(valid_df) == 0:
        return {'total': len(results_df), 'valid': 0, 'invalid': len(results_df), 'avg_score': 0}
    
    return {
        'total': len(results_df),
        'valid': len(valid_df),
        'invalid': len(results_df) - len(valid_df),
        'avg_score': round(valid_df['DrugLikeness_Score'].mean(), 1),
        'excellent': len(valid_df[valid_df['Result'] == 'Excellent']),
        'good': len(valid_df[valid_df['Result'] == 'Good']),
        'moderate': len(valid_df[valid_df['Result'] == 'Moderate']),
        'poor': len(valid_df[valid_df['Result'] == 'Poor']),
    }
