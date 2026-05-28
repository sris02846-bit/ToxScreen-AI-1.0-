"""
Centralized Model Loader Module
Cached loading for all toxicity prediction models.
Prevents redundant model loading across modules.
"""

import joblib
import os
from typing import Dict, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Global model cache
_MODEL_CACHE: Dict[str, Any] = {}


def get_models_dir() -> str:
    """Get the models directory path."""
    return os.path.join(os.path.dirname(__file__), '..', 'models')


def load_model(model_name: str) -> Optional[Any]:
    """
    Load a model from disk with caching.
    
    Args:
        model_name: Name of the model file (without .pkl)
        
    Returns:
        Loaded model or None if not found
    """
    # Check cache first
    if model_name in _MODEL_CACHE:
        return _MODEL_CACHE[model_name]
    
    model_path = os.path.join(get_models_dir(), f"{model_name}.pkl")
    
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            _MODEL_CACHE[model_name] = model
            return model
        except Exception as e:
            print(f"Error loading {model_name}: {e}")
            return None
    
    return None


def save_model(model: Any, model_name: str):
    """
    Save a model to disk and update cache.
    
    Args:
        model: Trained model object
        model_name: Name for the model file
    """
    models_dir = get_models_dir()
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, f"{model_name}.pkl")
    joblib.dump(model, model_path)
    _MODEL_CACHE[model_name] = model
    print(f"Model saved: {model_name}.pkl")


def clear_cache():
    """Clear the model cache to free memory."""
    _MODEL_CACHE.clear()


def get_cached_models() -> list:
    """Get list of currently cached model names."""
    return list(_MODEL_CACHE.keys())


def preload_all_models() -> Dict[str, bool]:
    """
    Preload all available toxicity models.
    
    Returns:
        Dictionary with model names and load status
    """
    model_names = [
        "hepatotoxicity_model",
        "herg_model",
        "cardiotoxicity_model",
        "nephrotoxicity_model",
        "neurotoxicity_model",
        "cytotoxicity_model"
    ]
    
    results = {}
    for name in model_names:
        model = load_model(name)
        results[name] = model is not None
    
    return results


def get_model_info() -> Dict:
    """
    Get information about all available models.
    
    Returns:
        Dictionary with model info
    """
    models_dir = get_models_dir()
    info = {}
    
    model_descriptions = {
        "hepatotoxicity_model": "Liver Toxicity (Tox21 SR-HSE)",
        "herg_model": "hERG Channel Cardiotoxicity",
        "cardiotoxicity_model": "General Cardiotoxicity (XGBoost)",
        "nephrotoxicity_model": "Kidney Toxicity (DrugBank/TDC)",
        "neurotoxicity_model": "Neurotoxicity (ChEMBL/PubChem)",
        "cytotoxicity_model": "Cytotoxicity (Tox21 SR-MMP)"
    }
    
    for model_name, description in model_descriptions.items():
        model_path = os.path.join(models_dir, f"{model_name}.pkl")
        info[model_name] = {
            "description": description,
            "exists": os.path.exists(model_path),
            "cached": model_name in _MODEL_CACHE
        }
    
    return info
