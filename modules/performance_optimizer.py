"""
Performance Optimization Module
Caching layer for fingerprints, predictions, and molecular descriptors.
Reduces prediction time to <2 seconds.
"""

import streamlit as st
import os
os.environ['RDKIT_SUPPRESS_WARNINGS'] = '1'
from rdkit import Chem
from rdkit.Chem import AllChem
from functools import lru_cache
import hashlib
import json
from typing import Dict, Optional, Any
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))


# In-memory cache for predictions
_PREDICTION_CACHE: Dict[str, Dict] = {}
_FINGERPRINT_CACHE: Dict[str, Any] = {}
_DESCRIPTOR_CACHE: Dict[str, Dict] = {}


def get_cache_key(smiles: str, model_name: str) -> str:
    """Generate unique cache key."""
    return hashlib.md5(f"{smiles}_{model_name}".encode()).hexdigest()


@st.cache_data(ttl=3600)
def cached_morgan_fingerprint(smiles: str, radius: int = 2, nbits: int = 2048):
    """
    Cached Morgan fingerprint generation.
    
    Args:
        smiles: SMILES string
        radius: Fingerprint radius
        nbits: Number of bits
        
    Returns:
        RDKit fingerprint or None
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    return AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=nbits)


@st.cache_data(ttl=3600)
def cached_molecular_descriptors(smiles: str) -> Optional[Dict]:
    """
    Cached molecular descriptor calculation.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary of descriptors or None
    """
    from rdkit.Chem import Descriptors
    
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    
    return {
        'MolWt': Descriptors.MolWt(mol),
        'LogP': Descriptors.MolLogP(mol),
        'TPSA': Descriptors.TPSA(mol),
        'NumHAcceptors': Descriptors.NumHAcceptors(mol),
        'NumHDonors': Descriptors.NumHDonors(mol),
        'NumRotatableBonds': Descriptors.NumRotatableBonds(mol),
        'NumAromaticRings': Descriptors.NumAromaticRings(mol),
        'HeavyAtomCount': Descriptors.HeavyAtomCount(mol),
        'RingCount': Descriptors.RingCount(mol),
    }


def cache_prediction(smiles: str, model_name: str, result: Dict):
    """Store prediction in cache."""
    key = get_cache_key(smiles, model_name)
    _PREDICTION_CACHE[key] = result


def get_cached_prediction(smiles: str, model_name: str) -> Optional[Dict]:
    """Retrieve cached prediction."""
    key = get_cache_key(smiles, model_name)
    return _PREDICTION_CACHE.get(key)


def clear_all_caches():
    """Clear all caches."""
    _PREDICTION_CACHE.clear()
    _FINGERPRINT_CACHE.clear()
    _DESCRIPTOR_CACHE.clear()
    st.cache_data.clear()


def profile_prediction_time(func, *args, **kwargs) -> tuple:
    """
    Profile prediction function execution time.
    
    Args:
        func: Function to profile
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Tuple of (result, execution_time_seconds)
    """
    import time
    start = time.time()
    result = func(*args, **kwargs)
    elapsed = time.time() - start
    return result, round(elapsed, 3)


def batch_predict_with_progress(smiles_list: list, predict_func, model_name: str, 
                                 progress_bar=None, status_text=None) -> list:
    """
    Batch predict with progress tracking.
    
    Args:
        smiles_list: List of SMILES strings
        predict_func: Prediction function
        model_name: Name of model for caching
        progress_bar: Streamlit progress bar
        status_text: Streamlit status text
        
    Returns:
        List of prediction results
    """
    results = []
    total = len(smiles_list)
    
    for i, smiles in enumerate(smiles_list):
        # Check cache first
        cached = get_cached_prediction(smiles, model_name)
        if cached:
            results.append(cached)
        else:
            try:
                result = predict_func(smiles)
                cache_prediction(smiles, model_name, result)
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "smiles": smiles})
        
        # Update progress
        if progress_bar:
            progress_bar.progress((i + 1) / total)
        if status_text:
            status_text.text(f"Processing {i+1}/{total}: {smiles[:30]}...")
    
    return results


def get_performance_stats() -> Dict:
    """Get cache performance statistics."""
    return {
        "prediction_cache_size": len(_PREDICTION_CACHE),
        "fingerprint_cache_size": len(_FINGERPRINT_CACHE),
        "descriptor_cache_size": len(_DESCRIPTOR_CACHE),
        "cache_hit_rate": "Enabled (Streamlit + in-memory)"
    }
