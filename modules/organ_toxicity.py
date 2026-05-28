"""
Unified Organ Toxicity Module
Runs all organ toxicity models and computes weighted safety score.
"""

import sys
import os
from typing import Dict, List

sys.path.insert(0, os.path.dirname(__file__))

from ml_model import predict_hepatotoxicity
from herg_model import predict_herg
from cardiotoxicity_model import predict_cardiotoxicity
from nephrotoxicity_model import predict_nephrotoxicity
from neurotoxicity_model import predict_neurotoxicity
from cytotoxicity_model import predict_cytotoxicity


def run_all_toxicity_tests(smiles: str) -> Dict:
    """
    Run all 6 organ toxicity models on a compound.
    
    Args:
        smiles: SMILES string
        
    Returns:
        Dictionary with all results and safety score
    """
    results = {
        "smiles": smiles,
        "models": {},
        "safety_score": 0,
        "total_tests": 6,
        "toxic_hits": 0,
        "overall_risk": "Unknown"
    }
    
    # Run all models
    models_to_run = [
        ("Liver (Hepatotoxicity)", predict_hepatotoxicity),
        ("Heart (hERG)", predict_herg),
        ("Heart (Cardiotoxicity)", predict_cardiotoxicity),
        ("Kidney (Nephrotoxicity)", predict_nephrotoxicity),
        ("Brain (Neurotoxicity)", predict_neurotoxicity),
        ("Cell (Cytotoxicity)", predict_cytotoxicity),
    ]
    
    toxic_count = 0
    total_penalty = 0
    
    for organ_name, model_func in models_to_run:
        try:
            result = model_func(smiles)
            
            if 'error' in result:
                results["models"][organ_name] = {
                    "prediction": "Error",
                    "confidence": 0,
                    "risk_level": "Unknown",
                    "is_toxic": False,
                    "penalty": 0
                }
            else:
                is_toxic = "toxic" in result.get("prediction", "").lower() or \
                          "blocker" in result.get("prediction", "").lower()
                
                risk = result.get("risk_level", "Low")
                confidence = result.get("confidence", 0)
                
                # Calculate penalty based on risk
                if risk == "High":
                    penalty = 25
                elif risk == "Medium":
                    penalty = 15
                elif risk == "Low":
                    penalty = 5
                else:
                    penalty = 0
                
                if is_toxic:
                    toxic_count += 1
                    total_penalty += penalty
                
                results["models"][organ_name] = {
                    "prediction": result.get("prediction", "N/A"),
                    "confidence": confidence,
                    "risk_level": risk,
                    "is_toxic": is_toxic,
                    "penalty": penalty
                }
        except Exception as e:
            results["models"][organ_name] = {
                "prediction": f"Error: {str(e)[:50]}",
                "confidence": 0,
                "risk_level": "Unknown",
                "is_toxic": False,
                "penalty": 0
            }
    
    # Calculate safety score
    results["toxic_hits"] = toxic_count
    results["total_penalty"] = total_penalty
    
    safety_score = max(0, 100 - total_penalty)
    results["safety_score"] = safety_score
    
    # Determine overall risk
    if toxic_count == 0:
        results["overall_risk"] = "Low Risk - All organs clear"
    elif toxic_count <= 2:
        results["overall_risk"] = "Moderate Risk - Some toxicity flags"
    elif toxic_count <= 4:
        results["overall_risk"] = "High Risk - Multiple toxicity concerns"
    else:
        results["overall_risk"] = "Critical Risk - Severe multi-organ toxicity"
    
    # Color for display
    if safety_score >= 80:
        results["safety_color"] = "#00ff66"
    elif safety_score >= 50:
        results["safety_color"] = "#ffaa00"
    else:
        results["safety_color"] = "#ff3355"
    
    return results


def get_toxicity_summary_table(results: Dict) -> List[Dict]:
    """
    Generate a compact summary table for display.
    
    Args:
        results: Results from run_all_toxicity_tests
        
    Returns:
        List of dictionaries for table display
    """
    summary = []
    
    for organ_name, data in results.get("models", {}).items():
        pred = data.get("prediction", "N/A")
        risk = data.get("risk_level", "Unknown")
        is_toxic = data.get("is_toxic", False)
        
        # Emoji indicator
        if risk == "High":
            indicator = "🔴"
        elif risk == "Medium":
            indicator = "🟡"
        elif risk == "Low":
            indicator = "🟢"
        else:
            indicator = "⚪"
        
        summary.append({
            "Organ": organ_name,
            "Prediction": pred,
            "Risk": f"{indicator} {risk}",
            "Toxic": "YES" if is_toxic else "NO",
            "Confidence": f"{data.get('confidence', 0)}%"
        })
    
    return summary
