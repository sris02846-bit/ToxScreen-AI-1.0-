"""
Morgan Fingerprint Module
Generates molecular fingerprints and calculates Tanimoto similarity.
"""

import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import Chem
    from rdkit.Chem import AllChem, DataStructs
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
try:
    from rdkit import DataStructs as DS
import pandas as pd
import os
from typing import List, Dict, Tuple, Optional


def generate_morgan_fingerprint(smiles: str, radius: int = 2, nbits: int = 2048) -> Optional[DataStructs.ExplicitBitVect]:
    """
    Generate Morgan (ECFP) fingerprint for a molecule.
    
    Args:
        smiles: SMILES string
        radius: Morgan fingerprint radius (default 2 for ECFP4)
        nbits: Number of bits in fingerprint
        
    Returns:
        RDKit ExplicitBitVect fingerprint or None if invalid SMILES
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    fp = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)
    return fp


def calculate_tanimoto_similarity(fp1: DataStructs.ExplicitBitVect, 
                                   fp2: DataStructs.ExplicitBitVect) -> float:
    """
    Calculate Tanimoto similarity between two fingerprints.
    
    Args:
        fp1: First fingerprint
        fp2: Second fingerprint
        
    Returns:
        Tanimoto similarity score (0-1)
    """
    return DataStructs.TanimotoSimilarity(fp1, fp2)


def load_toxin_database(csv_path: str = None) -> pd.DataFrame:
    """
    Load known toxins database from CSV.
    
    Args:
        csv_path: Path to known_toxins.csv
        
    Returns:
        DataFrame with toxin information
    """
    if csv_path is None:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'known_toxins.csv')
    
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError:
        print(f"Warning: Toxin database not found at {csv_path}")
        return pd.DataFrame(columns=['name', 'smiles', 'category', 'toxicity_level'])


def find_most_similar_toxin(query_smiles: str, 
                             toxin_db: pd.DataFrame = None) -> Dict:
    """
    Find the most similar known toxin to a query molecule.
    
    Args:
        query_smiles: SMILES string of query molecule
        toxin_db: DataFrame of known toxins
        
    Returns:
        Dictionary with similarity results
    """
    if toxin_db is None:
        toxin_db = load_toxin_database()
    
    if toxin_db.empty:
        return {
            "most_similar": None,
            "similarity": 0.0,
            "category": None,
            "toxicity_level": None,
            "all_similarities": []
        }
    
    # Generate query fingerprint
    query_fp = generate_morgan_fingerprint(query_smiles)
    if query_fp is None:
        return {
            "most_similar": None,
            "similarity": 0.0,
            "category": None,
            "toxicity_level": None,
            "error": "Invalid query SMILES"
        }
    
    # Calculate similarity with each toxin
    similarities = []
    for _, row in toxin_db.iterrows():
        toxin_fp = generate_morgan_fingerprint(row['smiles'])
        if toxin_fp is not None:
            sim = calculate_tanimoto_similarity(query_fp, toxin_fp)
            similarities.append({
                "name": row['name'],
                "smiles": row['smiles'],
                "category": row['category'],
                "toxicity_level": row['toxicity_level'],
                "similarity": round(sim, 4)
            })
    
    if not similarities:
        return {
            "most_similar": None,
            "similarity": 0.0,
            "category": None,
            "toxicity_level": None,
            "all_similarities": []
        }
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)
    
    best = similarities[0]
    
    return {
        "most_similar": best['name'],
        "similarity": best['similarity'],
        "category": best['category'],
        "toxicity_level": best['toxicity_level'],
        "all_similarities": similarities[:5]  # Top 5
    }


def compare_toxin_similarity(query_smiles: str) -> Dict:
    """
    Complete similarity analysis for a query molecule.
    
    Args:
        query_smiles: SMILES string
        
    Returns:
        Dictionary with complete similarity results
    """
    result = find_most_similar_toxin(query_smiles)
    
    # Add interpretation
    sim = result['similarity']
    if sim >= 0.7:
        result['interpretation'] = "HIGH structural similarity - potential toxicity concern"
        result['alert_level'] = "high"
    elif sim >= 0.4:
        result['interpretation'] = "MODERATE structural similarity - further investigation recommended"
        result['alert_level'] = "medium"
    else:
        result['interpretation'] = "LOW structural similarity to known toxins"
        result['alert_level'] = "low"
    
    return result


except ImportError:
    print("RDKit not available - some features disabled")